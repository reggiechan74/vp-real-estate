# Location Overview Module

Generate comprehensive location overviews for Ontario properties, suitable for inclusion in CUSPAP-compliant appraisal reports.

## Features

- **Dual Input Support**: Accept 9-digit Ontario PIN or municipal address
- **Multi-Source Integration**: Query multiple free APIs for comprehensive data
- **Provincial Plan Detection**: Identify Greenbelt, Growth Plan, Oak Ridges Moraine overlays
- **Zoning Analysis**: Retrieve zoning designation, permitted uses, and Official Plan policies
- **Neighbourhood Analysis**: Compile amenities, transit accessibility, surrounding uses
- **CUSPAP Compliance**: Output formatted per appraisal report standards

## Quick Start

### Command Line

```bash
# Generate location overview for an address
python -m Location_Overview.main "100 Queen Street West, Toronto"

# Generate JSON output
python -m Location_Overview.main --format json "150 King Street West, Toronto"

# Verbose output
python -m Location_Overview.main -v "200 University Avenue, Toronto"
```

### Slash Command

```
/location-overview 100 Queen Street West, Toronto
```

### Python API

```python
import asyncio
from Location_Overview.main import location_overview

async def main():
    result = await location_overview("100 Queen Street West, Toronto")

    if result.success:
        print(f"Report saved to: {result.report_path}")
        print(f"Zoning: {result.summary['zoning']}")
        print(f"Greenbelt: {result.summary['greenbelt']}")
    else:
        print(f"Error: {result.error}")

asyncio.run(main())
```

## Installation

```bash
# Install dependencies
pip install -r Location_Overview/requirements.txt
```

## Data Sources (Phase 1 MVP)

| Source | Type | Data Retrieved | Cost |
|--------|------|----------------|------|
| **Nominatim** | Free API | Geocoding (address → coordinates) | $0 |
| **Ontario GeoHub** | Free API | Provincial plans (Greenbelt, Growth Plan, ORM) | $0 |
| **Toronto Open Data** | Free API | Zoning, neighbourhoods, wards | $0 |
| **Overpass API** | Free API | Amenities from OpenStreetMap | $0 |

## Output

The generated report includes:

1. **Property Identification**: Address, coordinates, municipality, ward, neighbourhood
2. **Regional Context**: Description of the municipality and area
3. **Planning Framework**:
   - Official Plan designation
   - Zoning (designation, category, permitted uses)
   - Secondary plan (if applicable)
   - Provincial plan overlays
4. **Transportation & Access**: Transit accessibility, rapid transit proximity
5. **Neighbourhood Description**: Character, amenities, walkability
6. **Environmental Factors**: Constraints and servicing status
7. **Data Sources**: Full attribution and timestamps

## Module Structure

```
Location_Overview/
├── main.py                 # Entry point and orchestration
├── config.py               # Configuration management
├── input/                  # Input parsing and validation
│   ├── parser.py          # PIN/address detection
│   ├── normalizer.py      # Address standardization
│   └── municipality_detector.py
├── geocoding/              # Address → coordinates
│   ├── nominatim.py       # OpenStreetMap Nominatim
│   └── cache.py           # Geocoding cache
├── providers/              # Data source integrations
│   ├── base.py            # Abstract provider class
│   ├── ontario_geohub.py  # Provincial plans
│   ├── toronto_opendata.py # Toronto zoning/planning
│   └── overpass.py        # OSM amenities
├── aggregator/             # Result merging
│   ├── engine.py          # Parallel execution
│   ├── merger.py          # Result combination
│   └── validator.py       # Completeness checks
├── output/                 # Report generation
│   ├── formatter.py       # Markdown/JSON output
│   └── templates/         # Jinja2 templates
├── schemas/                # Data models
│   └── location_data.py   # LocationOverview dataclass
└── tests/                  # Test suite
```

## Configuration

Configuration via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LO_NOMINATIM_USER_AGENT` | Nominatim User-Agent | `LocationOverview/1.0` |
| `LO_CACHE_ENABLED` | Enable caching | `true` |
| `LO_CACHE_DIRECTORY` | Cache directory | `.cache/location_overview` |
| `LO_REPORTS_DIRECTORY` | Output directory | `Reports` |
| `LO_DEBUG` | Debug mode | `false` |

## Rate Limits

| API | Rate Limit | Notes |
|-----|------------|-------|
| Nominatim | 1 req/sec | Free tier policy |
| Ontario GeoHub | 5 req/sec | Conservative estimate |
| Toronto Open Data | 10 req/sec | Generous |
| Overpass API | 1 req/sec | Conservative |

## Limitations (Phase 1)

1. **PIN Lookup**: Requires OnLand/Teranet (Phase 3)
2. **Environmental Screening**: TRCA, Brownfields ESR in Phase 2
3. **Assessment Data**: MPAC requires paid subscription (Phase 3)
4. **Demographics**: CensusMapper integration in Phase 2

## Testing

```bash
# Run tests
pytest Location_Overview/tests/

# Run with coverage
pytest Location_Overview/tests/ --cov=Location_Overview

# Run specific test file
pytest Location_Overview/tests/unit/test_parser.py -v
```

## Phase Roadmap

| Phase | Features | Cost |
|-------|----------|------|
| **Phase 1 (MVP)** | Geocoding, provincial plans, zoning, amenities | $0/month |
| **Phase 2** | Ottawa/GTA municipalities, TRCA, heritage, transit | ~$100/month |
| **Phase 3** | MPAC assessment, Teranet PIN lookup, demographics | ~$35/lookup |

## License

Part of the Lease Abstract Toolkit. See main repository LICENSE.

## See Also

- [Implementation Plan](../Planning/location-overview-implementation-plan.md)
- [Slash Command](../.claude/commands/Infrastructure/location-overview.md)
