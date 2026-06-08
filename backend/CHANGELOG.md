# Changelog

All notable changes to the PersonaPad backend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-06-08

### Added

- Deterministic post-processing on generated drafts: long dashes (em/en and
  variants) are replaced with commas, and reflexive pleasantry openers (thanks
  for reaching out, I hope you are well, I appreciate the update, and similar)
  are stripped before the response is returned.
- Cross-mode `no pleasantries` policy in `van_keith/policies.md` with expanded
  banned-opener list in the email channel rules.
- Offline tests covering dash normalization, pleasantry stripping, and
  end-to-end output cleanup on mocked LLM responses.

## [0.6.0] - 2026-06-08

### Added

- Axis-split persona pack layout for `van_keith`: always-loaded voice modules
  (`identity.md`, `voice.md`, `lexicon.md`, `policies.md`), situational
  `domains/`, factual `bio/`, per-mode `channels/`, and a separate
  `examples.json` few-shot pool.
- `PersonaManifest` schema and module loaders (`_load_manifest`, `_load_module`)
  that compose the system prompt from manifest-declared files.
- `default_mode` on `GET /api/personas` responses, read from each persona's
  manifest.
- Offline tests that every axis module and section header survives prompt
  assembly in all four modes after the restructure.

### Changed

- Prompt assembly now composes always modules, the selected channel, all
  domains, and all bio chunks from disk instead of monolithic `profile.md` and
  inline `_MODE_RULES`.
- `persona.json` is a manifest only (metadata plus module lists); few-shot
  examples moved to `examples.json`.
- `list_personas` validates declared modules at listing time and skips personas
  with broken manifests or missing files.

### Removed

- Monolithic `van_keith/profile.md` and root-level `van_keith/email.md`
  (content lives under the axis layout).

## [0.5.3] - 2026-06-08

### Added

- Canonical "resume filler and recruiter pitch phrases" avoid list in
  `van_keith/profile.md`, shared by every channel including email.
- Offline test that dash, exclamation, contrast, salary-deflection, and
  do-not-invent-facts rules still appear in the assembled system prompt
  for all four modes after dedup.

### Changed

- Deduplicated persona voice rules: `profile.md` and `email.md` are the
  single source of truth; `email.md` defers to profile for shared bans
  instead of restating them; `_MODE_RULES` carries only per-mode format
  deltas plus a compact reinforcement line for the three most-violated
  bans. Reduces contradictory instructions when rules are updated.

## [0.5.2] - 2026-05-21

### Added

- Recruiter authenticity guidance for email mode when a recipient asks why you
  applied or what you liked about the company and role without sounding like
  AI: new section in `van_keith/email.md`, matching rules in `profile.md`,
  three few-shot entries in `persona.json` (including the Keepsafe / Christa
  reference draft), and `_MODE_RULES["email"]` instructions plus extra hard
  bans on cover-letter filler (`passionate about`, `thrilled to apply`,
  `excited about the opportunity`, `your mission resonates`, and similar).

## [0.5.1] - 2026-05-19

### Added

- Five new few-shot entries in `app/data/persona/van_keith/persona.json`:
  short LinkedIn and GitHub Q&A pairs that return the URL plain, two
  recruiter-email drafts (LinkedIn and GitHub) showing the exact greeting
  + body + sign-off shape with plain-text URLs, and a meta entry
  documenting the URL formatting rule so it can be retrieved as
  semantic context.
- Hard ban #9 in `_MODE_RULES["email"]` forbidding markdown formatting in
  email drafts. URLs must be plain text exactly as given, with no markdown
  link syntax (`[text](url)`), angle brackets (`<url>`), or bold/italic
  wrapping. The body also stays free of `**bold**`, `*italic*`, code
  fences, headings, and list markup. Was added after the model was
  observed auto-linkifying LinkedIn URLs as `[https://…](https://…)`
  inside email drafts.

## [0.5.0] - 2026-05-12

### Added

- New `email` mode for `POST /api/generate`. Joins the existing `raw`,
  `professional`, and `short` modes. Drafts come back shaped as an actual
  email (greeting, body, sign off) with proper sentence casing, kept short
  by default, and personalized to the role/company/recipient when those
  details are in the question.
- Per-persona `email.md` channel file under
  `app/data/persona/<persona_id>/email.md`. When present and `mode="email"`,
  it is injected into the system prompt under an `## Email channel rules`
  section between `profile.md` and the mode block. Absent file is a no-op,
  so personas without an email profile still work in email mode using just
  the inline mode rules.
- `_load_email_profile(persona_id)` in `app/services/persona_engine.py`,
  cached with `lru_cache(maxsize=32)` like the other persona loaders.
  Returns `None` when the persona has no `email.md`.
- Seeded `backend/app/data/persona/van_keith/email.md` with the Van Keith
  email channel rules (voice, length targets, greeting/sign-off rules,
  banned phrases, reference emails, and the cold-outreach boilerplate).
- Email-mode hard bans baked into `_MODE_RULES["email"]`: no dashes (incl.
  inside compound words and ranges), no "not X, it is Y" contrast, no email
  cliches (`hope this finds you well`, `just checking in`, `kindly`, etc.),
  no generic resume filler (`strong / extensive / deep / proven` qualifiers,
  `focused on delivering impactful solutions`, `passionate about`, etc.),
  no soft closes (`I would be open to a call`, `happy to chat`, `looking
  forward to hearing from you`), and a no-redundancy rule that prevents
  repeating role/stack/availability across paragraphs.

### Changed

- `Mode` literal in `app/schemas.py` extended from
  `Literal["raw", "professional", "short"]` to
  `Literal["raw", "professional", "short", "email"]`. Existing clients that
  only send the original three modes are unaffected.
- `_build_messages` now conditionally prepends an `## Email channel rules`
  block to the system prompt when `mode == "email"` and the persona has an
  `email.md`. All other modes produce the same system prompt as before.

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
