from __future__ import annotations

import json
import logging
import os
import re
import time
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from openai import APITimeoutError, OpenAI, OpenAIError, RateLimitError

from app.schemas import Example, GenerateResponse, Mode, Persona

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_PERSONA_DIR = _DATA_DIR / "persona"
_PROFILE_FILENAME = "profile.md"
_EMAIL_PROFILE_FILENAME = "email.md"
_PERSONA_FILENAME = "persona.json"
_PERSONA_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")

_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
_FEW_SHOT_MAX = 24

_MODE_RULES: dict[Mode, str] = {
    "raw": (
        "Mode: raw.\n"
        "Voice. Write as VK. The reference points are Harvey Specter, Ryan Reynolds, "
        "and Robert Downey Jr talking in a room with one other person. A senior software "
        "engineer with thirty years in. Calm, certain, slightly tired of explaining the "
        "obvious. Never enthusiastic. Never happy. Not selling. The other person is the "
        "one trying to convince you. Talk to them like they are sitting across from you, "
        "and only say things you would say to their face.\n"
        "Cadence. End every sentence on a downward inflection in the Chris Voss sense: "
        "settled, declarative, not asking for approval. Use plain words, the kind those "
        "three would actually use. No fancy adjectives, no big words for the sake of it. "
        "Use an analogy only when the point will not land without one. Do not overexplain.\n"
        "Format. Write entirely in lowercase. Periods and commas only when needed. "
        "No profanity unless the example pool already shows it.\n"
        "Hard bans. The output must never contain any of these:\n"
        "1. an exclamation point.\n"
        "2. an em dash, en dash, hyphen, or any other dash character anywhere, including "
        "inside compound words and ranges. Write 'self aware' and 'double check' as two "
        "words. Write 'monday to friday', not the dashed version.\n"
        "3. the rhetorical pattern 'it is not X, it is Y' or any 'not this, but that' "
        "contrast structure. Do not write 'it is not about the money, it is about respect' "
        "or 'it's not a bug, it's a feature'. Just say what it is, in one statement.\n"
        "4. corporate filler from the profile's avoid list."
    ),
    "professional": (
        "Mode: professional.\n"
        "Voice. Same VK underneath: direct, senior engineer, no theater. Clean up casing "
        "and use proper sentence punctuation. Cut filler. No profanity. Suitable for a "
        "recruiter, client, or interview email.\n"
        "Hard bans. The output must never contain any of these:\n"
        "1. an em dash, en dash, hyphen, or any other dash character anywhere, including "
        "inside compound words and ranges.\n"
        "2. the rhetorical pattern 'it is not X, it is Y' or any 'not this, but that' "
        "contrast structure.\n"
        "3. corporate filler from the profile's avoid list."
    ),
    "short": (
        "Mode: short.\n"
        "Voice. Same raw VK voice: lowercase, calm, declarative, downward inflection, "
        "never enthusiastic. Five sentences or fewer. Cut ruthlessly. Suitable for DMs, "
        "Slack, and quick replies.\n"
        "Hard bans. The output must never contain any of these:\n"
        "1. an exclamation point.\n"
        "2. an em dash, en dash, hyphen, or any other dash character anywhere, including "
        "inside compound words and ranges.\n"
        "3. the rhetorical pattern 'it is not X, it is Y' or any 'not this, but that' "
        "contrast structure."
    ),
}


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """
    Method: _get_client
    Objective: Lazily construct the OpenAI client so import-time does not require an API key
    Parameters:
        None
    Return:
        OpenAI: a singleton OpenAI client
    """
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _persona_path(persona_id: str) -> Path:
    """
    Method: _persona_path
    Objective: Resolve and validate the on-disk directory for a persona id
    Parameters:
        persona_id (str): The slug identifying the persona (matches the directory name)
    Return:
        Path: absolute path to the persona's directory
    """
    if not _PERSONA_ID_PATTERN.match(persona_id):
        raise HTTPException(status_code=400, detail="invalid persona_id")

    path = _PERSONA_DIR / persona_id
    if not path.is_dir():
        raise HTTPException(status_code=404, detail=f"persona not found: {persona_id}")
    return path


@lru_cache(maxsize=32)
def _load_style_profile(persona_id: str) -> str:
    """
    Method: _load_style_profile
    Objective: Load <persona>/profile.md once per persona and cache it
    Parameters:
        persona_id (str): The persona slug
    Return:
        str: full markdown contents
    """
    return (_persona_path(persona_id) / _PROFILE_FILENAME).read_text(encoding="utf-8")


