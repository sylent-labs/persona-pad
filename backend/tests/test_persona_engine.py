"""
Tests for persona_engine and POST /api/generate.

Test coverage:
- Mocked LLM happy path returns the GenerateResponse schema
- Bad mode is rejected at the Pydantic boundary
- POST /api/generate end-to-end with a mocked LLM
- RateLimitError maps to HTTP 429
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
from app.services.persona_engine import generate_vk_response


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
def fixture_invalid_mode() -> tuple[bool, str, type]:
    """
    Method: fixture_invalid_mode
    Objective: Fixture for Pydantic validation of an unknown mode value
    Parameters:
        None
    Return:
        tuple[bool, str, type]: (error_raised, message, exception_type)
    """
    return run_invalid_mode()


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

            response = generate_vk_response(
                question="Why should we hire you?",
                context="Recruiter screening",
                mode="professional_vk",
            )
            return True, response, ""
    except Exception as e:
        return False, None, str(e)


def run_invalid_mode() -> tuple[bool, str, type]:
    """
    Method: run_invalid_mode
    Objective: Confirm Pydantic rejects an unknown mode value
    Parameters:
        None
    Return:
        tuple[bool, str, type]: (error_raised, message, exception_type)
    """
    from pydantic import ValidationError

    try:
        GenerateRequest.model_validate(
            {"question": "hi", "context": "", "mode": "elite_vk"}
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
                        "question": "Are you available next week?",
                        "context": "recruiter",
                        "mode": "professional_vk",
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

            generate_vk_response("hi", "", "short_vk")
            return False, 0, "expected HTTPException, got none"
    except HTTPException as e:
        return True, e.status_code, str(e.detail)
    except Exception as e:
        return False, 0, f"wrong error type: {e}"


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


def test_invalid_mode_rejected(
    fixture_invalid_mode: tuple[bool, str, type],
) -> None:
    """
    Method: test_invalid_mode_rejected
    Objective: Verify Pydantic rejects an unknown mode value
    Parameters:
        fixture_invalid_mode (tuple): (error_raised, message, exception_type)
    Return:
        None
    """
    from pydantic import ValidationError

    error_raised, message, exception_type = fixture_invalid_mode

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
    response = generate_vk_response(
        question="Are you available for a call next week?",
        context="recruiter email",
        mode="professional_vk",
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

    print("--------- TEST INVALID MODE ----------")
    error_raised, message, exception_type = run_invalid_mode()
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
