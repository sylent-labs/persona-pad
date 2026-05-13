# Changelog

All notable changes to the PersonaPad frontend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-12

### Added
- New `email` option in the mode picker, matching the backend `email` mode
  added in backend `0.5.0`. Picks a draft shaped as a real email (greeting,
  body, sign off) instead of a chat-style reply. Hint copy reads
  "Reply structured for email: greeting, body, sign-off."
- `"email"` added to the exported `Mode` union in `src/api/types.ts` and a
  matching entry appended to `MODES` so the UI mode list stays the source
  of truth for the picker.

## [0.2.2] - 2026-05-10

### Changed
- `frontend/.env.production` now points `VITE_API_BASE_URL` at
  `https://persona-pad-backend-docker.onrender.com`, the new Dockerized
  backend service on Render that supports `git-crypt unlock` at boot
  (see backend `0.4.0`). The old `persona-pad-backend.onrender.com`
  service is retired.

## [0.2.1] - 2026-05-09

### Added
- Persona response bubbles are now prefixed with `option 1:` and `option 2:`
  labels so it's clear the user is being shown two takes on the same answer
  rather than two separate replies. Labels are only attached when both a draft
  and an alternate come back; a single-response case stays unlabeled.
- Optional `label` field on `ChatMessage` and matching optional prop on
  `Bubble` so the labeling is opt-in per message instead of role-driven.

### Fixed
- `ChatThread` now passes an empty string instead of `undefined` when a
  message has no label, avoiding a React prop-type mismatch when the optional
  `label` prop is forwarded.

## [0.2.0] - 2026-05-08

### Fixed
- Replaced the deprecated `apple-mobile-web-app-capable` meta tag warning by
  also emitting the standard `mobile-web-app-capable` tag. The Apple variant
  stays for iOS Safari; the new one stops Chrome/Edge from logging the
  deprecation notice.

## [0.1.0] - 2026-05-07

### Added
- Vite + React + TypeScript scaffold with strict ESLint config.
- `ChatBox`, `ResponseCard`, `ChatHeader`, and `Sidebar` components.
- Typed API client (`src/api/client.ts`) covering `/api/generate` and
  `/api/personas`.
- Persona type and persona-aware UI (sidebar list + active highlight).
- iMessage-style chat thread inside an iPhone bezel for the mobile-first view.
- Desktop layout: 280px left sidebar (brand + persona list) and a centered
  chat column with a 760px max width for comfortable reading lines.
- Subtle radial blue/violet gradient background and matching scrollbars.
- Production environment config (`.env.production`) pointing at the deployed
  Render backend.
- Vercel deployment configuration.
- Vitest coverage for `ChatBox` submission and `ResponseCard` clipboard
  behavior.

### Changed
- Layout reworked from a mobile-only chat into a desktop-first sidebar shell
  while keeping the mobile bezel view intact.
- Send button rendered as a rounded 40px square on desktop instead of the
  small mobile circle.

### Fixed
- Vercel build wiring corrected so production builds resolve the correct entry
  and the API base URL is read from the environment instead of being hardcoded.
