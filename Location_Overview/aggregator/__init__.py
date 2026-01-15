"""Data aggregation engine for parallel provider execution."""

from .engine import AggregationEngine
from .merger import ResultMerger
from .validator import CompletenessValidator

__all__ = ["AggregationEngine", "ResultMerger", "CompletenessValidator"]
