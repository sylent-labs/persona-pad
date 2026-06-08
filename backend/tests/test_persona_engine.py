"""
Tests for persona_engine and POST /api/generate.

Test coverage:
- Mocked LLM happy path returns the GenerateResponse schema
- Empty question is rejected at the Pydantic boundary
- POST /api/generate end-to-end with a mocked LLM
- RateLimitError maps to HTTP 429
- list_personas discovers the on-disk persona directories
- GET /api/personas returns the discovered personas
- Unknown persona_id maps to HTTP 404
- Every canonical rule survives prompt assembly in all 4 modes (dedup safety)
- Every module axis (identity, lexicon, domains, bio) survives the axis split
- The composed prompt carries the section scaffolding in all 4 modes
- Long dashes the model emits are stripped from draft and alternate
- Pleasantry openers the model emits are stripped from draft and alternate
- Live smoke test (skipped unless OPENAI_API_KEY is set)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from openai import RateLimitError

from app.main import app
from app.schemas import GenerateRequest, GenerateResponse
from app.services.persona_engine import (
    _build_messages,
    _strip_long_dashes,
    _strip_pleasantries,
    generate_response,
    list_personas,
)

_LONG_DASH_CHARS = "‐‑‒–—―−"

_DEFAULT_PERSONA_ID = "van_keith"
_ALL_MODES = ("raw", "professional", "short", "email")

# Each canonical rule must survive Phase 1 dedup and the Phase 2 axis split, and
# still appear in the assembled system prompt for every mode. Needle is matched
# case-insensitively.
_CANONICAL_RULES: dict[str, str] = {
    "dash ban": "dash",
    "exclamation ban": "exclamation",
    "not-X-it-is-Y ban": "it is not x, it is y",
    "salary deflection": "budget",
    "do-not-invent-facts": "do not invent facts",
}

# Phase 2 is a pure restructure: the same content the old single profile.md fed
# the model must still be present once it is sourced from split modules. These
# needles sample each axis (identity, voice, lexicon, every domain, every bio
# chunk) so a dropped or mis-listed module is caught for all four modes.
_CONTENT_COVERAGE: dict[str, str] = {
    "identity": "harvey specter",
    "lexicon-avoid": "synergy",
    "domain-business": "does the deal make sense",
    "domain-engineering": "this pr is starting to carry too many concerns",
    "domain-job-search": "recruiter authenticity",
    "domain-car-sales": "best thing is to see the unit first",
    "domain-sylent": "movement in silence",
    "domain-relationship": "i need to feel like i’m actually being chosen",
    "domain-assistant": "we need to up our game here",
    "domain-negotiation": "the deal has to make sense on both sides",
    "bio-background": "arizona state university",
    "bio-projects": "signalforge",
    "bio-challenges": "hide my email",
    "bio-contact": "650-281-1984",
    "bio-canonical-answers": "tell me about yourself",
}

# The composed system prompt must carry the new section scaffolding in every mode.
_SECTION_HEADERS: tuple[str, ...] = (
    "## Mode for this draft",
    "## Situational voice",
    "## Background and facts",
    "## Output",
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def fixture_generate_with_mock() -> tuple[bool, GenerateResponse | None, str]:
    """
    Method: fixture_generate_with_mock
    Objective: Fixture for happy-path generation with a mocked OpenAI client
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    return run_generate_with_mock()


@pytest.fixture
def fixture_invalid_request() -> tuple[bool, str, type]:
    """
    Method: fixture_invalid_request
    Objective: Fixture asserting Pydantic rejects a malformed GenerateRequest
    Parameters:
        None
    Return:
        tuple[bool, str, type]: (error_raised, message, exception_type)
    """
    return run_invalid_request()


@pytest.fixture
def fixture_generate_endpoint() -> tuple[bool, int, dict[str, Any], str]:
    """
    Method: fixture_generate_endpoint
    Objective: Fixture for POST /api/generate end-to-end with a mocked LLM
    Parameters:
        None
    Return:
        tuple[bool, int, dict, str]: (success, status_code, body, error)
    """
    return run_generate_endpoint()


