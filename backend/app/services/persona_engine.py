from __future__ import annotations

import json
import logging
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from openai import APITimeoutError, OpenAI, OpenAIError, RateLimitError
from pydantic import ValidationError

from app.schemas import Example, GenerateResponse, Mode, Persona, PersonaManifest

logger = logging.getLogger(__name__)

_PERSONA_DIR = Path(__file__).resolve().parent.parent / "personas"
_MANIFEST_FILENAME = "persona.json"
_PERSONA_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")

_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
_FEW_SHOT_MAX = 24

# Single source of truth for the cross-mode bans. The full, canonical ban list (with
# every example) lives in voice/mechanics.md and is always loaded. This constant is a
# short reinforcement appended after the channel block for every mode, so the rules
# never have to be duplicated per channel the way the old _MODE_RULES dict did.
_BAN_REINFORCEMENT = (
    "Reinforcement, applies to every mode regardless of channel:\n"
    "- No dash characters anywhere, including inside compound words and ranges. "
    "Write 'self aware' and 'double check' as two words, 'monday to friday' not the "
    "dashed version.\n"
    "- No exclamation points.\n"
    "- Never the 'it is not X, it is Y' pattern or any 'not this, but that' contrast "
    "structure. Just state what it is, in one statement.\n"
    "- No corporate filler from the lexicon avoid list.\n"
    "- Never cite the persona pack, profile, documents, or source material. Never write "
    "'(As per documents)', 'as per documents', 'according to my profile', 'based on the "
    "provided context', or similar. State facts directly as Van Keith would know them."
)

