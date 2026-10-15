# Changelog

## 1.0.1 - Unreleased

- Exclude `.env.*` files in the root and nested directories before reading content, including when explicitly included.
- Add no-read regression guards and preserve token estimation for ordinary files.

## 1.0.0 - 2026-07-26

- Added include and exclusion previews with conservative default exclusions.
- Added transparent token estimates, budgets, and truncation-risk labels.
- Added binary, encoding, size, and symlink safety boundaries.
