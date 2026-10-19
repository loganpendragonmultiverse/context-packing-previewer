# Context Packing Previewer

[![CI](https://github.com/loganpendragonmultiverse/context-packing-previewer/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/context-packing-previewer/actions/workflows/ci.yml)

Context Packing Previewer shows which local files would enter an AI coding context, estimates their token footprint, records exclusions, and warns when a chosen budget is close or exceeded. Nothing is uploaded.

## Three-minute start

```bash
python -m pip install .
context-preview . --include "src/**/*.py" --include "tests/**/*.py" --budget 32000
context-preview . --exclude "fixtures/**" --format json
```

The estimate deliberately uses a transparent four-characters-per-token approximation rather than claiming tokenizer-exact billing. Reports identify binary, non-UTF-8, oversized, and excluded files. Default exclusions cover common build directories, repositories, virtual environments, environment files, and private-key extensions.

Version 1.0.1 excludes `.env`, files ending in `.env`, and `.env.*` variants (including example templates) in root and nested directories before reading their contents. Explicit `--include` patterns do not override default exclusions. This is a filename convention, not a guarantee that every secret-bearing file is excluded.

## Security boundary

This is a read-only preview, not a secret scanner or an AI client. Review the final file list yourself. Symlinks are skipped, and no file contents appear in the report, but filenames and absolute root paths can still be sensitive.

Requires Python 3.10 or newer. Development checks use Ruff, pytest with branch coverage, and package builds.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Report and release behavior

Install the wheel from the GitHub release with python -m pip install ./PACKAGE.whl,
using the actual downloaded filename. The source distribution can also be installed
with pip. The wheel includes these handoff documents and supplied examples under
share/context-packing-previewer/ in the installation prefix. A repository checkout is the easiest
way to run the README examples as written.

Invalid inputs or failed output writes return exit status 2. A successful command
returns 0. Report files must be new: existing files, directories and symlinks are
refused. Keep reports outside scanned folders to avoid counting prior reports.
A failed write may leave a partial newly created report; no power-loss transaction
is promised. Closed stdout pipes return 2. Filenames, story data and paths in
reports can be sensitive; review before sharing.

Include patterns are Python pathlib globs relative to the chosen root. Absolute
patterns and parent-directory components are rejected; symlink roots and symlinked
descendant paths are skipped or refused. Selected files are listed in path order;
budgets classify the total estimate and do not silently drop files or choose an
optimal pack. This is an observation, not a filesystem snapshot or an adversarial
sandbox. Concurrent filesystem changes and inaccessible directories can interrupt
or limit traversal; inspect the supplied scope rather than treating omission as
proof that a file does not exist.
