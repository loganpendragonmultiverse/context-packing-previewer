# Development handoff

1.0.1 is the reviewed privacy fix. Dotenv exclusions must happen before content reads, even for explicit include patterns. Keep templates excluded conservatively and retain ordinary-file token estimation. Run Ruff formatting/lint, the coverage-gated pytest suite, and package builds. The regression tests intercept Path.read_bytes and fail on any dotenv read. Require protected CI and independent review before release.
