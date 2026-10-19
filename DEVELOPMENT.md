# Development

Keep this a local, bounded tool for its README purpose. Do not add network lookup,
telemetry, implicit source modification or unrelated catalog work. Preserve the
documented legacy report shapes and interpretation limits.

Run the exact checks in TESTING.md. Changes go through a branch and protected pull
request with the existing cross-platform CI and CodeQL checks. Review the final
diff and actual installed distributions before publishing an annotated version tag.
Use that tag workflow's wheel and source distribution, verify asset SHA-256
digests, then reconcile the Forge catalog, Gold scope, source-backed information
page and canonical portfolio record. No release is complete after a push alone.

## This patch

- Reject escaping include patterns and skip symlinked path components before content reads.
- Validate integer budgets, preserve literal Markdown paths, protect report destinations and handle closed output pipes cleanly.

Require independent review before release. Dotenv exclusions must precede reads even with explicit include globs. Preserve the no-read regression guards.
