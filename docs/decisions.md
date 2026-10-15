# Decisions

Format: **Decision** / **Why** / **Alternatives considered**.

## 001 - Layout: `app/` at the repo root
- **Why:** matches the architecture in CLAUDE.md; this is an application, not a distributable library.
- **Alternatives:** `src/support_pilot/` (uv package default).
