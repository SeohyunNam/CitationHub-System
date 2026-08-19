# IDCite data layer

CitationHub does not collect bibliographic records at request time. It reads **IDCite**, released as 17 Apache Parquet files. The inventory below follows *IDCite: Project and Dataset Documentation* (Version 3).

## Public locations

| Resource | Location |
|---|---|
| Official archived release (Zenodo, Version 3) | [https://doi.org/10.5281/zenodo.20796923](https://doi.org/10.5281/zenodo.20796923) |
| Processed dataset and graph files (Hugging Face) | [https://huggingface.co/datasets/Daniel0315/IDCite](https://huggingface.co/datasets/Daniel0315/IDCite) |
| Dataset Construction pipeline | [https://github.com/SeohyunNam/MDCite](https://github.com/SeohyunNam/MDCite) |
| Concept DOI (all versions) | [https://doi.org/10.5281/zenodo.18410049](https://doi.org/10.5281/zenodo.18410049) |

Earlier Zenodo versions remain available for provenance: Version 1 (MDCite) and Version 2 (MDContextCite / EdgeCite). CitationHub is not a Zenodo dataset version; it is the interactive system on top of IDCite.

## File inventory

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `citation_events.parquet` | 1,857,503 | 20 | Raw citation-event records |
| `citation_events_enriched.parquet` | 1,857,503 | 32 | Events enriched with cited seed-paper metadata |
| `citation_events_normalized.parquet` | 1,857,503 | 23 | Events with normalized intent and field identifiers |
| `citing_papers.parquet` | 1,467,045 | 7 | Citing-paper metadata |
| `citing_papers_normalized.parquet` | 1,467,045 | 8 | Citing papers with normalized journal IDs |
| `seed_cited_papers.parquet` | 23,479 | 42 | Highly cited seed-paper metadata |
| `seed_cited_papers_normalized.parquet` | 23,479 | 48 | Seed papers with normalized journal, author, affiliation, city, country, and field IDs |
| `kg_nodes.parquet` | 3,418,433 | 14 | Knowledge-graph nodes |
| `kg_edges.parquet` | 6,855,117 | 3 | Typed knowledge-graph edges |
| `authors.parquet` | 16,839 | 2 | Author ID–name mapping |
| `affiliations.parquet` | 5,271 | 2 | Affiliation ID–name mapping |
| `affiliation_geo.parquet` | 5,352 | 6 | Affiliation, city, and country mappings — names and identifiers only, no coordinates |
| `journals.parquet` | 46,237 | 2 | Journal ID–name mapping |
| `fields.parquet` | 21 | 3 | Field ID–name mapping |
| `intents.parquet` | 31 | 2 | Citation-intent ID–name mapping |
| `cities.parquet` | 1,899 | 2 | City ID–name mapping |
| `countries.parquet` | 108 | 2 | Country ID–name mapping |

## What CitationHub reads at runtime

The live interface uses a working subset:

| File | Used for |
|---|---|
| `seed_cited_papers_normalized.parquet` | Paper search, paper detail, author aggregation, Geographic Map |
| `citation_events_normalized.parquet` | Citing lists, intents, analytics, citation network |
| `authors.parquet` | Author names and author search |
| `kg_nodes.parquet` | Knowledge Graph explorer |
| `kg_edges.parquet` | RDF conversion for SPARQL |

The other files belong to the public IDCite release (lookups, unnormalized tables, enriched events) and support dataset reuse outside the website. Geographic Map reads the city, country, and affiliation names already carried on normalized seed papers; it does not need the separate affiliation-geography table.

## Place coordinates

No table in IDCite records latitude or longitude — `affiliation_geo.parquet` maps affiliations to city and country **names** only. Coordinates are therefore not dataset content but a derived lookup that CitationHub maintains alongside the application:

| Property | Value |
|---|---|
| Source | [GeoNames](https://www.geonames.org) `cities500` gazetteer and ISO country table, licensed CC BY 4.0 |
| Granularity | One coordinate per (city, country) pair — 1,842 pairs resolved out of 1,935 present |
| Coverage | 99.3% of papers that record a city |
| When it runs | Ahead of time, regenerated when the seed table changes; never at request time |

Keeping the lookup outside IDCite means the dataset stays the record of what was published, geocoding can be improved without reissuing dataset versions, and one coordinate is stored per city instead of repeating it across 23,479 seed-paper rows. Affiliations reuse their city’s coordinate, as IDCite gives no finer location.

Home-page cards may show slightly different counts from the full release (for example, journals listed in filters versus the full journal lookup, or the seven canonical intents versus 31 observed labels). Treat the Parquet inventory as the dataset of record.

## Construction in brief

IDCite is built in [MDCite](https://github.com/SeohyunNam/MDCite) from Scopus bibliographic records, Web of Science / 2024 JCR journal grouping, OpenAlex citation links, Semantic Scholar citation contexts, and SynIntent citation-intent annotation. Journal-stratified sampling covers 21 ESI fields, 21 representative Web of Science categories, and 105 Q1 journals; the top 5% most-cited papers are kept independently within each journal (23,479 seed papers).

CitationHub starts **after** those 17 files exist: it indexes them for search, visualization, and SPARQL.

## Core citation-event fields

From `citation_events` / normalized variants:

- `citation_event_id`, `citing_paper_id`, `cited_seed_paper_id`
- citing DOI, title, year, venue
- `primary_intent`, `all_intents`, `contexts`, `context_count`
- `is_influential`, `has_semantic_evidence`, `field_id`

Seed papers additionally carry DOI, title, venue, creator, citation count, field/category, and journal identifiers.

## Knowledge graph tables

`kg_nodes.parquet` and `kg_edges.parquet` are a supplementary, ontology-ready graph: node types include SeedPaper, CitingPaper, CitationEvent, Intent, Journal, Author, Affiliation, City, Country, and Field. Edges encode citation linkage, intent assignment, authorship, affiliation, venue, geography, and disciplinary assignment. CitationHub converts these tables to RDF for SPARQL; the Parquet files remain the portable release format.
