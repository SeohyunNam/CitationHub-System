# SPARQL layer

CitationHub exposes IDCite as an RDF knowledge graph so that structured questions can be asked in SPARQL. The live explorer is the **SPARQL** tab: [https://citation-hub-website.vercel.app/sparql](https://citation-hub-website.vercel.app/sparql).

## Why SPARQL here

Tabular Parquet files are convenient for search and charts. SPARQL is used when the question is a **graph traversal**: for example, authors of highly cited seed papers in a field, or countries reached through affiliation links. The RDF graph is derived from `kg_nodes.parquet` and `kg_edges.parquet`; it does not replace those files.

## Namespaces

```
PREFIX ch:   <http://citationhub.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

Resources use `http://citationhub.org/id/<node_id>`.

## Ontology 

**Classes:** `ch:SeedPaper`, `ch:CitingPaper`, `ch:CitationEvent`, `ch:Author`, `ch:Journal`, `ch:Affiliation`, `ch:City`, `ch:Country`, `ch:Field`, `ch:Intent`

**Object properties:** `hasAuthor`, `hasAffiliation`, `belongsToField`, `publishedIn`, `publishedInVenue`, `locatedInCity`, `locatedInCountry`, `hasCitedPaper`, `hasCitingPaper`, `hasPrimaryIntent`

**Data properties:** `rdfs:label`, `ch:doi`, `ch:year`, `ch:citedbyCount`, `ch:primaryIntent`, `ch:isInfluential`, `ch:venue`, `ch:publicationName`, `ch:contextCount`, `ch:intentCount`

A citation event connects a citing paper to a seed paper and carries a primary intent. Seed papers connect to authors, affiliations, geography, journals, and fields.

## SPARQL Engine

Queries are evaluated by **QLever**, a SPARQL engine designed for large RDF graphs. The website talks to QLever through a backend proxy:

- permitted: `SELECT`, `ASK`, `CONSTRUCT`, `DESCRIBE`
- rejected: SPARQL Update (`INSERT`, `DELETE`, and related write forms)

The public graph contains on the order of **25 million triples**.

## Example queries

Prepared examples live in [`../examples/sparql/`](../examples/sparql/):

| File | Question |
|---|---|
| `most-cited-seed-papers.rq` | Top seed papers by citation count |
| `intent-distribution.rq` | Citation events per primary intent |
| `top-research-fields.rq` | Fields with the most seed papers |
| `top-authors-by-citations.rq` | Authors whose seed papers accumulated the most citations |
| `top-countries.rq` | Countries with the most seed papers (via affiliations) |
| `total-triples.rq` | Triple count |

## References 

These papers are the recommended background for the SPARQL engine and related techniques used conceptually by CitationHub. They are not CitationHub publications.

1. Hannah Bast and Björn Buchhold. **QLever: A Query Engine for Efficient SPARQL+Text Search.** In *Proceedings of the 2017 ACM Conference on Information and Knowledge Management (CIKM)*, 2017, pp. 647–656. https://doi.org/10.1145/3132847.3132921

2. Hannah Bast, Johannes Kalmbach, Theresa Klumpp, Florian Kramer, and Niklas Schnelle. **Efficient and Effective SPARQL Autocompletion on Very Large Knowledge Graphs.** In *Proceedings of the 31st ACM International Conference on Information and Knowledge Management (CIKM)*, 2022, pp. 2893–2902. https://doi.org/10.1145/3511808.3557093

3. Hannah Bast, Johannes Kalmbach, Theresa Klumpp, and Claudius Korzen. **Knowledge Graphs and Search.** In Omar Alonso and Ricardo Baeza-Yates (eds.), *Information Retrieval: Advanced Topics and Techniques*, ACM Books, vol. 60, 2024, pp. 231–281. Preprint: https://ad-publications.cs.uni-freiburg.de/CHAPTER_knowledge_graphs_BKKK_2023.pdf

4. Sebastian Walter and Hannah Bast. **GRASP: Generic Reasoning And SPARQL Generation across Knowledge Graphs.** *International Semantic Web Conference (ISWC)*, 2025.

5. Hannah Bast, Johannes Kalmbach, Robin Textor-Falconi, and Christoph Ullinger. **Sparqloscope: A generic benchmark for the comprehensive and concise performance evaluation of SPARQL engines.** *International Semantic Web Conference (ISWC)*, 2025. https://purl.org/ad-freiburg/sparqloscope

6. Hannah Bast, Patrick Brosi, and Johannes Kalmbach. **Efficient Spatial Joins on Large Geometry Sets.** In *Proceedings of the 33rd ACM International Conference on Advances in Geographic Information Systems (SIGSPATIAL)*, 2025.

QLever software: [https://github.com/ad-freiburg/qlever](https://github.com/ad-freiburg/qlever)
