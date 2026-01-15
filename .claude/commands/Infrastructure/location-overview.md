# Location Overview Slash Command

Generate a **narrative-format location overview** for an Ontario property address or PIN, combining API data with deep web research into prose suitable for direct inclusion in an appraisal report.

## Usage

```
/location-overview <address|PIN> [--quick]
```

## Examples

```
/location-overview 100 Queen Street West, Toronto
/location-overview 7 Summerland Terrace, Etobicoke
/location-overview 7 Summerland Terrace, Etobicoke --quick
```

## Parameters

- `<address|PIN>`: Either a municipal address or 9-digit Ontario PIN
- `--quick`: Skip deep web research, use API data only (faster, less comprehensive)

## Prompt

You are generating a **narrative-format location overview** for the property at: $ARGUMENTS

The output must be written in **flowing prose** (not tables or bullet points) suitable for direct copy-paste into a CUSPAP-compliant appraisal report. Synthesize API data and web research findings into professional narrative paragraphs that read like an appraisal location description.

## Instructions

### Phase 1: API Data Collection

1. **Parse the input** to determine if it's an address or PIN:
   - PIN: 9 consecutive digits (e.g., 123456789 or 12345-6789)
   - Address: Municipal address with optional municipality

2. **Run the Location Overview module** to collect API data:
   ```bash
   cd /workspaces/lease-abstract
   python -m Location_Overview.main "$ARGUMENTS"
   ```

3. **Read the generated report** to get the base data including:
   - Coordinates and municipality
   - Zoning and planning designations
   - Environmental constraints
   - Amenities and transit data

### Phase 2: Deep Web Research (Skip if --quick)

After running the API module, conduct deep web research using WebSearch and WebFetch to supplement the data:

#### 2.1 Municipal Planning Research

Use **WebSearch** to find:
```
"[address]" site:toronto.ca planning application
"[address]" site:toronto.ca development
"[address]" site:ottawa.ca planning
"[address]" zoning amendment OR minor variance
"[address]" site plan approval
```

Then use **WebFetch** on relevant results to extract:
- Active or recent planning applications
- Committee of Adjustment decisions
- Site Plan Approval status
- Development permit status

#### 2.2 Heritage Research

Use **WebSearch** to find:
```
"[address]" heritage designation Ontario
"[address]" site:heritagetrust.on.ca
"[address]" heritage conservation district
"[neighbourhood name]" heritage character area
```

Extract:
- Heritage register listings
- Heritage impact assessments
- Heritage Conservation District studies

#### 2.3 Environmental Research

Use **WebSearch** to find:
```
"[address]" environmental site assessment
"[address]" record of site condition
"[address]" site:trca.ca OR site:cvc.ca
"[address]" contamination OR remediation
```

Extract:
- Conservation authority permits
- Environmental assessments
- Contamination history

#### 2.4 Development Activity Research

Use **WebSearch** to find:
```
"[address]" construction OR development OR redevelopment
"[address]" site:urbantoronto.ca OR site:skyrisecities.com
"[neighbourhood]" development pipeline [current year]
"[address]" building permit
```

Extract:
- Recent or proposed developments
- Building permit activity
- Neighbourhood development trends

#### 2.5 Market Context Research

Use **WebSearch** to find:
```
"[neighbourhood]" real estate market [current year]
"[neighbourhood]" property values trends
"[address]" recent sale OR sold
```

Extract:
- Market trends and context
- Notable transactions
- Neighbourhood market dynamics

### Phase 3: Narrative Synthesis

After completing API data collection and web research, **synthesize all findings into a narrative location overview** suitable for direct inclusion in an appraisal report. The narrative should:

1. **Read the API-generated report** to extract structured data
2. **Combine with web research findings** into flowing prose
3. **Write a narrative report** following CUSPAP location description standards

### Phase 4: Narrative Output Format

**CRITICAL**: The final output must be in **narrative prose format**, not tables or bullet points. Generate a location overview that reads like a professional appraisal report section.

**Structure the narrative as follows:**

#### 1. Property Identification (1 paragraph)
Open with the civic address, legal description (if available), and geographic coordinates. Include municipality, ward, and neighbourhood identification.

#### 2. Regional Context (1-2 paragraphs)
Describe the broader regional setting - the municipality's role in the GTA/province, population, economic character, and the subject's position within it.

#### 3. Neighbourhood Description (2-3 paragraphs)
Describe the immediate neighbourhood character, land use mix, building typology, and streetscape. Include specific observations from web research about the building/development (name, developer, year built, style). Reference the Secondary Plan area if applicable.

