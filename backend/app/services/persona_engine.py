from __future__ import annotations

import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from app.schemas import Example, GenerateResponse, Mode

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_STYLE_PROFILE_PATH = _DATA_DIR / "vk_style_profile.md"
_EXAMPLES_PATH = _DATA_DIR / "persona_vk.json"

_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
_FEW_SHOT_MAX = 24

_MODE_RULES: dict[Mode, str] = {
    "raw_vk": (
        "Mode: raw_vk. Allow conversational rhythm and lowercase casing where natural. "
        "Repetition for emphasis is fine. Filler phrases like 'just double checking' or "
        "'my thinking is' are welcome when they fit. No profanity unless the example pool shows it."
    ),
    "professional_vk": (
        "Mode: professional_vk. Keep VK's directness and self-aware tone, but clean up casing "
        "and reduce filler words. No profanity. Suitable for recruiter, client, or interview email."
    ),
    "short_vk": (
        "Mode: short_vk. Five sentences or fewer. Cut ruthlessly. Preserve the voice. "
        "Suitable for DMs, slack, and quick replies."
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


@lru_cache(maxsize=1)
def _load_style_profile() -> str:
    """
    Method: _load_style_profile
    Objective: Load vk_style_profile.md once and cache it
    Parameters:
        None
    Return:
        str: full markdown contents
    """
    return _STYLE_PROFILE_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_examples() -> tuple[Example, ...]:
    """
    Method: _load_examples
    Objective: Load persona_vk.json once and cache it as immutable tuples
    Parameters:
        None
    Return:
        tuple[Example, ...]: parsed few-shot examples
    """
    raw = json.loads(_EXAMPLES_PATH.read_text(encoding="utf-8"))
    return tuple(Example.model_validate(item) for item in raw)


def _build_messages(
    question: str,
    context: str,
    mode: Mode,
) -> list[dict[str, str]]:
    """
    Method: _build_messages
    Objective: Compose the system + few-shot + user messages for the LLM
    Parameters:
        question (str): The user's question
        context (str): Situational context (e.g., "recruiter email")
        mode (Mode): raw_vk, professional_vk, or short_vk
    Return:
        list[dict[str, str]]: messages in OpenAI chat completions shape
    """
    profile = _load_style_profile()
    examples = _load_examples()[:_FEW_SHOT_MAX]

    system_content = (
        f"{profile}\n\n"
        f"## Mode for this draft\n{_MODE_RULES[mode]}\n\n"
        "## Output\n"
        "Return JSON matching the GenerateResponse schema with three fields:\n"
        "- draft: the primary VK-voice draft (the main one Donna will send).\n"
        "- alternate: a second take that says the same thing differently.\n"
        "- style_notes: 2 to 4 short bullet strings describing what choices you made.\n"
        "Do not invent facts. If the question requires information you do not have, "
        "say what is missing in the draft itself."
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    for example in examples:
        messages.append({"role": "user", "content": example.question})
        messages.append({"role": "assistant", "content": example.answer})

    user_content = (
        f"Mode: {mode}\n"
        f"Context: {context or '(none)'}\n"
        f"Question: {question}"
    )
    messages.append({"role": "user", "content": user_content})
    return messages


def generate_vk_response(
    question: str,
    context: str,
    mode: Mode,
) -> GenerateResponse:
    """
    Method: generate_vk_response
    Objective: Draft a VK-voice reply via the OpenAI Structured Outputs API
    Parameters:
        question (str): The user's question
        context (str): Situational context (e.g., "recruiter email")
        mode (Mode): raw_vk, professional_vk, or short_vk
    Return:
        GenerateResponse: draft, alternate, style_notes
    """
    messages = _build_messages(question, context, mode)
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
    except APIError:
        logger.exception("openai api error")
        raise HTTPException(status_code=502, detail="LLM provider error")

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        logger.error("openai returned no parsed content")
        raise HTTPException(status_code=502, detail="LLM returned malformed response")

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "draft generated",
        extra={
            "mode": mode,
            "elapsed_ms": elapsed_ms,
            "question_chars": len(question),
            "draft_chars": len(parsed.draft),
        },
    )
    return parsed
