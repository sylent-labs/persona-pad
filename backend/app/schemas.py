from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["raw_vk", "professional_vk", "short_vk"]


class GenerateRequest(BaseModel):
    """
    Class: GenerateRequest
    Objective: Inbound payload for POST /api/generate
    """

    persona_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=5000)
    context: str = Field(default="", max_length=5000)
    mode: Mode


class GenerateResponse(BaseModel):
    """
    Class: GenerateResponse
    Objective: Outbound payload from POST /api/generate. Mirrors the OpenAI Structured Output schema.
    """

    draft: str
    alternate: str
    style_notes: list[str]


class Example(BaseModel):
    """
    Class: Example
    Objective: One few-shot pair loaded from a persona's persona.json
    """

    question: str
    answer: str


class Persona(BaseModel):
    """
    Class: Persona
    Objective: Lightweight metadata for a persona that the frontend dropdown can render
    """

    id: str
    display_name: str
