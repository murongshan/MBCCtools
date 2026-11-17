<!-- markdownlint-disable MD033 MD041 -->
<div align="center">

<img alt="LOGO" src="resource/base/image/logo.png" width="256" height="256" />

# MBCCtools 官服日常版

基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 的《无期迷途》小助手。图像识别 + 模拟控制，解放双手。

</div>

> 本仓库是 [quietlysnow/MBCCtools](https://github.com/quietlysnow/MBCCtools) 的官服分支，重点维护「夜莺助手日常」、登录恢复与日常稳定性。B 服 / 国际服仅保留结构兼容，未做同等实机验证。

## 下载与使用

- 到 [Releases](https://github.com/murongshan/MBCCtools/releases) 下载 `MBCCtools-win-x86_64-*.zip`。
- 解压后运行 `MFAAvalonia.exe`，连接模拟器，资源选择 **官服**。
- 推荐 MuMu 模拟器、1280×720 或 1600×900；框架会把截图归一到 1280×720。
- 日常流程：先运行「进入游戏」，再运行「助手待办（官服试验）」。后者会从主页打开夜莺助手，按顺序处理已适配的优先事项。
- 默认**保留体力**；需要清体力时在任务选项里选择「按配置清理体力」，使用下方作战区域与材料配置，不购买体力、不使用异方晶。

Windows 若提示缺少运行库，请安装 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) 与 [.NET 10.0](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)。

## 已实现功能

- **夜莺助手日常**：体力专属补给、监管生产物资、监管事件、记忆风暴、派遣、秘盟捐赠、浊暗之阱、每日免费补给、友情点、监察每日活跃十项。
- **登录恢复**：广告与公告关闭、情绪检测、储备体力弹窗、局长生日礼物/贺信、未知弹窗兜底、主页与助手面板确认。
- **助手快捷浮层**：识别「前往」浮层后直达对应业务页面；监察奖励延后到体力处理后。
- **日常任务**：秘盟捐赠、好友点数、监管奖励、采购办免费礼包、一键派遣、领取体力、邮箱领取、浊暗之阱、记忆风暴、每日体力用途、每日/密令奖励、破碎防线。
- **抽卡记录**：自动翻页采集卡池与稀有度，输出 md / xlsx 到 `record/抽卡记录/`。
- **活动提醒**：启动时后台采集 BWIKI 活动，写入 `record/活动.json`，供 GUI 页面读取。

## 已知限制

- 目前只在 Windows x64 + MuMu + 官服上做实机验证；B 服、国际服与 macOS 未做同等业务验证。
- 2026-11-12 的手工回归曾在「使用储备体力」弹窗上失败；2026-11-13 至 11-17 的日常队列未再遇到，但该弹窗的处理仍待实机确认。
- 「秘盟兑换」任务的 Pipeline 保留在仓库中，但 GUI 任务列表暂未开放；「活动大厅领奖」仍是未启用草稿。
- 本 fork 不提供 MirrorChyan 更新通道，升级请从本仓库 Releases 覆盖安装。

## 开发

- 开发约定与 Pipeline 写法见 [AGENTS.md](AGENTS.md)。
- 环境、离线识别工具与提交前自检见 [CONTRIBUTING.md](CONTRIBUTING.md)。
- 当前验证范围和未完成项见 [docs/开发状态.md](docs/开发状态.md)。
- 本项目以 JSON Pipeline 为主，复杂逻辑放在 `agent/` 的 Python Agent 中；发布包自带解释器，用户无需安装 Python。

## 致谢与许可证

本项目基于 [quietlysnow/MBCCtools](https://github.com/quietlysnow/MBCCtools) 继续开发，上游又基于 [MACC](https://github.com/mxia9416/MACC) 的设计思路重写。感谢 MaaFramework 与所有上游贡献者。

以 [MIT License](LICENSE) 发布。
