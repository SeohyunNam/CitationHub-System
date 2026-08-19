# CitationHub features

This page describes each user-facing view in the live system. The home screenshot in the [README](../README.md) shows the navigation bar that these sections follow.

Website URL: [https://citation-hub-website.vercel.app](https://citation-hub-website.vercel.app)

---

## Home (`/`)

Home is the orientation page.

- **Papers / Authors toggle** in the search box. Papers search by title or DOI; Authors search by name.
- **Dataset Overview** cards report the live index: seed papers, citation events, citing papers, authors, journals, countries, research fields, and citation intents.
- **Explore** cards link to Browse Papers, Author Search, Citation Analytics, Geographic Map, Knowledge Graph, and SPARQL Explorer.

The footer reads “Created by Seohyun Nam”.

---

## Search (`/search`)

Search is the catalogue of highly cited **seed papers**.

- Token-based matching on titles and DOIs (not only exact strings).
- Sidebar filters: **Field**, **Country**, **Journal**.
- Pagination and **Export CSV**.
- Each result card opens **paper detail**.

---

## Authors (`/authors`)

Authors is a name search over seed-paper creators, grouped by `author_id`.

Each result shows:

- name, affiliation, and country
- primary research field
- number of seed papers
- total citations of those papers

Selecting an author opens **author detail** (`/authors/[id]`):

- affiliations, fields, and countries
- seed-paper count, total citations, and citation-event count
- **Citation Intent Distribution** — why the author’s papers are cited
- citations over time
- top citing venues
- list of the author’s seed papers

---

## Analytics (`/analytics`)

Analytics summarizes **all citation events** currently indexed.

| Panel | What it shows |
|---|---|
| Citation Intent Distribution | Counts for the seven canonical intents |
| Influential Citations | Share of events marked influential |
| Citation Intent Trend Over Time | Intent mix by citing year |
| Top Citing Venues | Journals and preprint servers that cite seed papers most often |

Canonical intents: `background`, `uses`, `similarities`, `motivation`, `differences`, `future_work`, `extends`.

---

## Geographic Map (`/geo`)

Geographic Map locates seed-paper authors and affiliations. A view switch offers three layers over the same world map:

| Layer | What it draws |
|---|---|
| **By country** | Choropleth of paper counts (darker = more papers) |
| **By city** | One bubble per city, sized by paper count |
| **By affiliation** | One bubble per institution, sized by paper count |

- Bubble labels are placed automatically, avoiding one another; more names appear as the map is zoomed in.
- Hovering a country, city, or institution reports its paper count.
- Ranked bar charts under the map: **Top Countries**, **Top Cities**, **Top Affiliations**. Each bubble layer is coloured to match its bar chart.

### Where the coordinates come from

IDCite names the city and country of every affiliation but carries no latitude or longitude, so the map cannot be drawn from the dataset alone. CitationHub resolves the dataset’s 1,935 distinct city–country pairs against the [GeoNames](https://www.geonames.org) gazetteer (CC BY 4.0) in advance and ships the resulting lookup table with the application; nothing is geocoded at request time. Matching is done per country and accounts for spelling differences between bibliographic metadata and the gazetteer — accents, alternate names, and same-name towns such as Princeton, NJ and Princeton, FL. The current lookup resolves 1,842 pairs, covering 99.3% of papers that record a city; the remainder are mostly hamlets and typos in the source metadata and are left off the map.

Institutions have no coordinates of their own either, since IDCite locates an affiliation no more precisely than its city. Each is therefore drawn on its city’s position, and institutions sharing a city are fanned out around that point so that each keeps its own bubble, label, and hover target. That fan-out is a drawing device rather than a measured position, and it is held to a fixed size on screen so the ground distance it implies shrinks as the reader zooms in.

---

## Citation Network (`/network`)

Citation Network shows **who cites a chosen seed paper, and with what intent**.

- A seed-paper selector (titles of highly cited papers).
- Force-directed graph: the seed paper is the center node; citing papers are colored by primary intent.
- Node size reflects available citation-context evidence.
- Click a node for title, year, and intent; open **View Detail** for the full paper page.

This view is a citation neighborhood, not the full heterogeneous knowledge graph.

---

## Knowledge Graph (`/kg`)

Knowledge Graph shows **typed scholarly entities** around a seed paper.

**Knowledge Graph tab**

- Paper selector and a force graph of related nodes.
- Node types: seed paper, citing paper, citation event, journal, author, affiliation, city, country, field, intent.
- Pan, zoom, and click a node for its type and label.

**Citation Event Schema tab**

- Schema diagram: a `CitationEvent` links a `CitingPaper` to a `SeedPaper` with an intent, and seed papers link to journals, authors, affiliations, geography, and fields.
- Lists of edge types and node attributes.

---

## SPARQL (`/sparql`)

SPARQL is a query console over the RDF graph derived from IDCite (about 25.1 million triples).

- Example queries: most-cited seed papers, intent distribution, top fields, top authors, top countries, total triples.
- Ontology panel: classes, relations, and data properties.
- Editor for SELECT / ASK / CONSTRUCT / DESCRIBE.
- Results table and CSV download.
- Update operations (INSERT, DELETE, and similar) are rejected.

Example query files: [`../examples/sparql/`](../examples/sparql/). Technical notes: [`sparql.md`](sparql.md).

---

## Paper detail (`/papers/[id]`)

Paper detail is opened from Search, Citation Network, or Knowledge Graph.

Header: title, field, country, DOI, cited-by count, citation-event count, publication date, journal, author, affiliation, and city. Shortcuts: **View Knowledge Graph** and **Export Citations CSV**.

Inner tabs:

| Tab | Content |
|---|---|
| Overview | Intent distribution and summary statistics |
| Citing Papers | Papers that cite this seed paper |
| Co-cited | Other seed papers co-cited with this one |
| Citation Contexts | In-text citation snippets |

---

## How the views share data

All of these pages read IDCite. Search and paper detail use normalized seed papers and citation events. Authors use the author lookup plus seed-paper metadata. Analytics aggregates citation events. Geographic Map counts the city, country, and affiliation names recorded on seed papers and places them with the bundled coordinate lookup. Citation Network uses citing-paper lists for one seed paper. Knowledge Graph and SPARQL use the node/edge tables and the RDF conversion of those tables.