@pytest.fixture
def fixture_rate_limit_maps_to_429() -> tuple[bool, int, str]:
    """
    Method: fixture_rate_limit_maps_to_429
    Objective: Fixture asserting RateLimitError -> HTTPException(429)
    Parameters:
        None
    Return:
        tuple[bool, int, str]: (error_raised, status_code, message)
    """
    return run_rate_limit_maps_to_429()


@pytest.fixture
def fixture_list_personas() -> tuple[bool, list[dict[str, str]], str]:
    """
    Method: fixture_list_personas
    Objective: Fixture for list_personas returning the on-disk personas
    Parameters:
        None
    Return:
        tuple[bool, list[dict[str, str]], str]: (success, items_as_dicts, error)
    """
    return run_list_personas()


@pytest.fixture
def fixture_personas_endpoint() -> tuple[bool, int, list[dict[str, str]], str]:
    """
    Method: fixture_personas_endpoint
    Objective: Fixture for GET /api/personas
    Parameters:
        None
    Return:
        tuple[bool, int, list[dict[str, str]], str]: (success, status_code, body, error)
    """
    return run_personas_endpoint()


@pytest.fixture
def fixture_unknown_persona_404() -> tuple[bool, int, str]:
    """
    Method: fixture_unknown_persona_404
    Objective: Fixture asserting an unknown persona_id maps to HTTP 404
    Parameters:
        None
    Return:
        tuple[bool, int, str]: (error_raised, status_code, message)
    """
    return run_unknown_persona_404()


@pytest.fixture
def fixture_dash_stripped_from_output() -> tuple[bool, GenerateResponse | None, str]:
    """
    Method: fixture_dash_stripped_from_output
    Objective: Fixture asserting generate_response normalizes long dashes the model emits
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    return run_dash_stripped_from_output()


@pytest.fixture
def fixture_pleasantry_stripped_from_output() -> (
    tuple[bool, GenerateResponse | None, str]
):
    """
    Method: fixture_pleasantry_stripped_from_output
    Objective: Fixture asserting generate_response strips pleasantry openers the model emits
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    return run_pleasantry_stripped_from_output()


@pytest.fixture
def fixture_assemble_system_prompts() -> tuple[bool, dict[str, str], str]:
    """
    Method: fixture_assemble_system_prompts
    Objective: Fixture assembling the system prompt for every mode (dedup safety)
    Parameters:
        None
    Return:
        tuple[bool, dict[str, str], str]: (success, prompts_by_mode, error)
    """
    return run_assemble_system_prompts()


# ============================================================================
# RUNNERS
# ============================================================================


def _fake_completion(draft: str = "mocked draft") -> MagicMock:
    """
    Method: _fake_completion
    Objective: Build a MagicMock that mimics chat.completions.parse output
    Parameters:
        draft (str): the draft text to embed in the parsed response
    Return:
        MagicMock: an object with .choices[0].message.parsed populated
    """
    parsed = GenerateResponse(
        draft=draft,
        alternate="mocked alternate",
        style_notes=["direct tone", "no overclaiming"],
    )
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message = MagicMock()
    completion.choices[0].message.parsed = parsed
    return completion


