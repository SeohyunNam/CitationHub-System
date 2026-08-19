# System Architecture

CitationHub is a three-part application over IDCite: a web interface, an API that reads Parquet tables, and a SPARQL service over an RDF conversion of the knowledge graph.

This page describes **logical** structure. Hostnames, internal accounts, and operational runbooks are out of scope.

## Layers

```
Users
  └── Next.js frontend
        ├── search, author, and paper pages
        ├── analytics charts and geographic map
        ├── citation-network and knowledge-graph canvases
        └── SPARQL editor
              │
              │  JSON over HTTPS
              ▼
        FastAPI backend
              ├── overview / search / filters
              ├── paper and author detail
              ├── analytics and geo aggregations
              ├── per-paper knowledge-graph slices
              └── SPARQL proxy (read-only)
                    │
                    ├── Parquet (pandas, DuckDB)
                    └── SPARQL engine (QLever)
```

### Frontend

A Next.js (Pages Router) application with React. Typical libraries:

- **SWR / fetch** for API calls
- **Recharts** for analytics and author charts
- **react-simple-maps** for the world map: country choropleth plus city and affiliation bubble layers
- **react-force-graph-2d** for Citation Network and Knowledge Graph

The frontend does not embed the Parquet files. It only renders responses from the API.

### Backend

A FastAPI service that:

1. Loads seed-paper and lookup tables for interactive search.
2. Runs SQL-style aggregations over the large citation-event Parquet file (DuckDB).
3. Builds a small heterogeneous graph for one seed paper (Knowledge Graph page).
4. Forwards SPARQL to the internal engine after checking that the query is read-only.

Environment variables select a **local Parquet directory** or a **Hugging Face dataset** mirror. API keys are not stored in this repository.

### RDF / SPARQL

`kg_nodes.parquet` and `kg_edges.parquet` are written to N-Triples with a small ontology:

- resource IRIs under `http://citationhub.org/id/`
- classes and predicates under `http://citationhub.org/ontology/`

QLever indexes the triples. The backend exposes `POST /api/sparql` and rejects SPARQL Update verbs. The SPARQL port is not part of the public UI; users only see the proxied explorer.

See [`sparql.md`](sparql.md) for classes, relations, and references.

## API surface 

| Area | Role |
|---|---|
| Health | Process liveness |
| Overview | Dataset counts and filter option lists |
| Search | Seed-paper keyword search with field/country/journal filters |
| Paper | Intent summary, citing papers, co-cited papers, contexts |
| Authors | Name search, profile, and per-author analytics |
| Knowledge graph | Nodes and edges for one seed paper |
| Geo | Country, city, and affiliation counts, plus map points for cities and affiliations |
| Analytics | Intent trends, top venues, influential-citation ratio |
| SPARQL | Read-only query proxy |
| Export | CSV for search results or one paper’s citation events |

Exact paths and hosting details are omitted here on purpose.

## Data flow

```
IDCite Parquet (Zenodo / Hugging Face / local copy)
        │
        ├── seed + events + authors        →  search, detail, analytics, map
        └── kg_nodes + kg_edges            →  N-Triples → QLever index
                                                    │
                                                    └── SPARQL explorer
```

Construction of the 17 files is documented in [MDCite](https://github.com/SeohyunNam/MDCite). CitationHub assumes those files already exist.

## Design intent

- **Event-centric data.** Pages are organized around citation events (who cited whom, with what intent and context), not only paper-to-paper links.
- **One corpus, several views.** Search, maps, networks, and SPARQL are different projections of IDCite.
- **Read-only SPARQL.** The public explorer can query the graph; it cannot modify it.
- **Public documentation vs. operations.** This repository explains the design. It is not a deployment kit.
