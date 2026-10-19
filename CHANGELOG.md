# Changelog

## 1.0.2 - 2026-10-19

- Reject escaping include patterns and skip symlinked path components before content reads.
- Validate integer budgets, preserve literal Markdown paths, protect report destinations and handle closed output pipes cleanly.

## 1.0.1 - 2026-10-15

- Exclude `.env.*` files in the root and nested directories before reading content, including when explicitly included.
- Add no-read regression guards and preserve token estimation for ordinary files.

## 1.0.0 - 2026-07-26

- Added include and exclusion previews with conservative default exclusions.
- Added transparent token estimates, budgets, and truncation-risk labels.
- Added binary, encoding, size, and symlink safety boundaries.