def run_generate_with_mock() -> tuple[bool, GenerateResponse | None, str]:
    """
    Method: run_generate_with_mock
    Objective: Generate a draft with a mocked OpenAI client and return for validation
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    try:
        with patch("app.services.persona_engine._get_client") as mock_get_client:
            client = MagicMock()
            client.chat.completions.parse.return_value = _fake_completion()
            mock_get_client.return_value = client

            response = generate_response(
                persona_id=_DEFAULT_PERSONA_ID,
                question="Why should we hire you?",
                mode="professional",
            )
            return True, response, ""
    except Exception as e:
        return False, None, str(e)


def run_invalid_request() -> tuple[bool, str, type]:
    """
    Method: run_invalid_request
    Objective: Confirm Pydantic rejects a GenerateRequest with an empty question
    Parameters:
        None
    Return:
        tuple[bool, str, type]: (error_raised, message, exception_type)
    """
    from pydantic import ValidationError

    try:
        GenerateRequest.model_validate(
            {
                "persona_id": _DEFAULT_PERSONA_ID,
                "question": "",
                "mode": "raw",
            }
        )
        return False, "no error raised", type(None)
    except ValidationError as e:
        return True, str(e), type(e)
    except Exception as e:
        return False, f"wrong error type: {e}", type(e)


def run_generate_endpoint() -> tuple[bool, int, dict[str, Any], str]:
    """
    Method: run_generate_endpoint
    Objective: Hit POST /api/generate end-to-end with a mocked LLM
    Parameters:
        None
    Return:
        tuple[bool, int, dict, str]: (success, status_code, body, error)
    """
    try:
        with patch("app.services.persona_engine._get_client") as mock_get_client:
            client = MagicMock()
            client.chat.completions.parse.return_value = _fake_completion(
                draft="endpoint draft"
            )
            mock_get_client.return_value = client

            with TestClient(app) as test_client:
                r = test_client.post(
                    "/api/generate",
                    json={
                        "persona_id": _DEFAULT_PERSONA_ID,
                        "question": "Are you available next week?",
                        "mode": "professional",
                    },
                )
                return True, r.status_code, r.json(), ""
    except Exception as e:
        return False, 0, {}, str(e)


def run_rate_limit_maps_to_429() -> tuple[bool, int, str]:
    """
    Method: run_rate_limit_maps_to_429
    Objective: Confirm RateLimitError from the SDK maps to HTTP 429
    Parameters:
        None
    Return:
        tuple[bool, int, str]: (error_raised, status_code, message)
    """
    rate_limit_response = httpx.Response(
        status_code=429,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )

    try:
        with patch("app.services.persona_engine._get_client") as mock_get_client:
            client = MagicMock()
            client.chat.completions.parse.side_effect = RateLimitError(
                message="rate limited",
                response=rate_limit_response,
                body=None,
            )
            mock_get_client.return_value = client

            generate_response(_DEFAULT_PERSONA_ID, "hi", "short")
            return False, 0, "expected HTTPException, got none"
    except HTTPException as e:
        return True, e.status_code, str(e.detail)
    except Exception as e:
        return False, 0, f"wrong error type: {e}"


def run_list_personas() -> tuple[bool, list[dict[str, str]], str]:
    """
    Method: run_list_personas
    Objective: Call list_personas() and serialize results for inspection
    Parameters:
        None
    Return:
        tuple[bool, list[dict[str, str]], str]: (success, items_as_dicts, error)
    """
    try:
        items = [p.model_dump() for p in list_personas()]
        return True, items, ""
    except Exception as e:
        return False, [], str(e)


def run_personas_endpoint() -> tuple[bool, int, list[dict[str, str]], str]:
    """
    Method: run_personas_endpoint
    Objective: Hit GET /api/personas and return the parsed body
    Parameters:
        None
    Return:
        tuple[bool, int, list[dict[str, str]], str]: (success, status_code, body, error)
    """
    try:
        with TestClient(app) as test_client:
            r = test_client.get("/api/personas")
            return True, r.status_code, r.json(), ""
    except Exception as e:
        return False, 0, [], str(e)


def run_unknown_persona_404() -> tuple[bool, int, str]:
    """
    Method: run_unknown_persona_404
    Objective: Confirm an unknown persona_id raises HTTPException(404)
    Parameters:
        None
    Return:
        tuple[bool, int, str]: (error_raised, status_code, message)
    """
    try:
        generate_response(
            persona_id="nobody_here",
            question="hi",
            mode="short",
        )
        return False, 0, "expected HTTPException, got none"
    except HTTPException as e:
        return True, e.status_code, str(e.detail)
    except Exception as e:
        return False, 0, f"wrong error type: {e}"


def run_dash_stripped_from_output() -> tuple[bool, GenerateResponse | None, str]:
    """
    Method: run_dash_stripped_from_output
    Objective: Mock the LLM into returning an em dash and confirm generate_response
               strips it before returning, in both draft and alternate
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    dashed = "keep me in mind if something opens up — i'd be interested."
    try:
        with patch("app.services.persona_engine._get_client") as mock_get_client:
            client = MagicMock()
            completion = MagicMock()
            completion.choices = [MagicMock()]
            completion.choices[0].message = MagicMock()
            completion.choices[0].message.parsed = GenerateResponse(
                draft=dashed,
                alternate="something more aligned – let's talk.",
                style_notes=["direct"],
            )
            client.chat.completions.parse.return_value = completion
            mock_get_client.return_value = client

            response = generate_response(
                persona_id=_DEFAULT_PERSONA_ID,
                question="any update?",
                mode="email",
            )
            return True, response, ""
    except Exception as e:
        return False, None, str(e)


