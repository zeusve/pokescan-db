"""Tests for PokemonTCGClient."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.pokemon_client import (
    PokemonTCGClient,
    RateLimitExceededError,
)


def _mock_response(status_code: int = 200, json_data: dict = None, headers: dict = None) -> httpx.Response:
    """Build a fake httpx.Response."""
    resp = httpx.Response(
        status_code=status_code,
        json=json_data or {},
        headers=headers or {},
        request=httpx.Request("GET", "https://test.example.com"),
    )
    return resp


@pytest.fixture
def client() -> PokemonTCGClient:
    return PokemonTCGClient(
        base_url="https://test.example.com",
        api_key="test-key-123",
        timeout=5.0,
    )


# ── test_get_card_success ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_card_success(client: PokemonTCGClient) -> None:
    card_data = {"id": "base1-58", "name": "Pikachu", "hp": "40"}
    mock_resp = _mock_response(200, {"data": card_data})

    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, return_value=mock_resp):
        async with client:
            result = await client.get_card("base1-58")

    assert result == card_data
    assert result["name"] == "Pikachu"


# ── test_get_card_not_found ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_card_not_found(client: PokemonTCGClient) -> None:
    mock_resp = _mock_response(404, {"error": "Not Found"})

    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, return_value=mock_resp):
        async with client:
            result = await client.get_card("fake-id")

    assert result is None


# ── test_rate_limit_retry ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limit_retry(client: PokemonTCGClient) -> None:
    """First call returns 429, second returns 200 — client must retry."""
    card_data = {"id": "base1-58", "name": "Pikachu"}
    resp_429 = _mock_response(429, {}, {"Retry-After": "0"})
    resp_200 = _mock_response(200, {"data": card_data})

    call_count = 0

    async def mock_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return resp_429
        return resp_200

    with patch.object(httpx.AsyncClient, "request", side_effect=mock_request):
        async with client:
            result = await client.get_card("base1-58")

    assert result == card_data
    assert call_count == 2


# ── test_rate_limit_exhausted ────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limit_exhausted(client: PokemonTCGClient) -> None:
    """All retries return 429 — client must raise RateLimitExceededError."""
    resp_429 = _mock_response(429, {}, {"Retry-After": "0"})

    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, return_value=resp_429):
        async with client:
            with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
                await client.get_card("base1-58")


# ── test_api_key_header ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_key_header(client: PokemonTCGClient) -> None:
    """Verify X-Api-Key header is sent when api_key is configured."""
    card_data = {"id": "base1-58", "name": "Pikachu"}
    mock_resp = _mock_response(200, {"data": card_data})

    with patch.object(httpx.AsyncClient, "__init__", return_value=None) as mock_init, \
         patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, return_value=mock_resp), \
         patch.object(httpx.AsyncClient, "is_closed", new_callable=lambda: property(lambda self: False)), \
         patch.object(httpx.AsyncClient, "aclose", new_callable=AsyncMock):
        async with client:
            pass

    headers = client._build_headers()
    assert headers["X-Api-Key"] == "test-key-123"


# ── test_no_api_key_header ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_api_key_header() -> None:
    """Verify X-Api-Key is absent when no api_key is provided."""
    no_key_client = PokemonTCGClient(base_url="https://test.example.com")
    headers = no_key_client._build_headers()
    assert "X-Api-Key" not in headers


# ── test_search_cards_success ────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_cards_success(client: PokemonTCGClient) -> None:
    cards = [
        {"id": "base1-58", "name": "Pikachu"},
        {"id": "xy1-42", "name": "Pikachu"},
    ]
    mock_resp = _mock_response(200, {"data": cards})

    with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, return_value=mock_resp):
        async with client:
            result = await client.search_cards("name:pikachu")

    assert len(result) == 2
    assert result[0]["name"] == "Pikachu"


# ── test_server_error_retry ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_server_error_retry(client: PokemonTCGClient) -> None:
    """First call returns 500, second returns 200 — client retries."""
    card_data = {"id": "base1-58", "name": "Pikachu"}
    resp_500 = _mock_response(500, {"error": "Internal Server Error"})
    resp_200 = _mock_response(200, {"data": card_data})

    call_count = 0

    async def mock_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return resp_500
        return resp_200

    with patch.object(httpx.AsyncClient, "request", side_effect=mock_request):
        async with client:
            result = await client.get_card("base1-58")

    assert result == card_data
    assert call_count == 2


# ── test_env_defaults ────────────────────────────────────────────────

def test_env_defaults() -> None:
    """Client uses env vars when no explicit params given."""
    with patch.dict("os.environ", {
        "POKEMON_TCG_BASE_URL": "https://custom.api.example.com",
        "POKEMON_TCG_API_KEY": "env-key-456",
    }):
        env_client = PokemonTCGClient()
        assert env_client._base_url == "https://custom.api.example.com"
        assert env_client._api_key == "env-key-456"


def test_default_base_url() -> None:
    """Client falls back to empty base URL when env is unset."""
    with patch.dict("os.environ", {}, clear=True):
        default_client = PokemonTCGClient()
        assert default_client._base_url == ""
        assert default_client._api_key is None
