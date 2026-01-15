"""
Async HTTP Client Module

HTTP client with retry logic, timeouts, and rate limiting support.
"""

import asyncio
from typing import Optional, Dict, Any
import httpx


class AsyncHttpClient:
    """
    Async HTTP client with configurable timeouts and retries.
    """

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 2
    DEFAULT_BACKOFF = 1.0

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff: float = DEFAULT_BACKOFF,
        user_agent: str = "LocationOverview/1.0",
    ):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            retries: Number of retries on failure
            backoff: Backoff multiplier between retries
            user_agent: User-Agent header value
        """
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.user_agent = user_agent

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make GET request with retry logic.

        Args:
            url: Request URL
            params: Query parameters
            headers: Additional headers

        Returns:
            Response object

        Raises:
            httpx.HTTPError: On request failure after retries
        """
        headers = headers or {}
        headers.setdefault("User-Agent", self.user_agent)

        last_error = None

        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                    )
                    response.raise_for_status()
                    return response

            except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
                last_error = e

                # Don't retry on 4xx errors (except 429)
                if isinstance(e, httpx.HTTPStatusError):
                    if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                        raise

                if attempt < self.retries:
                    wait_time = self.backoff * (2 ** attempt)
                    await asyncio.sleep(wait_time)

        raise last_error

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make POST request with retry logic.

        Args:
            url: Request URL
            data: Form data
            json: JSON data
            headers: Additional headers

        Returns:
            Response object
        """
        headers = headers or {}
        headers.setdefault("User-Agent", self.user_agent)

        last_error = None

        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        data=data,
                        json=json,
                        headers=headers,
                        timeout=self.timeout,
                    )
                    response.raise_for_status()
                    return response

            except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
                last_error = e

                if isinstance(e, httpx.HTTPStatusError):
                    if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                        raise

                if attempt < self.retries:
                    wait_time = self.backoff * (2 ** attempt)
                    await asyncio.sleep(wait_time)

        raise last_error