def run_pleasantry_stripped_from_output() -> tuple[bool, GenerateResponse | None, str]:
    """
    Method: run_pleasantry_stripped_from_output
    Objective: Mock the LLM into returning pleasantry openers and confirm
               generate_response strips them from draft and alternate
    Parameters:
        None
    Return:
        tuple[bool, GenerateResponse | None, str]: (success, response, error)
    """
    draft = (
        "Hi Team,\n\nThanks for letting me know. I appreciate the update and the "
        "opportunity to apply. Keep me in mind if something opens up.\n\nRegards,\nVan Keith"
    )
    alternate = "I hope you are doing well. Friday at 3 works."
    try:
        with patch("app.services.persona_engine._get_client") as mock_get_client:
            client = MagicMock()
            completion = MagicMock()
            completion.choices = [MagicMock()]
            completion.choices[0].message = MagicMock()
            completion.choices[0].message.parsed = GenerateResponse(
                draft=draft,
                alternate=alternate,
                style_notes=["direct"],
            )
            client.chat.completions.parse.return_value = completion
            mock_get_client.return_value = client

            response = generate_response(
                persona_id=_DEFAULT_PERSONA_ID,
                question="any update?",
                mode="email",
            )
            return True, response, ""
    except Exception as e:
        return False, None, str(e)


def run_assemble_system_prompts() -> tuple[bool, dict[str, str], str]:
    """
    Method: run_assemble_system_prompts
    Objective: Build the system prompt for every mode with example selection
               stubbed out, so the assembled prompt can be inspected offline
    Parameters:
        None
    Return:
        tuple[bool, dict[str, str], str]: (success, prompts_by_mode, error)
    """
    try:
        # Stub the embedding-backed selector so no network call happens; the
        # canonical rules live in profile.md / email.md / _MODE_RULES, not in
        # the few-shot examples, so an empty pool is fine for this check.
        with patch(
            "app.services.example_selector.select_examples",
            return_value=(),
        ):
            prompts: dict[str, str] = {}
            for mode in _ALL_MODES:
                messages = _build_messages(_DEFAULT_PERSONA_ID, "a test question", mode)
                prompts[mode] = messages[0]["content"]
        return True, prompts, ""
    except Exception as e:
        return False, {}, str(e)


# ============================================================================
# TESTS
# ============================================================================


def test_generate_with_mock_returns_schema(
    fixture_generate_with_mock: tuple[bool, GenerateResponse | None, str],
) -> None:
    """
    Method: test_generate_with_mock_returns_schema
    Objective: Verify mocked generation returns a populated GenerateResponse
    Parameters:
        fixture_generate_with_mock (tuple): (success, response, error)
    Return:
        None
    """
    success, response, error = fixture_generate_with_mock

    assert success, f"mocked generation failed: {error}"
    assert response is not None, "response should not be None"
    assert response.draft == "mocked draft", f"unexpected draft: {response.draft!r}"
    assert response.alternate == "mocked alternate", f"unexpected alt: {response.alternate!r}"
    assert response.style_notes, "style_notes should be non-empty"


