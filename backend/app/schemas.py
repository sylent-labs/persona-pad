from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["raw", "professional", "short", "email"]


class GenerateRequest(BaseModel):
    """
    Class: GenerateRequest
    Objective: Inbound payload for POST /api/generate
    """

    persona_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=5000)
    mode: Mode


class GenerateResponse(BaseModel):
    """
    Class: GenerateResponse
    Objective: Outbound payload from POST /api/generate. Mirrors the OpenAI Structured Output schema.
    Fields:
        draft (str): primary persona-voice reply, the main one to send
        alternate (str): a second take that says the same thing differently
        guide (list[str]): strategic bullets coaching the user on how Van Keith would
                           approach replying to this specific message. Produced in the
                           same single LLM call and dissected out client-side.
    """

    draft: str
    alternate: str
    guide: list[str]


class Example(BaseModel):
    """
    Class: Example
    Objective: One few-shot pair loaded from a persona's examples.json. The optional
               domain tag (engineering, job_search, casual, ...) is used by the example
               selector for domain-aware retrieval; it is absent on legacy untagged pools.
    """

    question: str
    answer: str
    domain: str | None = None


class Persona(BaseModel):
    """
    Class: Persona
    Objective: Lightweight metadata for a persona that the frontend dropdown can render
    """

    id: str
    display_name: str


class PersonaManifest(BaseModel):
    """
    Class: PersonaManifest
    Objective: The persona.json manifest for an axis-split pack. Holds metadata plus the
               relative paths of every module. Contains no voice content itself.
    Fields:
        id (str): persona slug, matches the directory name
        display_name (str): human label for the dropdown
        default_mode (Mode): channel used when the caller does not specify one
        always (list[str]): voice modules concatenated into every prompt
        bio (list[str]): biographical prose modules
        facts (str): relative path to the structured facts JSON
        domains (list[str]): situational voice modules
        channels (dict[Mode, str]): per-mode format overlay paths
        examples (str): relative path to the few-shot pool
    """

    id: str
    display_name: str
    default_mode: Mode
    always: list[str]
    bio: list[str]
    facts: str
    domains: list[str]
    channels: dict[Mode, str]
    examples: str
