# Changelog

All notable changes to the PersonaPad frontend will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-06-08

### Added
- Rebuild the app shell to a 3-column desktop layout (272px sidebar, fill
  center, 372px right rail) with ambient purple glows; mobile collapses to a
  single column with a hamburger quick-actions drawer.
- Welcome hero with AI-core orb, heading, subtitle, and a 2×2 grid of
  suggestion cards wired to quick actions.
- Tone card on the desktop right rail for reply-mode selection
  (Professional, Raw, Short, Email) with per-mode hints.
- Mode chips row below the thread on mobile for the same mode picker.
- Guide card placeholder in the right rail (empty state until PR3).
- BrandMark, Hero, SuggestionCards, ToneCard, ModeChips, and
  QuickActionGroups components.

### Changed
- Hardcode the active persona to Van Keith (`PERSONA_ID`); remove the persona
  switcher and the `listPersonas()` fetch from the UI.
- Rebuild the sidebar to brand mark plus grouped quick actions only.
- Rework the chat thread: persona block shows Option 1 (`draft`), Option 2
  (`alternate`), style-notes chips, and a Delivered indicator on the last
  user message.
- Restyle the composer as a rounded pill with attach glyph, auto-grow
  textarea, and gradient send button; mode selection lives in the Tone card
  or mode chips, not the composer.
- Mobile header is hamburger plus a centered "VK Van Keith" badge; desktop
  has no top bar.

### Removed
- `QuickActionPicker` dropdown (quick actions live in the sidebar and mobile
  drawer as buttons).

## [0.7.0] - 2026-06-08

### Changed
- Rebrand visible UI copy from PersonaPad to Van Keith Intelligence
  (page title, sidebar name, tagline "Everything Van Keith knows").
- Swap the CSS color tokens in `index.css` to the VKI / Colors palette
  (purple accent, darker surfaces, solid borders). Layout rules unchanged.

## [0.6.0] - 2026-05-19

### Added
- Two new quick actions, "LinkedIn" and "GitHub", placed in the chat group
  right above the email actions. Both send a short question so the persona
  replies with the corresponding URL.
- Section dividers in the quick action list. The sidebar now renders one
  group per category with its own label ("Quick Actions — Chat" and
  "Quick Actions — Email"), and the mobile dropdown mirrors the same
  grouping via `<optgroup>` elements.
- `group: "chat" | "email"` field on `QuickAction` in `src/quickActions.ts`,
  plus exported `QUICK_ACTION_GROUP_LABELS` and `QUICK_ACTION_GROUP_ORDER`
  so labels and order live in a single place.

### Changed
- `Sidebar` iterates over `QUICK_ACTION_GROUP_ORDER` and renders a labeled
  `<nav>` per group instead of a single flat list, with each `aria-label`
  set to the group name.
- `QuickActionPicker` renders an `<optgroup label=…>` per group so the same
  visual grouping shows up on small screens.

## [0.5.1] - 2026-05-18

### Changed
- Message input textarea now auto-grows as the user types or pastes
  multi-line content, up to the existing 160px cap, then scrolls. The
  height is recalculated in a `useLayoutEffect` keyed on the text value
  (reset to `auto`, then set to `scrollHeight`) so the field also shrinks
  back when lines are deleted or after sending clears the input.

## [0.5.0] - 2026-05-18

### Added
- Copy button on every chat bubble. Renders as a small ghost icon button on
  the inner side of the bubble (left of user messages, right of persona
  messages), turns into a green check for ~1.5s after a successful copy.
  Copies just the message text — the `option 1: ` / `option 2: ` label
  prefix is stripped before writing to the clipboard. Error bubbles do not
  get one. Falls back silently if `navigator.clipboard` is unavailable
  (insecure context, etc.).
- Two new email-mode quick actions, "Email availability" and "Email
  template", with `message` values of `"Availability"` and `"Template"`.
  Picking either one auto-switches the mode picker to `email` before
  sending so the persona answers in email mode without the user having to
  flip the toggle manually.
- Optional `mode` field on `QuickAction` so each entry in
  `src/quickActions.ts` can declare which mode it wants the draft
  generated in. The sidebar and the mobile picker both forward it.

### Changed
- `App.handleSend` now accepts an optional `modeOverride: Mode` parameter.
  When the override is provided and differs from the current mode, the
  picker state is updated and the request goes out under the overridden
  mode so the next reply matches what the user picked.
- `QuickActionPicker`, `Sidebar`, and `ChatHeader` `onQuickAction`
  signatures gained an optional `mode?: Mode` argument and pass it through
  to `App` so quick actions that carry a mode reach the request layer.

## [0.4.0] - 2026-05-18

### Added
- Quick action shortcuts for the most common questions (tell me about
  yourself, why are you leaving, what are you looking for, projects you're
  leading, salary expectations). Selecting one immediately sends that
  question as a user message, no typing required.
- `src/quickActions.ts` holds the canonical list of quick actions
  (`id`, `label`, `message`) so the sidebar and the mobile picker render
  from a single source of truth.
- New `QuickActionPicker` component renders a "Quick action…" dropdown in
  the chat header. Shown on mobile only; on desktop the sidebar handles it.
  Resets its value after each pick so the same action can be reused.
- `Sidebar` now renders a "Quick Actions" section beneath the persona
  list as plain buttons. Buttons disable when no persona is selected or a
  request is already in flight, matching the picker's disabled state.

### Changed
- `App` wires `handleSend` to both the sidebar quick action buttons and
  the chat-header picker, and derives a single `quickActionsDisabled`
  flag from `pending || !personaId`.
- Sidebar layout tweaked so the persona list and quick actions both fit
  without the list eating all vertical space. Persona list is
  `flex: 0 1 auto` with `min-height: 0`; quick action list is
  `flex: 0 0 auto` with a `max-height: 280px` cap.
- Chat header name row gets `min-width: 0` and the mobile persona select
  is `flex: 0 1 auto` so the quick action picker sits to the right
  without squashing the persona name. Subtitle truncates with ellipsis
  when space is tight.

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
