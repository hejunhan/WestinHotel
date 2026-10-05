# WestinHotel

简体中文 | [English](README.en.md)

WestinHotel 是一个多人合作开发的 Unreal Engine 项目。本仓库收录当前以
`DSH_Standalone` 形式交付的独立工程部分，供团队继续开发；它是整个项目的一部分。

工程文件名和已有资源路径沿用原始交付版本，以保持资源引用有效。
打开 **`DSH_Standalone.uproject`** 即可进入本仓库中的 WestinHotel 工程。

## 环境要求

- **Unreal Engine 5.8.2**：与原始交付说明要求的版本一致。工程描述文件关联 UE 5.8。
- **Git 和 Git LFS**：每位协作者都需要安装。
- 能够运行本工程现有 DX12、Lumen、Nanite、光线追踪及高分辨率贴图设置的 Windows 电脑。
- 工程所需的引擎内置插件见 `DSH_Standalone.uproject`，具体引擎文件要求见
  `Docs/EngineRequirements.json`。

原始交付说明记录了工程无需额外的项目插件。UE 引擎本身需要单独安装。

## 下载与打开

安装 Git 和 Git LFS 后，在 PowerShell 中执行：

```powershell
git lfs install
git clone https://github.com/hejunhan/WestinHotel.git
cd WestinHotel
git lfs pull
git lfs fsck
Start-Process .\DSH_Standalone.uproject
```

请在克隆前初始化 Git LFS。Unreal 资源在 Git 中保存为 LFS 指针，必须下载实际资源后
才能正常打开工程。首次资源下载量约 **2.2 GiB**，请预留下载时间，以及资源和 UE
本地缓存所需的磁盘空间。建议使用上面的命令获取可编辑工程。

首次打开时需要等待着色器编译和资源处理。默认编辑器启动地图和游戏地图均为
**`Main_World2_MonitorArchitectural`**。加载完成后，点击 **Play** 运行。

## 当前工程内容

当前交付版本包含建筑主关卡、监控室、三屏监控、四个交互机关、电梯及当前第三人称角色。
已有 Unreal 资源名称和路径，包括中文名称，均沿用原工程。

| 路径 | 用途 |
| --- | --- |
| `DSH_Standalone.uproject` | 工程描述文件及显式插件依赖 |
| `Content/` | Unreal 资源、蓝图、材质、贴图及地图 |
| `Config/` | 共享工程设置、渲染设置和输入设置 |
| `Docs/` | 原始引擎依赖要求及交付检查报告 |
| `Tools/Verify-And-Launch.ps1` | 原始交付文件完整性及引擎依赖检查工具 |
| `Check-And-Launch.cmd` | 原始交付检查工具的启动入口 |
| `MANIFEST_SHA256.csv` | 原始交付文件的校验值清单 |
| `CONTRIBUTING.md` | 英文团队协作指南 |

`Binaries/`、`DerivedDataCache/`、`Intermediate/`、`Saved/` 等生成目录由 Git 忽略，
需要时由本机重新生成。

原始 FBX 和贴图制作源文件未包含在本次交付部分中；工程使用的 Unreal 资源数据位于
`Content/` 中。

## 团队协作

公开仓库允许任何人克隆。需要直接向本仓库推送分支的组员，应由仓库拥有者添加为
协作者；其他贡献者可通过 Fork 和 Pull Request 提交修改。

建议在工作区干净、已有修改已保存或提交的情况下，从最新的 `main` 创建功能分支：

```powershell
git switch main
git pull --ff-only
git lfs pull
git switch -c feature/describe-your-change
```

请把示例分支名替换为本次工作的名称，并遵循以下约定：

- 编辑同一地图、蓝图或其他二进制资源前，先与组员协调，减少同时修改造成的冲突。
- 在 Unreal 中保存修改后的资源，再使用 `git status` 和 `git lfs status` 检查待提交内容。
- 使用 Unreal 的 Content Browser 移动或重命名资源，并一起提交相关引用更新。
- 新资源及其依赖应与引用它们的地图或蓝图一起提交。
- 保留 `.gitattributes` 中的 LFS 规则；缓存、日志、打包产物和本地凭据应留在本机。
- 推送功能分支后，向 `main` 发起 Pull Request，说明修改内容、受影响资源和验证结果。

完整分支、提交及故障排查步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 交付记录与验证范围

`Docs/` 下的报告、原始中文交付说明和校验清单作为历史交付记录保留。它们记录了此前
的资源加载、蓝图编译、地图加载和无图形界面的 Play 检查。
**本次上传 GitHub 未重新执行这些 UE 编辑器检查**；原报告也注明未验证 GPU 画面和
实体键盘操作。

原始检查工具适用于未修改的交付版本。当前上传的工作副本中，
`BP_FlipPanelControl.uasset` 已与原始校验清单不同，仓库保留了它的当前本地版本。
因此，即使刚克隆本仓库，原始校验工具也会报告该文件不匹配。
日常开发请直接打开 `.uproject`；后续团队修改同样会与原始校验值不同。
为 GitHub 添加的仓库配置和说明文件未包含在原始校验清单中。

本仓库公开用于合作开发。本次仓库整理未新增授权许可；项目及第三方资源已有的使用
条款继续适用。
