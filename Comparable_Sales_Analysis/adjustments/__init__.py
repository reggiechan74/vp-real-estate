"""
Comparable Sales Adjustment Modules

This package provides modular adjustment calculations for the 6-stage
comparable sales adjustment methodology:

Stage 6: Physical Characteristics (49 subcategories across 7 modules)
- Land characteristics (8 adjustments)
- Site improvements (6 adjustments)
- Industrial building (10 adjustments)
- Office building (8 adjustments)
- Building general (6 adjustments)
- Special features (6 adjustments)
- Zoning/legal (5 adjustments)

CUSPAP 2024 & USPAP 2024 Compliant
"""

# Explicit imports for clean API
from . import land
from . import site
from . import industrial_building
from . import office_building
from . import building_general
from . import special_features
from . import zoning_legal
from . import validation

# Public API
__all__ = [
    'land',
    'site',
    'industrial_building',
    'office_building',
    'building_general',
    'special_features',
    'zoning_legal',
    'validation',
]

# Module metadata
__version__ = '1.0.1'
__author__ = 'Claude Code'
