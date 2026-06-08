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

from app.schemas import (
    Example,
    GenerateResponse,
    Mode,
    Persona,
    PersonaManifest,
)

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_PERSONA_DIR = _DATA_DIR / "persona"
_MANIFEST_FILENAME = "persona.json"
_EXAMPLES_FILENAME = "examples.json"
_PERSONA_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")

_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
_FEW_SHOT_MAX = 24

# The full voice, bans, and avoid lists live in the always-loaded modules
# (identity.md, voice.md, lexicon.md, policies.md), which are assembled into the
# system prompt ahead of the per-mode channel block. _BAN_REINFORCEMENT is one
# compact reinforcement line for the three most-violated bans, appended after the
# channel block for every mode. It is not the home for any rule; the complete ban
# and avoid lists live in the modules. See
# .claude/plans/2026-06-08-persona-data-restructure-phase2.md.
_BAN_REINFORCEMENT = (
    "Reinforcement, the three most-violated bans, they override any writing habit: "
    "no exclamation points anywhere; no dash characters of any kind, including "
    "inside compound words and ranges, so write 'end to end', 'full time', and "
    "'monday to friday' as separate words; and never the 'it is not X, it is Y' or "
    "any 'not this, but that' contrast, just state the thing. The complete ban and "
    "avoid lists are in the voice and lexicon rules above; follow all of them."
)


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
def _load_manifest(persona_id: str) -> PersonaManifest:
    """
    Method: _load_manifest
    Objective: Load and validate <persona>/persona.json (the manifest) once per persona
    Parameters:
        persona_id (str): The persona slug
    Return:
        PersonaManifest: validated manifest declaring metadata and module files
    """
    raw = json.loads(
        (_persona_path(persona_id) / _MANIFEST_FILENAME).read_text(encoding="utf-8")
    )
    return PersonaManifest.model_validate(raw)


@lru_cache(maxsize=256)
def _load_module(persona_id: str, relpath: str) -> str:
    """
    Method: _load_module
    Objective: Load a single persona module file (relative to the persona dir) and cache it
    Parameters:
        persona_id (str): The persona slug
        relpath (str): Module path relative to the persona directory, e.g. 'voice.md'
                       or 'domains/engineering.md'
    Return:
        str: full markdown contents of the module
    """
    base = _persona_path(persona_id)
    path = (base / relpath).resolve()
    # Guard against path traversal in a manifest; modules must stay inside the persona dir.
    if base.resolve() not in path.parents:
        raise HTTPException(status_code=500, detail="invalid persona module path")
    if not path.is_file():
        raise HTTPException(
            status_code=500, detail=f"persona module missing: {relpath}"
        )
    return path.read_text(encoding="utf-8")


def _join_modules(persona_id: str, relpaths: list[str]) -> str:
    """
    Method: _join_modules
    Objective: Load each listed module and concatenate them with blank-line separators
    Parameters:
        persona_id (str): The persona slug
        relpaths (list[str]): module paths relative to the persona directory
    Return:
        str: the modules' contents joined by a blank line, in listed order
    """
    return "\n\n".join(_load_module(persona_id, rel) for rel in relpaths)


@lru_cache(maxsize=32)
def _load_examples(persona_id: str) -> tuple[Example, ...]:
    """
    Method: _load_examples
    Objective: Load <persona>/examples.json once per persona and cache it as immutable tuples
    Parameters:
        persona_id (str): The persona slug
    Return:
        tuple[Example, ...]: parsed few-shot examples
    """
    raw = json.loads(
        (_persona_path(persona_id) / _EXAMPLES_FILENAME).read_text(encoding="utf-8")
    )
    return tuple(Example.model_validate(item) for item in raw)


def list_personas() -> list[Persona]:
    """
    Method: list_personas
    Objective: Discover available personas by scanning data/persona/* directories
    Parameters:
        None
    Return:
        list[Persona]: sorted by id, one entry per directory with a valid manifest,
                       an examples file, and every module the manifest declares present
                       on disk. A persona with a broken manifest or a missing module is
                       skipped rather than crashing the whole listing.
    """
    if not _PERSONA_DIR.is_dir():
        return []

    personas: list[Persona] = []
    for child in sorted(_PERSONA_DIR.iterdir()):
        if not child.is_dir():
            continue
        if not _PERSONA_ID_PATTERN.match(child.name):
            continue
        if not (child / _MANIFEST_FILENAME).is_file():
            continue
        if not (child / _EXAMPLES_FILENAME).is_file():
            continue
        try:
            manifest = _load_manifest(child.name)
            _validate_modules_present(child.name, manifest)
        except Exception:
            logger.exception("skipping persona with invalid manifest: %s", child.name)
            continue
        personas.append(
            Persona(
                id=manifest.id,
                display_name=manifest.display_name,
                default_mode=manifest.default_mode,
            )
        )
    return personas


def _validate_modules_present(persona_id: str, manifest: PersonaManifest) -> None:
    """
    Method: _validate_modules_present
    Objective: Confirm every module the manifest declares exists on disk, so a broken
               persona is caught at listing time instead of mid-generation
    Parameters:
        persona_id (str): The persona slug
        manifest (PersonaManifest): the persona's parsed manifest
    Return:
        None
    """
    base = _persona_path(persona_id)
    declared = [
        *manifest.always,
        *manifest.domains,
        *manifest.bio,
        *manifest.channels.values(),
    ]
    for relpath in declared:
        if not (base / relpath).is_file():
            raise HTTPException(
                status_code=500,
                detail=f"persona {persona_id} missing module: {relpath}",
            )


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
        mode (Mode): raw, professional, short, or email
    Return:
        list[dict[str, str]]: messages in OpenAI chat completions shape
    """
    # Local import to avoid a circular dependency: example_selector imports
    # _load_examples from this module.
    from app.services.example_selector import select_examples

    manifest = _load_manifest(persona_id)
    examples = select_examples(persona_id, question, _FEW_SHOT_MAX)

    # Phase 2 composes from the axis layout but loads everything unconditionally:
    # always modules, the selected channel, then ALL domains and ALL bio. This keeps
    # the same coverage as the old single profile.md. Topic routing and relevance
    # retrieval are deferred to Phase 4.
    always_block = _join_modules(persona_id, manifest.always)
    channel_block = _load_module(persona_id, manifest.channels[mode])
    domains_block = _join_modules(persona_id, manifest.domains)
    bio_block = _join_modules(persona_id, manifest.bio)

    system_content = (
        f"{always_block}\n\n"
        f"## Mode for this draft\n{channel_block}\n\n{_BAN_REINFORCEMENT}\n\n"
        f"## Situational voice\n{domains_block}\n\n"
        f"## Background and facts\n{bio_block}\n\n"
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
