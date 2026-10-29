"""只读检查 Pipeline/引用/模板并真实加载三服；结果仅写 .scratch/resource-check，不连接设备。"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
repository = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--resource-root", type=Path, default=repository / "resource")
parser.add_argument("--interface", type=Path, default=repository / "interface.json")
parser.add_argument("--native-library-root", type=Path, help="可选：GUI 使用的原生库目录；省略时使用已安装 MaaFw 自带的库")
args = parser.parse_args()
resource_root = args.resource_root.resolve()
interface_path = args.interface.resolve()
check_root = repository / ".scratch/resource-check"
check_root.mkdir(parents=True, exist_ok=True)
if args.native_library_root:
    os.environ["MAAFW_BINARY_PATH"] = str(args.native_library_root.resolve())
else:
    os.environ.pop("MAAFW_BINARY_PATH", None)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

from maa.library import Library
from maa.resource import Resource
from maa.tasker import Tasker, LoggingLevelEnum

Tasker.set_log_dir(check_root / "debug")
Tasker.set_stdout_level(LoggingLevelEnum.Error)

BUNDLES = ("base", "bilibili", "global")
errors = []


def file_manifest(paths, relative_to):
    """哈希包含文件路径、长度和每文件 SHA256，避免简单拼接的边界歧义。"""
    digest = hashlib.sha256()
    size = 0
    paths = sorted(paths, key=lambda p: p.relative_to(relative_to).as_posix())
    for path in paths:
        data = path.read_bytes()
        size += len(data)
        entry = [path.relative_to(relative_to).as_posix(), len(data), hashlib.sha256(data).hexdigest()]
        digest.update(json.dumps(entry, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
    return {"sha256": digest.hexdigest(), "file_count": len(paths), "byte_count": size}


def resource_files():
    return [p for b in BUNDLES for p in (resource_root / b).rglob("*") if p.is_file()]


def refs(value):
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    result = []
    for item in items:
        if isinstance(item, dict):
            if item.get("anchor"):
                continue
            name = item.get("name", "")
        else:
            name = item
        if not isinstance(name, str):
            errors.append({"kind": "invalid_reference", "value": item})
            continue
        if name.startswith("[Anchor]"):
            continue
        result.append(re.sub(r"^(?:\[JumpBack\])+", "", name))
    return result


def template_names(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("template", "templates"):
                for item in child if isinstance(child, list) else [child]:
                    if isinstance(item, str):
                        yield item
            else:
                yield from template_names(child)
    elif isinstance(value, list):
        for child in value:
            yield from template_names(child)


def override_blocks(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "pipeline_override" and isinstance(child, dict):
                yield child
            else:
                yield from override_blocks(child)
    elif isinstance(value, list):
        for child in value:
            yield from override_blocks(child)


def check_node(label, name, fields, names, image_roots):
    count_refs = count_templates = 0
    for field in ("next", "on_error"):
        for ref in refs(fields.get(field)):
            count_refs += 1
            if ref not in names:
                errors.append({"server": label, "node": name, "field": field, "missing_node": ref})
    # 此仓库的字符串坐标支持引用既有节点；锚点动态引用不作静态断言。
    for section in (fields.get("recognition", {}), fields.get("action", {})):
        param = section.get("param", {}) if isinstance(section, dict) else {}
        for field in ("target", "roi", "begin", "end"):
            ref = param.get(field)
            if isinstance(ref, str) and not ref.startswith("[Anchor]"):
                count_refs += 1
                if ref not in names:
                    errors.append({"server": label, "node": name, "field": field, "missing_node": ref})
    for template in template_names(fields):
        count_templates += 1
        if not any((p / template).is_file() for p in image_roots):
            errors.append({"server": label, "node": name, "missing_template": template})
    return count_refs, count_templates


snapshot_before = file_manifest(resource_files(), resource_root)
raw_bundles = {}
bundle_info = {}
pipeline_paths = []
for bundle in BUNDLES:
    paths = sorted((resource_root / bundle / "pipeline").rglob("*.json"))
    pipeline_paths.extend(paths)
    nodes = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for name, fields in payload.items():
            if name.startswith("$"):
                continue
            if name in nodes:
                errors.append({"bundle": bundle, "duplicate_node": name})
            nodes[name] = fields
    raw_bundles[bundle] = nodes
    bundle_info[bundle] = {"pipeline_files": len(paths), "defined_nodes": len(nodes)}

interface = json.loads(interface_path.read_text(encoding="utf-8"))
all_overrides = list(override_blocks(interface))
results = []
for label, bundles in (("官服", ("base",)), ("B服", ("base", "bilibili")), ("国际服", ("base", "global"))):
    merged = {}
    for bundle in bundles:
        for name, fields in raw_bundles[bundle].items():
            merged.setdefault(name, {}).update(fields)
    ref_count = template_count = 0
    images = [resource_root / b / "image" for b in bundles]
    for name, fields in merged.items():
        rc, tc = check_node(label, name, fields, merged, images)
        ref_count += rc
        template_count += tc
    for task in interface.get("task", []):
        if task["entry"] not in merged:
            errors.append({"server": label, "task": task.get("name"), "missing_entry": task["entry"]})
    for override in all_overrides:
        for name, fields in override.items():
            if name not in merged:
                errors.append({"server": label, "missing_override_node": name})
            rc, tc = check_node(label, name, fields, merged, images)
            ref_count += rc
            template_count += tc
    resource = Resource()
    loaded = []
    for bundle in bundles:
        ok = resource.post_bundle(resource_root / bundle).wait().succeeded
        loaded.append({"bundle": bundle, "succeeded": ok})
        if not ok:
            errors.append({"server": label, "bundle_load_failed": bundle})
    native_names = set(resource.node_list)
    if native_names != set(merged):
        errors.append({"server": label, "native_node_set_diff": {"missing": sorted(set(merged)-native_names), "extra": sorted(native_names-set(merged))}})
    results.append({"server": label, "bundles": loaded, "pipeline_files": sum(bundle_info[b]["pipeline_files"] for b in bundles),
                    "merged_nodes": len(merged), "native_nodes": len(native_names), "task_entries": len(interface.get("task", [])),
                    "references_checked": ref_count, "template_references_checked": template_count})

snapshot_after = file_manifest(resource_files(), resource_root)
if snapshot_before != snapshot_after:
    errors.append({"kind": "resource_changed_during_check", "before": snapshot_before, "after": snapshot_after})
base_paths = sorted((resource_root / "base/pipeline").glob("*.json"))
result = {"checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(), "resource_root": str(resource_root),
          "framework_version": Library.version(), "framework_source": str(Library.framework_libpath),
          "json_pipeline_files": len(pipeline_paths), "bundles": bundle_info, "servers": results,
          "resource_manifest": snapshot_after, "pipeline_manifest": file_manifest(pipeline_paths, resource_root),
          "base_pipeline_concat_sha256": hashlib.sha256(b"".join(p.read_bytes() for p in base_paths)).hexdigest(),
          "interface_sha256": hashlib.sha256(interface_path.read_bytes()).hexdigest(),
          "source_snapshot_stable": snapshot_before == snapshot_after,
          "game_tasks_executed": False, "errors": errors, "passed": not errors,
          "limitations": ["不验证游戏画面、OCR准确率、坐标与阈值。", "不判定业务结果或GUI队列行为。", "不静态求解动态Anchor；option覆盖只检查节点及引用，不执行每种选项组合。", "resource/default_pipeline.json位于bundle父目录，未因此移位或改变全局节奏。"]}
destination = check_root / "检查结果.json"
destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result["passed"] else 1)