@lru_cache(maxsize=32)
def _load_email_profile(persona_id: str) -> str | None:
    """
    Method: _load_email_profile
    Objective: Load <persona>/email.md once per persona and cache it; return None if absent
    Parameters:
        persona_id (str): The persona slug
    Return:
        str | None: full markdown contents, or None when the persona has no email.md
    """
    path = _persona_path(persona_id) / _EMAIL_PROFILE_FILENAME
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=32)
def _load_examples(persona_id: str) -> tuple[Example, ...]:
    """
    Method: _load_examples
    Objective: Load <persona>/persona.json once per persona and cache it as immutable tuples
    Parameters:
        persona_id (str): The persona slug
    Return:
        tuple[Example, ...]: parsed few-shot examples
    """
    raw = json.loads(
        (_persona_path(persona_id) / _PERSONA_FILENAME).read_text(encoding="utf-8")
    )
    return tuple(Example.model_validate(item) for item in raw)


def _to_display_name(persona_id: str) -> str:
    """
    Method: _to_display_name
    Objective: Convert a persona_id slug like 'van_keith' to a human label like 'Van Keith'
    Parameters:
        persona_id (str): The persona slug
    Return:
        str: title-cased display name
    """
    return " ".join(part.capitalize() for part in persona_id.split("_") if part)


def list_personas() -> list[Persona]:
    """
    Method: list_personas
    Objective: Discover available personas by scanning data/persona/* directories
    Parameters:
        None
    Return:
        list[Persona]: sorted by id, one entry per directory containing both
                       profile.md and persona.json
    """
    if not _PERSONA_DIR.is_dir():
        return []

    personas: list[Persona] = []
    for child in sorted(_PERSONA_DIR.iterdir()):
        if not child.is_dir():
            continue
        if not _PERSONA_ID_PATTERN.match(child.name):
            continue
        if not (child / _PROFILE_FILENAME).is_file():
            continue
        if not (child / _PERSONA_FILENAME).is_file():
            continue
        personas.append(
            Persona(id=child.name, display_name=_to_display_name(child.name))
        )
    return personas


def _build_messages(
    persona_id: str,
    question: str,
    mode: Mode,
) -> list[dict[str, str]]:
    """
    Method: _build_messages
    Objective: Compose the system + few-shot + user messages for the LLM
    Parameters:
        persona_id (str): Which persona's profile and examples to load
        question (str): The user's question
        mode (Mode): raw, professional, or short
    Return:
        list[dict[str, str]]: messages in OpenAI chat completions shape
    """
    # Local import to avoid a circular dependency: example_selector imports
    # _load_examples from this module.
    from app.services.example_selector import select_examples

    profile = _load_style_profile(persona_id)
    examples = select_examples(persona_id, question, _FEW_SHOT_MAX)

    system_content = (
        f"{profile}\n\n"
        f"## Mode for this draft\n{_MODE_RULES[mode]}\n\n"
        "## Output\n"
        "Return JSON matching the GenerateResponse schema with three fields:\n"
        "- draft: the primary persona-voice draft (the main one to send).\n"
        "- alternate: a second take that says the same thing differently.\n"
        "- style_notes: 2 to 4 short bullet strings describing what choices you made.\n"
        "Do not invent facts. If the question requires information you do not have, "
        "say what is missing in the draft itself."
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    for example in examples:
        messages.append({"role": "user", "content": example.question})
        messages.append({"role": "assistant", "content": example.answer})

    user_content = f"Mode: {mode}\nQuestion: {question}"
    messages.append({"role": "user", "content": user_content})
    return messages


def generate_response(
    persona_id: str,
    question: str,
    mode: Mode,
) -> GenerateResponse:
    """
    Method: generate_response
    Objective: Draft a persona-voice reply via the OpenAI Structured Outputs API
    Parameters:
        persona_id (str): Which persona to draft as
        question (str): The user's question
        mode (Mode): raw, professional, or short
    Return:
        GenerateResponse: draft, alternate, style_notes
    """
    messages = _build_messages(persona_id, question, mode)
    started = time.perf_counter()

    try:
        completion = _get_client().chat.completions.parse(
            model=_MODEL,
            messages=messages,
            response_format=GenerateResponse,
        )
    except RateLimitError:
        logger.warning("openai rate limited")
        raise HTTPException(status_code=429, detail="LLM rate limited, try again")
    except APITimeoutError:
        logger.warning("openai timeout")
        raise HTTPException(status_code=504, detail="LLM timeout")
    except OpenAIError:
        logger.exception("openai error")
        raise HTTPException(status_code=502, detail="LLM provider error")

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        logger.error("openai returned no parsed content")
        raise HTTPException(status_code=502, detail="LLM returned malformed response")

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "draft generated",
        extra={
            "persona_id": persona_id,
            "mode": mode,
            "elapsed_ms": elapsed_ms,
            "question_chars": len(question),
            "draft_chars": len(parsed.draft),
        },
    )
    return parsed
