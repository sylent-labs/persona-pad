from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import GenerateRequest, GenerateResponse, Persona
from app.services.persona_engine import generate_response, list_personas

load_dotenv()

logging.basicConfig(
    level=os.environ.get("PERSONA_PAD_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _parse_allowed_origins() -> list[str]:
    """
    Method: _parse_allowed_origins
    Objective: Read the comma-separated ALLOWED_ORIGINS env var into a clean list
    Parameters:
        None
    Return:
        list[str]: origins permitted by the CORS middleware
    """
    raw = os.environ.get("ALLOWED_ORIGINS", _DEFAULT_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="PersonaPad", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, object]:
    """
    Method: root
    Objective: Liveness probe and identity for the deployed app
    Parameters:
        None
    Return:
        dict[str, object]: app name + ok flag
    """
    return {"app": "persona-pad", "ok": True}


@app.get("/api/personas", response_model=list[Persona])
def personas() -> list[Persona]:
    """
    Method: personas
    Objective: List the personas that the frontend dropdown can choose from
    Parameters:
        None
    Return:
        list[Persona]: discovered personas, sorted by id
    """
    return list_personas()


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    """
    Method: generate
    Objective: Draft a persona-voice reply for the given question/mode
    Parameters:
        req (GenerateRequest): persona_id, question, and mode
    Return:
        GenerateResponse: draft, alternate, style_notes
    """
    return generate_response(req.persona_id, req.question, req.mode)
