"""
Vercel serverless entrypoint.

Vercel's Python runtime detects the `app` symbol exported here and serves it as
an ASGI application. The actual FastAPI app lives in `app/main.py`; this file
exists only so Vercel's filesystem-based routing has a function file at
`/api/index`. All inbound requests are funnelled here by the rewrites in
`vercel.json`, after which FastAPI routes them normally.
"""
from __future__ import annotations

from app.main import app

__all__ = ["app"]
