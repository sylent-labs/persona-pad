# Changelog

All notable changes to the PersonaPad backend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
