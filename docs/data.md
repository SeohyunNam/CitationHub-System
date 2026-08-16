# IDCite data layer

CitationHub does not collect bibliographic records at request time. It reads **IDCite**, released as 17 Apache Parquet files. The inventory below follows *IDCite: Project and Dataset Documentation* (Version 3).

## Public locations

| Resource | Location |
|---|---|
| Official archived release (Zenodo, Version 3) | [https://doi.org/10.5281/zenodo.20796923](https://doi.org/10.5281/zenodo.20796923) |
| Processed dataset and graph files (Hugging Face) | [https://huggingface.co/datasets/Daniel0315/IDCite](https://huggingface.co/datasets/Daniel0315/IDCite) |
| Construction pipeline | [https://github.com/SeohyunNam/MDCite](https://github.com/SeohyunNam/MDCite) |
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
| `affiliation_geo.parquet` | 5,352 | 6 | Affiliation, city, and country mappings (including coordinates for the map) |
| `journals.parquet` | 46,237 | 2 | Journal ID–name mapping |
| `fields.parquet` | 21 | 3 | Field ID–name mapping |
| `intents.parquet` | 31 | 2 | Citation-intent ID–name mapping |
| `cities.parquet` | 1,899 | 2 | City ID–name mapping |
| `countries.parquet` | 108 | 2 | Country ID–name mapping |

## What CitationHub reads at runtime

The live interface uses a working subset:

| File | Used for |
|---|---|
| `seed_cited_papers_normalized.parquet` | Paper search, paper detail, author aggregation |
| `citation_events_normalized.parquet` | Citing lists, intents, analytics, citation network |
| `authors.parquet` | Author names and author search |
| `affiliation_geo.parquet` | Geographic Map |
| `kg_nodes.parquet` | Knowledge Graph explorer |
| `kg_edges.parquet` | RDF conversion for SPARQL |

The other files belong to the public IDCite release (lookups, unnormalized tables, enriched events) and support dataset reuse outside the website.

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