_OUTPUT_INSTRUCTIONS = (
    "Return JSON matching the GenerateResponse schema with three fields:\n"
    "- draft: the primary persona-voice draft (the main one to send).\n"
    "- alternate: a second take that says the same thing differently.\n"
    "- guide: exactly 4 short strategic bullets coaching the user on HOW Van Keith "
    "would approach replying to this specific message. Cover what to lead with, what "
    "to hold back, whether less is more, and sometimes whether to reply at all. These "
    "are tactics for the person sending the reply, not a restatement of the draft. "
    "Flavor: 'they asked about price, do not quote a number, ask their budget first', "
    "'less is more here, a one liner lands better than a paragraph'. Every bullet must "
    "be specific to this message, never generic advice. The guide obeys the same "
    "do-not-invent rule: coach only from known information, never fabricate facts, "
    "prices, names, or relationships.\n"
    "Do not invent facts. The known facts block above is authoritative; if the question "
    "requires information that is neither in the facts nor the background, say what is "
    "missing in the draft itself rather than guessing.\n"
    "Never cite the persona pack, profile, documents, or source material. Never write "
    "'(As per documents)', 'as per documents', 'according to my profile', 'based on the "
    "provided context', or similar meta commentary. State facts directly as Van Keith "
    "would know them."
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
    Objective: Load and validate <persona>/persona.json once per persona and cache it
    Parameters:
        persona_id (str): The persona slug
    Return:
        PersonaManifest: validated manifest (metadata + module path lists)
    """
    raw = json.loads(
        (_persona_path(persona_id) / _MANIFEST_FILENAME).read_text(encoding="utf-8")
    )
    return PersonaManifest.model_validate(raw)


@lru_cache(maxsize=256)
def _load_module(persona_id: str, rel_path: str) -> str:
    """
    Method: _load_module
    Objective: Load a single markdown module from the pack and cache it
    Parameters:
        persona_id (str): The persona slug
        rel_path (str): Module path relative to the persona directory
    Return:
        str: the module's text contents, stripped of trailing whitespace
    """
    return (_persona_path(persona_id) / rel_path).read_text(encoding="utf-8").rstrip()


def _join_modules(persona_id: str, rel_paths: tuple[str, ...]) -> str:
    """
    Method: _join_modules
    Objective: Concatenate several markdown modules with blank-line separators
    Parameters:
        persona_id (str): The persona slug
        rel_paths (tuple[str, ...]): Ordered module paths to join
    Return:
        str: the modules joined in order, separated by blank lines
    """
    return "\n\n".join(_load_module(persona_id, path) for path in rel_paths)


def _render_facts(facts: dict[str, Any]) -> str:
    """
    Method: _render_facts
    Objective: Flatten the structured facts JSON into a compact, deterministic
               'label: value' block so the model always sees the same atomic facts in
               full, instead of relying on similarity retrieval to surface them
    Parameters:
        facts (dict[str, Any]): the parsed facts.json, a dict of grouped fields
    Return:
        str: a markdown-ish block grouped by section, each field on its own line
    """
    lines: list[str] = []
    for group, fields in facts.items():
        lines.append(f"### {group.replace('_', ' ').title()}")
        if isinstance(fields, dict):
            for key, value in fields.items():
                label = "note" if key.startswith("_") else key.replace("_", " ")
                lines.append(f"{label}: {value}")
        else:
            lines.append(str(fields))
        lines.append("")
    return "\n".join(lines).rstrip()


@lru_cache(maxsize=32)
def _load_facts_block(persona_id: str, rel_path: str) -> str:
    """
    Method: _load_facts_block
    Objective: Load and render the persona's structured facts file once and cache it
    Parameters:
        persona_id (str): The persona slug
        rel_path (str): Facts JSON path relative to the persona directory
    Return:
        str: the rendered facts block
    """
    raw = json.loads(
        (_persona_path(persona_id) / rel_path).read_text(encoding="utf-8")
    )
    return _render_facts(raw)


@lru_cache(maxsize=32)
def _load_examples(persona_id: str) -> tuple[Example, ...]:
    """
    Method: _load_examples
    Objective: Load <persona>/examples.json (the voice-only few-shot pool) once per
               persona and cache it as immutable tuples
    Parameters:
        persona_id (str): The persona slug
    Return:
        tuple[Example, ...]: parsed few-shot examples
    """
    manifest = _load_manifest(persona_id)
    raw = json.loads(
        (_persona_path(persona_id) / manifest.examples).read_text(encoding="utf-8")
    )
    return tuple(Example.model_validate(item) for item in raw)


def _modules_exist(persona_id: str, manifest: PersonaManifest) -> bool:
    """
    Method: _modules_exist
    Objective: Verify every module a manifest declares is actually present on disk
    Parameters:
        persona_id (str): The persona slug
        manifest (PersonaManifest): the manifest to check
    Return:
        bool: True when all declared modules (always, bio, facts, domains, channels,
              examples) exist as files; False otherwise
    """
    base = _PERSONA_DIR / persona_id
    declared = [
        *manifest.always,
        *manifest.bio,
        manifest.facts,
        *manifest.domains,
        *manifest.channels.values(),
        manifest.examples,
    ]
    return all((base / rel_path).is_file() for rel_path in declared)


def list_personas() -> list[Persona]:
    """
    Method: list_personas
    Objective: Discover available personas by scanning the personas/* directories,
               skipping any whose manifest is broken or whose declared modules are
               missing on disk
    Parameters:
        None
    Return:
        list[Persona]: sorted by id, one entry per valid pack
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
        try:
            manifest = _load_manifest(child.name)
        except (ValidationError, json.JSONDecodeError, OSError):
            logger.warning("skipping persona with broken manifest: %s", child.name)
            continue
        if not _modules_exist(child.name, manifest):
            logger.warning("skipping persona with missing modules: %s", child.name)
            continue
        personas.append(Persona(id=manifest.id, display_name=manifest.display_name))
    return personas


def _build_messages(
    persona_id: str,
    question: str,
    mode: Mode,
) -> list[dict[str, str]]:
    """
    Method: _build_messages
    Objective: Compose the system + few-shot + user messages from the axis-split pack
    Parameters:
        persona_id (str): Which persona's pack to load
        question (str): The user's question
        mode (Mode): raw, professional, short, or email
    Return:
        list[dict[str, str]]: messages in OpenAI chat completions shape
    """
    # Local import to avoid a circular dependency: example_selector imports
    # _load_examples from this module.
    from app.services.example_selector import select_examples

    manifest = _load_manifest(persona_id)
    if mode not in manifest.channels:
        raise HTTPException(status_code=400, detail=f"unsupported mode: {mode}")

    always_block = _join_modules(persona_id, tuple(manifest.always))
    channel_block = _load_module(persona_id, manifest.channels[mode])
    domains_block = _join_modules(persona_id, tuple(manifest.domains))
    bio_block = _join_modules(persona_id, tuple(manifest.bio))
    facts_block = _load_facts_block(persona_id, manifest.facts)

    examples = select_examples(persona_id, question, _FEW_SHOT_MAX)

    system_content = (
        f"{always_block}\n\n"
        f"## Mode for this draft\n{channel_block}\n\n{_BAN_REINFORCEMENT}\n\n"
        f"## Situational voice\n{domains_block}\n\n"
        f"## Background\n{bio_block}\n\n"
        f"## Known facts\n{facts_block}\n\n"
        f"## Output\n{_OUTPUT_INSTRUCTIONS}"
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
        mode (Mode): raw, professional, short, or email
    Return:
        GenerateResponse: draft, alternate, guide
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
            "guide_count": len(parsed.guide),
        },
    )
    return parsed