def test_invalid_request_rejected(
    fixture_invalid_request: tuple[bool, str, type],
) -> None:
    """
    Method: test_invalid_request_rejected
    Objective: Verify Pydantic rejects an empty question
    Parameters:
        fixture_invalid_request (tuple): (error_raised, message, exception_type)
    Return:
        None
    """
    from pydantic import ValidationError

    error_raised, message, exception_type = fixture_invalid_request

    assert error_raised, f"expected ValidationError, got: {message}"
    assert exception_type is ValidationError, f"wrong exception type: {exception_type}"


def test_generate_endpoint_returns_200_and_schema(
    fixture_generate_endpoint: tuple[bool, int, dict[str, Any], str],
) -> None:
    """
    Method: test_generate_endpoint_returns_200_and_schema
    Objective: Verify POST /api/generate returns 200 with a valid response body
    Parameters:
        fixture_generate_endpoint (tuple): (success, status_code, body, error)
    Return:
        None
    """
    success, status_code, body, error = fixture_generate_endpoint

    assert success, f"endpoint call failed: {error}"
    assert status_code == 200, f"expected 200, got {status_code}: {body}"
    assert body.get("draft") == "endpoint draft", f"unexpected draft: {body!r}"
    assert "alternate" in body, "alternate missing from body"
    assert isinstance(body.get("style_notes"), list), "style_notes should be a list"


def test_rate_limit_maps_to_429(
    fixture_rate_limit_maps_to_429: tuple[bool, int, str],
) -> None:
    """
    Method: test_rate_limit_maps_to_429
    Objective: Verify a RateLimitError is mapped to HTTP 429 with a clear message
    Parameters:
        fixture_rate_limit_maps_to_429 (tuple): (error_raised, status_code, message)
    Return:
        None
    """
    error_raised, status_code, message = fixture_rate_limit_maps_to_429

    assert error_raised, f"expected HTTPException, got nothing. message={message}"
    assert status_code == 429, f"expected 429, got {status_code}"
    assert "rate" in message.lower(), f"expected rate-limit message, got: {message}"


def test_list_personas_includes_van_keith(
    fixture_list_personas: tuple[bool, list[dict[str, str]], str],
) -> None:
    """
    Method: test_list_personas_includes_van_keith
    Objective: Verify list_personas() finds the van_keith persona on disk
    Parameters:
        fixture_list_personas (tuple): (success, items_as_dicts, error)
    Return:
        None
    """
    success, items, error = fixture_list_personas

    assert success, f"list_personas failed: {error}"
    ids = [p["id"] for p in items]
    assert _DEFAULT_PERSONA_ID in ids, f"expected {_DEFAULT_PERSONA_ID} in {ids}"
    vk = next(p for p in items if p["id"] == _DEFAULT_PERSONA_ID)
    assert vk["display_name"] == "Van Keith", f"unexpected display_name: {vk!r}"
    assert vk["default_mode"] == "raw", f"unexpected default_mode: {vk!r}"


def test_personas_endpoint_returns_200_and_list(
    fixture_personas_endpoint: tuple[bool, int, list[dict[str, str]], str],
) -> None:
    """
    Method: test_personas_endpoint_returns_200_and_list
    Objective: Verify GET /api/personas returns 200 with a list of personas
    Parameters:
        fixture_personas_endpoint (tuple): (success, status_code, body, error)
    Return:
        None
    """
    success, status_code, body, error = fixture_personas_endpoint

    assert success, f"endpoint call failed: {error}"
    assert status_code == 200, f"expected 200, got {status_code}: {body}"
    assert isinstance(body, list), f"expected list, got {type(body).__name__}"
    assert any(p.get("id") == _DEFAULT_PERSONA_ID for p in body), (
        f"expected {_DEFAULT_PERSONA_ID} in body: {body}"
    )


