# Changelog

All notable changes to the PersonaPad backend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-05-10

### Added

- Persona data under `backend/app/data/**` is now encrypted at rest in the
  repo via [`git-crypt`](https://github.com/AGWA/git-crypt). `profile.md` and
  `persona.json` are stored as encrypted blobs on GitHub and decrypted to
  plaintext in working copies that have run `git-crypt unlock`. The on-disk
  paths and `_load_style_profile` / `_load_examples` are unchanged, so
  `persona_engine` does not need to know about the encryption.
- `backend/Dockerfile` (Python 3.11-slim base) installs `git-crypt`, copies
  the repo, and installs `requirements.txt`. Build context is the repo root
  so `.git` and the top-level `.gitattributes` are available for unlock.
- `backend/docker-entrypoint.sh` runs at container start, base64-decodes
  `GIT_CRYPT_KEY_B64` into a temp file, calls `git-crypt unlock`, scrubs the
  key file, then `exec`s `uvicorn`. Skips the unlock if the repo is already
  unlocked (defensive, for restarts inside the same writable layer).
- `.dockerignore` at the repo root, scoped to keep `.git` (required for
  unlock) while trimming `frontend/`, caches, and local-only env files out
  of the build context.

### Changed

- `.gitattributes` adds `backend/app/data/** filter=git-crypt diff=git-crypt`,
  scoping encryption to persona content only. Code, configs, tests, and the
  rest of the repo stay diffable in plaintext.
- `render.yaml` switched from `runtime: python` to `runtime: docker` with
  `dockerfilePath: ./backend/Dockerfile` and `dockerContext: .`. Render's
  managed Python runtime can't `apt-get install git-crypt`, so a Dockerfile
  is the only path that lets git-crypt unlock the persona files at boot.
  `buildCommand`, `startCommand`, and `PYTHON_VERSION` were removed (now
  controlled by the Dockerfile). New required env var `GIT_CRYPT_KEY_B64`
  set via the Render dashboard with `sync: false`.

## [0.3.0] - 2026-05-08

### Added

- Global `Exception` handler in `app/main.py` so any unhandled error returns a
  JSON 500 from inside the user middleware chain. Without this, exceptions
  escape to Starlette's outermost `ServerErrorMiddleware` (sits outside
  `CORSMiddleware`), producing a bare `text/plain` 500 with no
  `Access-Control-Allow-Origin` header. The browser then surfaces it as a
  CORS error and the real cause is hidden in the server log.

### Changed

- `requirements.txt` now includes `numpy>=2.0,<3` so production deploys (which
  install via pip, not Poetry) match the `pyproject.toml` constraint and
  `example_selector` can import.

### Fixed

- Exception catches in `persona_engine.generate_response` and
  `example_selector.select_examples` broadened from `APIError` to
  `OpenAIError` (the SDK base class). This covers the missing-API-key case,
  where `OpenAI()` raises `OpenAIError` directly, plus any other
  non-`APIError` SDK errors. Previously these escaped the catch and produced
  a CORS-shaped 500 in the browser; now they surface as a clean 502 with a
  `LLM provider error` / `embedding ...` detail and proper CORS headers.

## [0.2.0] - 2026-05-07

### Added

- `app/services/example_selector.py` with semantic top-k few-shot picking via
  OpenAI text embeddings, lazy per-persona embedding cache, and cosine ranking.
- `numpy` dependency for vector math.

### Changed

- `persona_engine._build_messages` now calls `select_examples(...)` instead of
  slicing the first N few-shot examples, so the prompt carries the most
  relevant ones for the current question.
- Few-shot examples are ordered "most relevant last" so the strongest signal
  sits closest to the user's message.
- Mode prompts and the `van_keith` persona profile/examples tightened for
  better voice fidelity.

### Fixed

- Graceful fallback to the first-k examples when the embedding API call fails,
  so a transient embedding outage never breaks `/api/generate`.

## [0.1.0] - 2026-04

### Added

- FastAPI app (`app/main.py`) with CORS configured via `ALLOWED_ORIGINS`.
- `GET /api/personas` to list personas for the frontend dropdown.
- `POST /api/generate` to draft a persona-voice reply (draft, alternate,
  style notes) using the OpenAI Responses API with structured JSON output.
- `app/services/persona_engine.py`: prompt assembly, model call, response
  parsing, and persona discovery from the file system.
- File-based persona storage under `app/data/persona/<persona_id>/`
  (`profile.md` + `persona.json`).
- Pydantic request/response schemas in `app/schemas.py`.
- Pytest coverage for the happy path, validation, error paths, and a live
  smoke test against the real model.
- Render deployment config.