#### 4. Transportation & Accessibility (1-2 paragraphs)
Describe transit connectivity (subway, bus, GO Transit), major road access, and walkability. Quantify distances to key transit nodes. Mention cycling infrastructure if relevant.

#### 5. Amenities & Services (1-2 paragraphs)
Describe proximity to schools, shopping, healthcare, recreation, and employment centres. Reference specific amenities by name and distance where impactful.

#### 6. Planning Framework (2-3 paragraphs)
Describe the Official Plan designation, zoning, and any Secondary Plan policies. Explain what development is permitted and any restrictions. Include Provincial Plan status (Greenbelt, Growth Plan, etc.).

#### 7. Development Activity (1-2 paragraphs)
Describe recent, ongoing, and proposed development in the area. Reference specific projects by name, scale, and status. Note neighbourhood trends (intensification, stability, decline).

#### 8. Environmental Considerations (1 paragraph)
Address floodplain status, conservation authority jurisdiction, heritage designations, and brownfield/contamination status. Note any environmental constraints or clearances.

#### 9. Market Context (1 paragraph)
Provide brief market positioning - comparable values, market trends, and factors driving demand in the area.

#### 10. Conclusion (1 paragraph)
Summarize the location's strengths and any limitations relevant to value or marketability.

**Save the narrative to**: `Reports/[timestamp]_location_overview_narrative_[address_slug].md`

**Present to user**:
1. The full narrative text (display in chat)
2. Path to saved file
3. Data sources used
4. Recommendations for verification

## Deep Research Queries by Municipality

### Toronto
- Planning: `site:toronto.ca/city-government/planning-development`
- Applications: `site:app.toronto.ca/DevelopmentApplications`
- Heritage: `site:toronto.ca/explore-enjoy/history-art-culture/heritage-toronto`

### Ottawa
- Planning: `site:ottawa.ca/en/planning-development-and-construction`
- Applications: `site:devapps.ottawa.ca`
- Heritage: `site:ottawa.ca/heritage`

### Mississauga
- Planning: `site:mississauga.ca/services-and-programs/building-and-renovating/planning-and-development`

### Other Municipalities
- Use general searches with municipality name + "planning department"
- Check if municipality has online development tracker

## Output Format

The final output is a **narrative prose document** suitable for direct inclusion in an appraisal report. It synthesizes:

### Data Sources Used
- **API Providers**: Nominatim, Ontario GeoHub, Toronto/Ottawa Open Data, Overpass API, Heritage Registry, Brownfields ESR, TRCA Conservation, Transit GTFS, Census Demographics
- **Web Research**: Municipal planning portals, Heritage Trust Ontario, Conservation authority websites, Development news (UrbanToronto, Skyrise Cities), Real estate market reports

## Example Narrative Output

