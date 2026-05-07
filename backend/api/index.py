"""
Vercel serverless entry point.

Vercel's Python runtime auto-detects an exported ASGI `app` variable
and serves it. The vercel.json `rewrites` block sends every request
into this single function so FastAPI handles all routing internally.
"""

from app.main import app  # noqa: F401