def test_unknown_persona_id_returns_404(
    fixture_unknown_persona_404: tuple[bool, int, str],
) -> None:
    """
    Method: test_unknown_persona_id_returns_404
    Objective: Verify an unknown persona_id raises HTTPException(404)
    Parameters:
        fixture_unknown_persona_404 (tuple): (error_raised, status_code, message)
    Return:
        None
    """
    error_raised, status_code, message = fixture_unknown_persona_404

    assert error_raised, f"expected HTTPException, got nothing. message={message}"
    assert status_code == 404, f"expected 404, got {status_code}"
    assert "persona" in message.lower(), f"expected persona-not-found message, got: {message}"


def test_canonical_rules_survive_in_every_mode(
    fixture_assemble_system_prompts: tuple[bool, dict[str, str], str],
) -> None:
    """
    Method: test_canonical_rules_survive_in_every_mode
    Objective: Verify Phase 1 dedup dropped no canonical rule; each one still
               appears in the assembled system prompt for all four modes
    Parameters:
        fixture_assemble_system_prompts (tuple): (success, prompts_by_mode, error)
    Return:
        None
    """
    success, prompts, error = fixture_assemble_system_prompts

    assert success, f"prompt assembly failed: {error}"
    assert set(prompts) == set(_ALL_MODES), (
        f"expected all modes assembled, got: {sorted(prompts)}"
    )

    for mode, content in prompts.items():
        haystack = content.lower()
        for rule_name, needle in _CANONICAL_RULES.items():
            assert needle in haystack, (
                f"canonical rule {rule_name!r} (needle {needle!r}) missing from "
                f"assembled {mode!r} prompt"
            )


def test_content_survives_axis_split_in_every_mode(
    fixture_assemble_system_prompts: tuple[bool, dict[str, str], str],
) -> None:
    """
    Method: test_content_survives_axis_split_in_every_mode
    Objective: Verify the Phase 2 axis split dropped no content; a needle from
               every module axis (identity, lexicon, each domain, each bio chunk)
               still appears in the assembled system prompt for all four modes
    Parameters:
        fixture_assemble_system_prompts (tuple): (success, prompts_by_mode, error)
    Return:
        None
    """
    success, prompts, error = fixture_assemble_system_prompts

    assert success, f"prompt assembly failed: {error}"
    for mode, content in prompts.items():
        haystack = content.lower()
        for axis_name, needle in _CONTENT_COVERAGE.items():
            assert needle.lower() in haystack, (
                f"content {axis_name!r} (needle {needle!r}) missing from "
                f"assembled {mode!r} prompt"
            )


def test_section_scaffolding_present_in_every_mode(
    fixture_assemble_system_prompts: tuple[bool, dict[str, str], str],
) -> None:
    """
    Method: test_section_scaffolding_present_in_every_mode
    Objective: Verify the composed prompt carries the channel/domains/bio/output
               section headers in every mode, so the composition order is locked
    Parameters:
        fixture_assemble_system_prompts (tuple): (success, prompts_by_mode, error)
    Return:
        None
    """
    success, prompts, error = fixture_assemble_system_prompts

    assert success, f"prompt assembly failed: {error}"
    for mode, content in prompts.items():
        for header in _SECTION_HEADERS:
            assert header in content, (
                f"section header {header!r} missing from assembled {mode!r} prompt"
            )


