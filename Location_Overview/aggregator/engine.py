"""
Aggregation Engine Module

Coordinates parallel execution of data providers and aggregates results.
Handles timeouts, errors, and graceful degradation.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ..providers.base import BaseProvider, ProviderResult, ProviderStatus


logger = logging.getLogger(__name__)


@dataclass
class AggregationResult:
    """Result from the aggregation engine."""

    data: Dict[str, Any]
    providers_succeeded: List[str]
    providers_failed: List[str]
    warnings: List[str]
    errors: List[str]
    total_time_ms: float


class AggregationEngine:
    """
    Coordinates parallel execution of data providers.

    Features:
    - Parallel provider execution
    - Per-provider timeouts
    - Graceful degradation on failures
    - Result merging
    """

    DEFAULT_TIMEOUT = 30.0  # seconds

    def __init__(
        self,
        providers: Optional[List[BaseProvider]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize aggregation engine.

        Args:
            providers: List of data providers
            timeout: Default per-provider timeout
        """
        self.providers = providers or []
        self.timeout = timeout

    def register_provider(self, provider: BaseProvider) -> None:
        """
        Register a data provider.

        Args:
            provider: Provider instance
        """
        self.providers.append(provider)

    def get_applicable_providers(self, municipality: str) -> List[BaseProvider]:
        """
        Get providers applicable to a municipality.

        Args:
            municipality: Municipality name

        Returns:
            List of applicable providers
        """
        return [p for p in self.providers if p.is_applicable(municipality)]

    async def execute(
        self,
        lat: float,
        lon: float,
        municipality: str,
        **kwargs,
    ) -> AggregationResult:
        """
        Execute all applicable providers in parallel.

        Args:
            lat: Latitude
            lon: Longitude
            municipality: Municipality name
            **kwargs: Additional parameters for providers

        Returns:
            AggregationResult with merged data
        """
        import time

        start_time = time.time()

        # Get applicable providers
        providers = self.get_applicable_providers(municipality)

        if not providers:
            return AggregationResult(
                data={},
                providers_succeeded=[],
                providers_failed=[],
                warnings=["No applicable providers for municipality"],
                errors=[],
                total_time_ms=0.0,
            )

        # Create tasks for parallel execution
        tasks = []
        provider_names = []

        for provider in providers:
            task = asyncio.wait_for(
                provider.query(lat, lon, **kwargs),
                timeout=self.timeout,
            )
            tasks.append(task)
            provider_names.append(provider.name)

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        data = {}
        providers_succeeded = []
        providers_failed = []
        warnings = []
        errors = []

        for provider_name, result in zip(provider_names, results):
            if isinstance(result, asyncio.TimeoutError):
                providers_failed.append(provider_name)
                errors.append(f"{provider_name}: Timeout after {self.timeout}s")
                logger.warning(f"Provider {provider_name} timed out")
                continue

            if isinstance(result, Exception):
                providers_failed.append(provider_name)
                errors.append(f"{provider_name}: {str(result)}")
                logger.error(f"Provider {provider_name} failed: {result}")
                continue

            # result is a ProviderResult
            if result.success:
                providers_succeeded.append(provider_name)
                data[provider_name] = result.data

                # Collect warnings
                if result.warnings:
                    warnings.extend(
                        [f"{provider_name}: {w}" for w in result.warnings]
                    )

                logger.info(
                    f"Provider {provider_name} succeeded "
                    f"(cached={result.cached}, time={result.response_time_ms:.0f}ms)"
                )
            else:
                providers_failed.append(provider_name)
                if result.error:
                    errors.append(f"{provider_name}: {result.error}")
                logger.warning(f"Provider {provider_name} failed: {result.error}")

        total_time = (time.time() - start_time) * 1000

        return AggregationResult(
            data=data,
            providers_succeeded=providers_succeeded,
            providers_failed=providers_failed,
            warnings=warnings,
            errors=errors,
            total_time_ms=total_time,
        )

    async def execute_provider(
        self,
        provider: BaseProvider,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Execute a single provider with timeout handling.

        Args:
            provider: Provider to execute
            lat: Latitude
            lon: Longitude
            **kwargs: Additional parameters

        Returns:
            ProviderResult
        """
        try:
            return await asyncio.wait_for(
                provider.query(lat, lon, **kwargs),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            return ProviderResult(
                source=provider.name,
                success=False,
                data=None,
                error=f"Timeout after {self.timeout}s",
                status=ProviderStatus.TIMEOUT,
            )
        except Exception as e:
            return ProviderResult(
                source=provider.name,
                success=False,
                data=None,
                error=str(e),
                status=ProviderStatus.FAILED,
            )
