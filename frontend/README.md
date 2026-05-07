# PersonaPad Frontend

The mobile first chat UI for PersonaPad. Built with React, TypeScript, and Vite.

## What it does

This is the only screen the user sees. It opens a chat with the digital persona configured in the backend. The user types a message, the app calls `POST /api/generate`, and the reply renders as a bubble.

The whole layout is mobile first. It must feel native on a phone before it works on a desktop browser.

## Stack

- React 18 with TypeScript (strict mode)
- Vite for dev server and build
- Vitest plus React Testing Library for tests
- Plain `fetch` through a typed API client (no SDK)

## Local dev

```bash
pnpm install
pnpm dev      # Vite dev server on :5173
pnpm build
pnpm test     # vitest
```

The dev server expects the backend at `http://localhost:8000` by default. Override with the `VITE_API_BASE_URL` env var if you run the backend elsewhere.

```bash
VITE_API_BASE_URL=http://192.168.1.20:8000 pnpm dev
```

## Project layout

```
src/
├── App.tsx                 # Root component, holds chat state
├── main.tsx                # Entry point
├── components/
│   ├── ChatBox.tsx         # Input + send button
│   └── ResponseCard.tsx    # Reply bubble
└── api/
    ├── client.ts           # Typed fetch wrapper for /api/generate
    └── types.ts            # Mirrors backend Pydantic models
```

## Conventions

- Strict TypeScript. No `any` without a comment justifying why.
- Named exports on components; no default exports.
- All API calls go through `src/api/client.ts`. No `fetch` inside components.
- Types in `src/api/types.ts` must mirror the backend Pydantic models in `backend/app/schemas.py`. When one changes, change both in the same PR.
- Tests live next to the source: `Foo.tsx` and `Foo.test.tsx`.

See `.claude/rules/45-typescript-standards.md` at the repo root for the full standard.
