"""
Rate Limiter Module

Token bucket rate limiter for API calls.
"""

import asyncio
import time
from typing import Dict


class RateLimiter:
    """
    Token bucket rate limiter.

    Limits requests to a maximum rate per second.
    """

    def __init__(self, rate: float = 1.0, burst: int = 1):
        """
        Initialize rate limiter.

        Args:
            rate: Maximum requests per second
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire a rate limit token.

        Blocks until a token is available.
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class MultiRateLimiter:
    """
    Rate limiter for multiple providers.

    Maintains separate rate limits per provider.
    """

    def __init__(self):
        """Initialize multi rate limiter."""
        self._limiters: Dict[str, RateLimiter] = {}

    def register(self, provider: str, rate: float, burst: int = 1) -> None:
        """
        Register a provider with its rate limit.

        Args:
            provider: Provider name
            rate: Requests per second
            burst: Burst size
        """
        self._limiters[provider] = RateLimiter(rate, burst)

    async def acquire(self, provider: str) -> None:
        """
        Acquire a token for a provider.

        Args:
            provider: Provider name
        """
        if provider in self._limiters:
            await self._limiters[provider].acquire()
