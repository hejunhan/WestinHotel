# WestinHotel

English | [简体中文](README.zh-CN.md)

WestinHotel is a collaborative Unreal Engine project. This repository contains
the current standalone project component supplied as `DSH_Standalone`; it is a
starting point for the team's ongoing work, rather than the complete scope of
the larger project.

The Unreal project filename and existing asset paths are retained so their
references continue to work. Open **`DSH_Standalone.uproject`** to work on
WestinHotel.

## Requirements

- **Unreal Engine 5.8.2**, matching the version specified by the supplied delivery
  documentation. The project descriptor associates the project with UE 5.8.
- **Git** and **Git LFS** on every contributor's machine.
- A Windows PC with graphics hardware suitable for the project's existing
  DX12, Lumen, Nanite, ray tracing, and high-resolution texture settings.
- The engine-provided plugins listed in `DSH_Standalone.uproject` and the
  engine files recorded in `Docs/EngineRequirements.json`.

The original package documentation reports no additional project plugins.
The Unreal Engine installation itself is not included in this repository.

## Clone and open

```powershell
git lfs install
git clone https://github.com/hejunhan/WestinHotel.git
cd WestinHotel
git lfs pull
git lfs fsck
Start-Process .\DSH_Standalone.uproject
```

Install Git LFS before cloning. The Unreal assets use LFS pointers in Git; the
actual assets must be downloaded before opening the editor. The initial asset
payload is approximately **2.2 GiB**, so allow time and disk space for the
download and Unreal's generated caches. Use the commands above to obtain a
working project.

On first launch, wait for shader compilation and resource processing. The
configured startup and game map is **`Main_World2_MonitorArchitectural`**.
After the editor finishes loading, press **Play**.

## Current component

The supplied snapshot includes the architectural main level, a monitoring room
with three screens, four interactive mechanisms, elevators, and the current
third-person character. Unreal asset names and paths, including Chinese names,
are preserved from the delivered project.

| Path | Purpose |
| --- | --- |
| `DSH_Standalone.uproject` | Project descriptor and explicit plugin dependencies |
| `Content/` | Unreal assets, Blueprints, materials, textures, and maps |
| `Config/` | Shared project, rendering, and input settings |
| `Docs/` | Original dependency requirements and delivery audit reports |
| `Tools/Verify-And-Launch.ps1` | Original delivery integrity and engine preflight tool |
| `Check-And-Launch.cmd` | Launcher for the original delivery preflight workflow |
| `MANIFEST_SHA256.csv` | Checksums of the original delivered files |
| `CONTRIBUTING.md` | Team setup and collaboration workflow |

Generated `Binaries/`, `DerivedDataCache/`, `Intermediate/`, and `Saved/` files
are excluded from Git. They are recreated locally as needed. Original FBX and
texture authoring files are not included in the supplied component; the
packaged Unreal assets are present in `Content/`.

## Team workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch and pull request workflow.
Coordinate edits to the same Blueprint, map, or other binary Unreal asset.
Check `git lfs status` before committing resource changes and include the
required assets in the same change as their referencing map or Blueprint.

## Delivery reports and verification scope

The existing files under `Docs/`, the Chinese delivery notes, and the checksum
manifest are retained as records of the supplied snapshot. They describe
earlier asset loading, Blueprint compilation, map loading, and headless Play
checks. Those editor checks were **not rerun as part of publishing this
repository**; the supplied reports also state that GPU rendering and physical
keyboard behavior were not verified.

The original preflight tool is intended for an unchanged delivery snapshot.
The working copy uploaded here already differs from that original manifest in
`BP_FlipPanelControl.uasset`; its current local version is preserved. The
original checksum checker will therefore report a mismatch even after a fresh
clone. Open the `.uproject` normally for ongoing development. Further team
edits will also differ from the original checksums. Repository setup files
added for GitHub are not part of the original checksum manifest.

This repository is public for collaboration. No new license grant is added by
this repository setup; existing project and third-party asset terms continue
to apply.