def test_strip_long_dashes_normalizes_all_variants() -> None:
    """
    Method: test_strip_long_dashes_normalizes_all_variants
    Objective: Verify _strip_long_dashes removes every long-dash variant and that a
               spaced clause dash becomes a comma, while ASCII hyphens are untouched
    Parameters:
        None
    Return:
        None
    """
    cleaned = _strip_long_dashes("opens up — i'd be interested")
    assert "—" not in cleaned, f"em dash survived: {cleaned!r}"
    assert cleaned == "opens up, i'd be interested", f"unexpected: {cleaned!r}"

    for dash in _LONG_DASH_CHARS:
        out = _strip_long_dashes(f"a {dash} b")
        assert not any(d in out for d in _LONG_DASH_CHARS), (
            f"dash {dash!r} survived: {out!r}"
        )

    # ASCII hyphen is left alone: it is needed inside URLs (email mode is verbatim).
    url = "see https://python.plainenglish.io/system-design-for-python-abc"
    assert _strip_long_dashes(url) == url, "ASCII hyphen in URL must be preserved"


def test_dash_stripped_from_generated_output(
    fixture_dash_stripped_from_output: tuple[bool, GenerateResponse | None, str],
) -> None:
    """
    Method: test_dash_stripped_from_generated_output
    Objective: Verify generate_response strips long dashes from draft and alternate
               even when the model emits them
    Parameters:
        fixture_dash_stripped_from_output (tuple): (success, response, error)
    Return:
        None
    """
    success, response, error = fixture_dash_stripped_from_output

    assert success, f"generation failed: {error}"
    assert response is not None, "response should not be None"
    assert not any(d in response.draft for d in _LONG_DASH_CHARS), (
        f"long dash survived in draft: {response.draft!r}"
    )
    assert not any(d in response.alternate for d in _LONG_DASH_CHARS), (
        f"long dash survived in alternate: {response.alternate!r}"
    )


def test_strip_pleasantries_removes_filler_keeps_content() -> None:
    """
    Method: test_strip_pleasantries_removes_filler_keeps_content
    Objective: Verify _strip_pleasantries removes pleasantry openers but keeps the
               real content after them, and never touches the allowed cases
    Parameters:
        None
    Return:
        None
    """
    # Pleasantry opener removed, trailing content kept.
    assert (
        _strip_pleasantries("Thanks for the heads up, I'll take a look.")
        == "I'll take a look."
    ), "trailing content must survive a removed opener"
    assert (
        _strip_pleasantries("I hope you are doing well. Friday at 3 works.")
        == "Friday at 3 works."
    ), "hope-you-are-well opener must be removed"
    assert (
        _strip_pleasantries(
            "Thanks for letting me know. I appreciate the update. Keep me in mind."
        )
        == "Keep me in mind."
    ), "stacked pleasantry openers must all be removed"

    # Allowed cases left untouched.
    assert (
        _strip_pleasantries("I would just appreciate at least one day's notice.")
        == "I would just appreciate at least one day's notice."
    ), "a non-pleasantry 'appreciate' must be preserved"
    assert (
        _strip_pleasantries("thank you. merging this now.")
        == "thank you. merging this now."
    ), "a concrete bare thank-you must be preserved"
    assert (
        _strip_pleasantries("Thanks,\nVan Keith") == "Thanks,\nVan Keith"
    ), "the Thanks sign-off must be preserved"


