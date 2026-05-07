# PersonaPad

PersonaPad is a mobile first web app for chatting with the digital persona of someone you know privately. You ask a question, the app answers in their voice. Useful when the person is no longer reachable and you still want a sense of what they would say. Think of it as a "what would they say" companion that runs in your browser on any device.

The personas in PersonaPad are private people, not public figures. Family, friends, mentors, anyone whose voice mattered to you.

## How it works

You open the app on your phone or laptop and type a message. The frontend sends it to the backend at `/api/generate`. The backend loads the persona profile, builds a system prompt that captures how the person speaks and thinks, and forwards the request to OpenAI. The structured reply comes back and renders as a chat bubble.

The persona itself lives in local files inside the backend: a markdown style profile and a JSON persona definition. Swapping in a new persona means swapping those files.

## Tech stack

Backend runs on Python 3.11 with FastAPI, managed by Poetry. A single endpoint at `POST /api/generate` handles every request.

Frontend is React with TypeScript and Vite, styled mobile first so it feels native on a phone and still works on a desktop browser.

LLM calls go to OpenAI through the Responses API with structured JSON output.

Storage in the MVP is plain local files. No database.

Frontend deploys to Vercel. Backend deploys later on Render, Railway, or Fly.

## Local dev

From `backend/`:

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

From `frontend/`:

```bash
pnpm install
pnpm dev
```

The Vite dev server runs on port 5173 and the FastAPI server on port 8000. CORS is preconfigured for local development.

## Project layout

```
persona-pad/
├── backend/
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── services/persona_engine.py
│       └── data/
│           ├── persona/
│               ├── john_smith/
│                   ├── profile.md
│                   ├── persona.md
│               ├── mike_ross/
│                   ├── profile.md
│                   ├── persona.md
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── api/client.ts
└── README.md
```
