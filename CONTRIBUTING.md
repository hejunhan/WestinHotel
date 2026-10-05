# Contributing to WestinHotel

WestinHotel is a collaborative Unreal Engine project. Use the same engine
version, **UE 5.8.2**, and install **Git LFS** before cloning or editing assets.

## Getting access

The public repository can be cloned by anyone. Contributors who need to push
branches to this repository must be added as collaborators by its owner.
Other contributors can work in a fork and open a pull request.

## Start a change

Start from an updated `main` branch with a clean working tree:

```powershell
git switch main
git pull --ff-only
git lfs pull
git switch -c feature/describe-your-change
```

Save or commit existing work before switching branches. Open
`DSH_Standalone.uproject` and use the configured startup map.

## Work with Unreal assets

- Save the modified assets in Unreal before committing.
- Coordinate ownership of maps and Blueprints before editing them in parallel.
  These files are binary and generally need to be resolved in Unreal when
  changes overlap.
- Keep existing asset references valid. Use Unreal's Content Browser to move
  or rename assets, and include the resulting reference updates.
- Include new assets and their dependencies in the same pull request.
- Keep generated caches, logs, packaged builds, and local credentials out of
  commits. The repository's `.gitignore` excludes the current generated folders.
- Keep Unreal assets under Git LFS. Do not remove their tracking rules from
  `.gitattributes`.

## Commit and open a pull request

Review the change before staging it:

```powershell
git status --short
git diff
git lfs status
git add <changed-files-or-folders>
git diff --cached --stat
git commit -m "Describe the project change"
git push -u origin feature/describe-your-change
```

Replace the placeholder paths and branch name with your actual change. Open a
pull request against `main` describing what changed, which maps or assets it
affects, and what you tested. Check the editor's compile messages and use Play
to exercise the behavior your change affects. Record any checks you could not
perform.

After a pull request is merged, update `main` with `git pull --ff-only` and
`git lfs pull` before starting the next change.

## Troubleshooting missing assets

If the editor cannot load assets after cloning or updating, close the editor
and run:

```powershell
git lfs install
git lfs pull
git lfs fsck
```

Check the Git LFS output for download or authentication errors. An LFS pointer
is a small text reference, not a usable Unreal asset. Do not open the project
until the resource download completes.

## Original delivery checksums

`MANIFEST_SHA256.csv` records the original delivered snapshot. It is not a
manifest of subsequent team changes. Keep the original reports available as
historical evidence and document new verification results in pull requests.
