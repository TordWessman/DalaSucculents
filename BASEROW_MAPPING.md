# Baserow → Web Schema Field Mapping

## Source Tables

| Table | Baserow ID | Rows | Description |
|---|---|---|---|
| Plant index | 746875 | 150 | Plant taxa with cultivation & conservation data |
| Genus | 747169 | 54 | Genus → Family lookup |
| Plant collection | 748062 | 191 | Individual specimens (seedlings, cuttings, etc.) |
| Country | 753691 | 249 | ISO 3166 country codes |

## Plant Index (746875) → `plants`

| Baserow Field | Field ID | Type | Web Column | Notes |
|---|---|---|---|---|
| Name | 6297762 | formula | — (computed) | Derived from genus+species+infrarank. Not stored directly. |
| ID | 6995221 | text | `baserow_id` | Custom ID like "0001" |
| ID__auto | 6297763 | autonumber | — | Internal Baserow ID, not used |
| Species | 6300262 | text | `species` | |
| Subspecies | 6300742 | text | `subspecies` | |
| Variety | 6300796 | text | `variety` | |
| Form | 6300798 | text | `form` | |
| Cultivar | 6300802 | text | `cultivar` | |
| Genus | 6313656 | link_row→747169 | `genus_id` FK | Resolved to genus name |
| Family | 6319244 | lookup | — | Derived via genus, stored on `genera` table |
| Field number | 6331303 | text | `field_number` | Collector field number (e.g., "AL 272") |
| Field location | 6331304 | text | `field_location` | Locality (e.g., "El Refugio, NL") |
| Plant collection | 6340534 | link_row→748062 | — | Reverse: specimens link back to plant |
| Vegetation period | 6297766 | single_select | `vegetation_period` | Summer \| Winter |
| Substrate | 6360415 | single_select | `substrate` | 3 options |
| Winter rest temp | 6360425 | single_select | `winter_temp_range` | 7 options |
| Watering | 6376724 | single_select | `watering` | Emoji scale (1-3 drops) |
| Exposure | 6410605 | single_select | `exposure` | 4 options |
| Red List Assessment | 6360427 | single_select | `red_list_status` | 9 IUCN categories |
| Red List Link | 6360459 | url | `red_list_url` | |
| LLIFLE Link | 6360469 | url | `llifle_url` | |
| CITES listing | 6360475 | single_select | `cites_listing` | None/Appendix I/II/III |
| Author citation | 6361735 | text | `author_citation` | Taxonomic authority |
| Native to country | 6365077 | link_row→753691 | `plant_countries` M2M | Multiple countries per plant |
| Notes | 6457140 | long_text | `notes` | |

## Genus (747169) → `genera`

| Baserow Field | Field ID | Type | Web Column | Notes |
|---|---|---|---|---|
| Genus | 6300340 | single_select | `name` | |
| Family | 6301600 | single_select | `family` | Stored directly, not normalized further |
| Plant list | 6319241 | link_row→746875 | — | Reverse relation |

## Plant Collection (748062) → `specimens`

| Baserow Field | Field ID | Type | Web Column | Notes |
|---|---|---|---|---|
| Specimen ID | 6308470 | formula | `specimen_code` | e.g., "0001-26s01" |
| Notes | 6308471 | long_text | `notes` | |
| For sale | 6308472 | boolean | `for_sale` | Currently all false |
| Name | 6308515 | link_row→746875 | `plant_id` FK | Links specimen to plant taxon |
| Propagation date | 6308673 | date | `propagation_date` | |
| Propagation method | 6309007 | single_select | `propagation_method` | Seed/Cutting/etc. |
| Specimen origin | 6309023 | single_select | `specimen_origin` | Country code of specimen |
| Source material origin | 6309031 | single_select | `source_material_origin` | Country code of source |
| Provenance | 6309034 | text | `provenance` | Source name (e.g., "Kaktus Köhres") |
| Specimen suffix | 6319584 | text | `specimen_suffix` | e.g., "01" |
| Image | 6341815 | file | — | Currently empty. Will use placeholder. |

## Country (753691) → `countries`

| Baserow Field | Field ID | Type | Web Column | Notes |
|---|---|---|---|---|
| English short name | 6365193 | text | `name` | |
| Alpha-2 code | 6365194 | text | `alpha2` | |
| Alpha-3 code | 6365195 | text | `alpha3` | PK in web schema |
| Numeric | 6365196 | text | `numeric_code` | |

## Single-Select Option Values

### Vegetation period
- Summer
- Winter

### Substrate
- 100% mineral-based
- Some organic component
- Humus-rich succulent mix

### Winter rest temperature range
- [Winter grower]
- \>15 °C
- 10-15 °C
- 5-10 °C
- 1-5 °C
- Frost-tolerant (dry)
- Winter-hardy (outdoors protected)

### Watering (growing season)
- 💧 (low)
- 💧💧 (moderate)
- 💧💧💧 (regular)

### Exposure
- Full sun
- Full sun to partial shade
- Partial shade
- Tolerates shade

### Red List Assessment (IUCN)
- Not evaluated (NE)
- Data deficient (DD)
- Least concern (LC)
- Near threatened (NT)
- Vulnerable (VU)
- Endangered (EN)
- Critically endangered (CR)
- Extinct in the wild (EW)
- Extinct (EX)

### CITES listing
- None
- Appendix III
- Appendix II
- Appendix I

### Propagation method
- Seed
- (others TBD from full data)

### Specimen origin / Source material origin
- SE, DE (country codes)
- (others TBD from full data)

## Slug Generation Strategy

Slugs are generated from the full botanical name:
- `{genus}-{species}` as base
- Append infraspecific rank if present: `-ssp-{subspecies}`, `-var-{variety}`, `-f-{form}`
- Append cultivar if present: `-{cultivar}` (strip quotes)
- Append field number if present: `-{field_number}` (lowercase, replace spaces with hyphens)
- Append field location if present: `-{location}` (lowercase, strip parens, replace spaces)
- Lowercase, replace spaces with hyphens, remove special characters
- Example: "Ariocarpus retusus AL 272 (El Refugio, NL)" → `ariocarpus-retusus-al-272-el-refugio-nl`