def test_pleasantry_stripped_from_generated_output(
    fixture_pleasantry_stripped_from_output: tuple[bool, GenerateResponse | None, str],
) -> None:
    """
    Method: test_pleasantry_stripped_from_generated_output
    Objective: Verify generate_response strips pleasantry openers from draft and
               alternate even when the model emits them, keeping greeting and content
    Parameters:
        fixture_pleasantry_stripped_from_output (tuple): (success, response, error)
    Return:
        None
    """
    success, response, error = fixture_pleasantry_stripped_from_output

    assert success, f"generation failed: {error}"
    assert response is not None, "response should not be None"

    draft = response.draft.lower()
    for needle in ("thanks for letting me know", "i appreciate the update", "i hope you"):
        assert needle not in draft, f"pleasantry {needle!r} survived: {response.draft!r}"
    assert "i hope you" not in response.alternate.lower(), (
        f"pleasantry survived in alternate: {response.alternate!r}"
    )
    # Real content and structure survive.
    assert "keep me in mind" in draft, f"content dropped: {response.draft!r}"
    assert response.draft.startswith("Hi Team,"), (
        f"greeting must survive: {response.draft!r}"
    )
    assert "friday at 3 works" in response.alternate.lower(), (
        f"content dropped from alternate: {response.alternate!r}"
    )


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="Live smoke requires OPENAI_API_KEY",
)
def test_live_smoke() -> None:
    """
    Method: test_live_smoke
    Objective: Hit the real OpenAI API and assert response shape only
    Parameters:
        None
    Return:
        None
    """
    response = generate_response(
        persona_id=_DEFAULT_PERSONA_ID,
        question="Are you available for a call next week?",
        mode="professional",
    )

    assert response.draft, "live LLM returned empty draft"
    assert response.alternate, "live LLM returned empty alternate"
    assert isinstance(response.style_notes, list), "style_notes should be a list"


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    print("--------- TEST GENERATE WITH MOCK ----------")
    success, response, error = run_generate_with_mock()
    print(f"Result: {'PASSED' if success else 'FAILED'}")
    if response:
        print(f"Draft: {response.draft!r}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST INVALID REQUEST ----------")
    error_raised, message, exception_type = run_invalid_request()
    print(f"Result: {'PASSED' if error_raised else 'FAILED'}")
    print(f"Exception type: {exception_type.__name__}")

    print("--------- TEST GENERATE ENDPOINT ----------")
    success, status_code, body, error = run_generate_endpoint()
    print(f"Result: {'PASSED' if success and status_code == 200 else 'FAILED'}")
    print(f"Status: {status_code}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST RATE LIMIT MAPS TO 429 ----------")
    error_raised, status_code, message = run_rate_limit_maps_to_429()
    print(f"Result: {'PASSED' if error_raised and status_code == 429 else 'FAILED'}")
    print(f"Status: {status_code}, message: {message}")

    print("--------- TEST LIST PERSONAS ----------")
    success, items, error = run_list_personas()
    print(f"Result: {'PASSED' if success else 'FAILED'}")
    print(f"Items: {items}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST PERSONAS ENDPOINT ----------")
    success, status_code, body, error = run_personas_endpoint()
    print(f"Result: {'PASSED' if success and status_code == 200 else 'FAILED'}")
    print(f"Status: {status_code}, body: {body}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST UNKNOWN PERSONA 404 ----------")
    error_raised, status_code, message = run_unknown_persona_404()
    print(f"Result: {'PASSED' if error_raised and status_code == 404 else 'FAILED'}")
    print(f"Status: {status_code}, message: {message}")

    print("--------- TEST DASH STRIPPED FROM OUTPUT ----------")
    success, response, error = run_dash_stripped_from_output()
    ok = success and response is not None and not any(
        d in response.draft for d in _LONG_DASH_CHARS
    )
    print(f"Result: {'PASSED' if ok else 'FAILED'}")
    if response:
        print(f"Draft: {response.draft!r}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST PLEASANTRY STRIPPED FROM OUTPUT ----------")
    success, response, error = run_pleasantry_stripped_from_output()
    ok = (
        success
        and response is not None
        and "thanks for letting me know" not in response.draft.lower()
        and "keep me in mind" in response.draft.lower()
    )
    print(f"Result: {'PASSED' if ok else 'FAILED'}")
    if response:
        print(f"Draft: {response.draft!r}")
    if error:
        print(f"Error: {error}")

    print("--------- TEST CANONICAL RULES SURVIVE IN EVERY MODE ----------")
    success, prompts, error = run_assemble_system_prompts()
    missing: list[str] = []
    for mode, content in prompts.items():
        haystack = content.lower()
        for rule_name, needle in _CANONICAL_RULES.items():
            if needle not in haystack:
                missing.append(f"{mode}:{rule_name}")
    ok = success and not missing
    print(f"Result: {'PASSED' if ok else 'FAILED'}")
    if error:
        print(f"Error: {error}")
    if missing:
        print(f"Missing: {missing}")
