<!-- markdownlint-disable MD033 MD041 -->
<div align="center">

<img alt="LOGO" src="resource/base/image/logo.png" width="256" height="256" />

# MBCCtools — CN Daily Branch

A Path to Nowhere assistant based on [MaaFramework](https://github.com/MaaXYZ/MaaFramework). Image recognition + emulator control.

</div>

> This repository is a fork of [quietlysnow/MBCCtools](https://github.com/quietlysnow/MBCCtools), focused on the official (CN) server, the Nightingale assistant daily flow, and login recovery. Bilibili and global servers are kept loadable but are not live-tested here.

## Download

- Get `MBCCtools-win-x86_64-*.zip` from [Releases](https://github.com/murongshan/MBCCtools/releases).
- Unzip and run `MFAAvalonia.exe`; choose the **official (官服)** resource.
- MuMu Player at 1280×720 or 1600×900 is recommended; screenshots are normalized to 1280×720.
- Run **进入游戏** first, then **助手待办（官服试验）**. The latter opens the Nightingale assistant and handles the adapted priority items in order.
- Stamina is preserved by default. Select **按配置清理体力** to spend current stamina with the configured stage; the tool does not buy stamina or use cubes.

Install the [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) and [.NET 10.0](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) if Windows reports missing runtimes.

## Features

- Nightingale assistant daily: stamina supply, supervisor resources/events, memory storm, dispatch, guild donation, dark zone, free daily pack, friend points, supervisor daily activity.
- Login recovery: ads/notices, mood test, reserve-stamina popup, director birthday gift/letter, unknown popups, home and assistant confirmation.
- Existing tasks: guild donation, friend points, supervisor rewards, free packs, dispatch, stamina claim, mail, dark zone, memory storm, daily stamina, battle pass, broken frontline, gacha records.
- Gacha records export to md/xlsx under `record/抽卡记录/`.

## Known limitations

- Only Windows x64 + MuMu + official CN server is live-tested. Bilibili/global servers and macOS are not.
- The reserve-stamina popup was hit once in a manual run on 2026-11-12 and is still awaiting live confirmation; the daily queue did not hit it from 2026-11-13 to 11-17.
- The guild-exchange task stays in the pipeline but is not exposed in the GUI yet; the activity-hall draft is not enabled.
- No MirrorChyan channel for this fork; upgrade from this repository's Releases.

## Development

See [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/开发状态.md](docs/开发状态.md). Pipelines are JSON; custom logic lives in `agent/`. The release package bundles its own Python runtime.

## Credits and license

Based on [quietlysnow/MBCCtools](https://github.com/quietlysnow/MBCCtools), which in turn references [MACC](https://github.com/mxia9416/MACC). Powered by MaaFramework. Licensed under the [MIT License](LICENSE).