```markdown
# Location Overview

**Property:** 7 Summerland Terrace, Etobicoke, Ontario M9A 0B6

## Property Identification

The subject property is located at 7 Summerland Terrace in the Etobicoke City Centre neighbourhood of Toronto, Ontario. The property is situated within Ward 03 (Etobicoke-Lakeshore) at geographic coordinates 43.643485°N, 79.531954°W. The site is positioned within one of Etobicoke's designated Urban Growth Centres, approximately 15 kilometres west of downtown Toronto.

## Regional Context

Toronto is Ontario's capital city and Canada's largest municipality, with a population of approximately 2.9 million residents according to the 2021 Census. The city serves as the economic centre of Canada and the Greater Toronto Area (GTA), characterized by diverse neighbourhoods, extensive transit infrastructure, and a dynamic mix of residential, commercial, and employment uses. The subject property is located in the western portion of the city within the former municipality of Etobicoke, which amalgamated with Toronto in 1998.

## Neighbourhood Description

The subject property is a residential condominium unit within Sierra at Village Gate West, a 21-storey high-rise tower developed by Concert Properties circa 2009-2010. The building contains 218 units and features a modern architectural style with a podium base. Sierra forms part of the larger Village Gate West master-planned community situated at the intersection of Bloor Street West/Dundas Street West and Islington Avenue.

The Etobicoke City Centre neighbourhood is characterized by a mix of high-rise residential towers, low-rise commercial development along major arterials, and established residential subdivisions. The area has undergone significant transformation over the past two decades from a suburban commercial district to an emerging urban centre, driven by its designation as an Urban Growth Centre under the Provincial Growth Plan and excellent transit accessibility.

The immediate surroundings include mid-rise and high-rise residential buildings to the north and east, commercial retail along Dundas Street to the south, and the Village Gate West development to the west. The streetscape reflects a transitional urban character with wide arterial roads, surface parking, and pedestrian-oriented improvements associated with recent development.

## Transportation & Accessibility

The property benefits from excellent transit connectivity. The Islington TTC subway station on Line 2 (Bloor-Danforth) is located approximately 600 metres to the southeast, providing direct rapid transit access to downtown Toronto and connections to the broader subway network. Multiple TTC bus routes serve the immediate area, including the 37 Islington and 50 Burnhamthorpe routes, with stops within 150 metres of the subject.

Regional transit connections are available at Kipling Station, approximately 1.5 kilometres to the west, which serves as a multi-modal hub offering GO Transit service on the Milton and Kitchener lines, as well as connections to Mississauga's MiWay transit system. The property is also accessible by automobile via Dundas Street West and the nearby Highway 427 interchange.

## Amenities & Services

The subject property is well-served by neighbourhood amenities. Islington Junior Middle School is located approximately 514 metres to the north, while additional educational facilities are available throughout the area. Shopping and daily conveniences are accessible within walking distance, with Hasty Market located 136 metres away and larger retail options along Dundas Street. Healthcare services include the Dunbloor Medical Clinic (116 metres) and Dunbloor Pharmacy (123 metres). Recreational amenities include F45 Training (159 metres) and numerous parks and open spaces within the broader neighbourhood.

## Planning Framework

The property is located within the Etobicoke Centre Secondary Plan area, which establishes a planning framework for intensification around the Islington and Kipling transit nodes. The Secondary Plan targets a density of 400 people and jobs per hectare and permits Floor Space Index (FSI) of up to 5.0 in designated areas. Key policy directions include high-density mixed-use development along Dundas Street and Bloor Street, enhanced pedestrian and cycling connections, and integration with rapid transit infrastructure.

The property is located outside of Provincial Plan areas including the Greenbelt Plan, Oak Ridges Moraine Conservation Plan, and Niagara Escarpment Plan. The site falls within the Greater Golden Horseshoe Growth Plan area, which designates Etobicoke Centre as an Urban Growth Centre requiring minimum density targets and transit-supportive development.

## Development Activity

The surrounding area is experiencing significant development activity. The $480 million Etobicoke Civic Centre redevelopment is currently under construction at the Dundas Street/Kipling Avenue intersection, representing a major civic investment in the area. The Bloor-Kipling Master Plan has received approval for over 2,700 residential units around the Kipling transit hub, with construction expected to proceed in phases over the coming years. Additional residential towers within the Village Gate West development have been completed, contributing to the ongoing intensification of the area.

## Environmental Considerations

The property is not located within a regulated floodplain or other environmental constraint area. The site falls within the jurisdiction of the Toronto and Region Conservation Authority (TRCA) but is outside of regulated areas requiring development permits. No Record of Site Condition (RSC) is on file with the Ministry of Environment, Conservation and Parks, indicating no known contamination issues. No heritage designations apply to the property or the immediate surrounding area.

## Market Context

The Etobicoke City Centre area has experienced steady appreciation in condominium values, driven by proximity to rapid transit, major civic investment, ongoing intensification per the Secondary Plan, and employment growth in the area. Comparable condominium sales in the Village Gate West complex and surrounding developments suggest values in the range of $650 to $850 per square foot for units in buildings of similar vintage and quality.

## Conclusion

The subject property benefits from an excellent location within an emerging Urban Growth Centre supported by strong transit connectivity, comprehensive neighbourhood amenities, and a favourable planning framework that encourages continued development and intensification. The property has no significant environmental constraints or heritage restrictions. The primary limitation is the transitional character of the immediate streetscape, which retains some suburban commercial elements despite ongoing urbanization. Overall, the location is considered desirable for residential use and supportive of condominium values.

---

*Generated: December 17, 2025*
*Data Sources: Ontario GeoHub, Toronto Open Data, Overpass API, Heritage Registry, Brownfields ESR, TRCA Conservation, Transit GTFS, Census Demographics, GTA-Homes, City of Toronto Planning, UrbanToronto*
```

## Limitations

1. **PIN lookup** requires OnLand/Teranet integration (Phase 3)
2. **Assessment data** (MPAC) requires paid subscription (Phase 3)
3. **Web research** depends on publicly available information
4. **Planning application status** may be outdated - verify with municipality

## See Also

- Implementation plan: `Planning/location-overview-implementation-plan.md`
- Module documentation: `Location_Overview/README.md`
