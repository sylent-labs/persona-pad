from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import GenerateRequest, GenerateResponse
from app.services.persona_engine import generate_vk_response

load_dotenv()

logging.basicConfig(
    level=os.environ.get("PERSONA_PAD_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="Persona Pad", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    """
    Method: generate
    Objective: Draft a VK-voice reply for the given question/context/mode
    Parameters:
        req (GenerateRequest): question, context, and mode
    Return:
        GenerateResponse: draft, alternate, style_notes
    """
    return generate_vk_response(req.question, req.context, req.mode)
