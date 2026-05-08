# Changelog

All notable changes to the PersonaPad frontend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
