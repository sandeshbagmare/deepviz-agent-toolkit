"""Bounded, schema-driven visualization contracts and normalization."""

from .models import Artifact, ChartSpec, NormalizedData
from .normalize import normalize

__all__ = ["Artifact", "ChartSpec", "NormalizedData", "normalize"]
