"""Client for the Pokémon TCG API (https://pokemontcg.io)."""

import asyncio
import os
from typing import Any, Optional

import httpx

DEFAULT_BASE_URL = "https://api.pokemontcg.io/v2"
DEFAULT_TIMEOUT = 10.0
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0


class PokemonTCGClientError(Exception):
    """Base exception for PokemonTCGClient errors."""


class CardNotFoundError(PokemonTCGClientError):
    """Raised when a card is not found (404)."""


class RateLimitExceededError(PokemonTCGClientError):
    """Raised when rate limit retries are exhausted."""


class PokemonTCGClient:
    """Async client for the Pokémon TCG API.

    Reads configuration from environment variables:
    - POKEMON_TCG_BASE_URL: API base URL (default: https://api.pokemontcg.io/v2)
    - POKEMON_TCG_API_KEY: Optional API key for authenticated requests.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = (
            base_url
            or os.getenv("POKEMON_TCG_BASE_URL")
            or DEFAULT_BASE_URL
        )
        self._api_key = api_key or os.getenv("POKEMON_TCG_API_KEY")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        return headers

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._build_headers(),
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "PokemonTCGClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Execute an HTTP request with exponential backoff on 429 and 5xx."""
        client = await self._ensure_client()
        backoff = INITIAL_BACKOFF

        for attempt in range(MAX_RETRIES):
            response = await client.request(method, url, **kwargs)

            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    raise RateLimitExceededError(
                        f"Rate limit exceeded after {MAX_RETRIES} retries"
                    )
                retry_after = response.headers.get("Retry-After")
                wait_time = float(retry_after) if retry_after else backoff
                await asyncio.sleep(wait_time)
                backoff *= 2
                continue

            if response.status_code >= 500:
                if attempt == MAX_RETRIES - 1:
                    response.raise_for_status()
                await asyncio.sleep(backoff)
                backoff *= 2
                continue

            return response

        return response  # pragma: no cover

    async def get_card(self, card_id: str) -> dict[str, Any]:
        """Fetch a single card by its ID.

        Args:
            card_id: The card identifier (e.g. "base1-58").

        Returns:
            Card data dictionary.

        Raises:
            CardNotFoundError: If the card does not exist.
            RateLimitExceededError: If rate limit retries are exhausted.
        """
        response = await self._request_with_retry("GET", f"/cards/{card_id}")

        if response.status_code == 404:
            raise CardNotFoundError(f"Card not found: {card_id}")

        response.raise_for_status()
        return response.json().get("data", {})

    async def search_cards(self, query: str) -> list[dict[str, Any]]:
        """Search for cards matching a query string.

        Args:
            query: Search query (e.g. "name:pikachu").

        Returns:
            List of card data dictionaries.

        Raises:
            RateLimitExceededError: If rate limit retries are exhausted.
        """
        response = await self._request_with_retry(
            "GET", "/cards", params={"q": query}
        )

        response.raise_for_status()
        return response.json().get("data", [])
