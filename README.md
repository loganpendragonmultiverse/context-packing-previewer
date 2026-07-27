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

## Security boundary

This is a read-only preview, not a secret scanner or an AI client. Review the final file list yourself. Symlinks are skipped, and no file contents appear in the report, but filenames and absolute root paths can still be sensitive.

Requires Python 3.10 or newer. Development checks use Ruff, pytest with branch coverage, and package builds.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).
