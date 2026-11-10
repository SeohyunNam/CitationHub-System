# Citation search evaluation set

Citation search runs on a fixed evaluation set built from IDCite. This page explains what the set
contains, how each part is derived from the public IDCite files, and how to regenerate it yourself
and check that it is identical to the one CitationHub uses.

Website: [https://citation-hub-website.vercel.app/search/citation](https://citation-hub-website.vercel.app/search/citation)

---

## What the set contains

| Part | Size | Meaning |
|---|---|---|
| Test citation events | 1,975 | Real IDCite citation events: a citing paper, the sentence in which it cites a seed paper (citation context), the citation intent, and the seed paper it cites |
| Validation citation events | 1,954 | Built the same way from a disjoint set of citing papers |
| Candidate sets | 100 per event | The cited seed paper plus 99 other seed papers from the same scientific field |

The **paper cited in a citation event** is part of the IDCite record itself: `citation_event_id` has the
form `<citing paper>__to__<cited seed paper>`, and its second half equals `target_seed_id`. Nothing is
labelled by hand.

The seven intent labels were assigned automatically when IDCite was built; they are not manually
verified gold labels.

---

## Inputs

Find Two files from the IDCite release ([Zenodo](https://doi.org/10.5281/zenodo.20796923)

| File | SHA-256 of the copy used by CitationHub |
|---|---|
| `citation_events_enriched.parquet` | `946d7b0879ee8403e4940fcf758fa19e20060989e532efbb0ac9b2b5fdc4cc72` |
| `seed_cited_papers_normalized.parquet` | `5b45d860e9cd97cedb01590985d72b7fe2437616da344cea53dc234fb3893d6e` |

---

## How the set is derived

All steps use `RANDOM_SEED = 42`. The code is [`scripts/extract_candidates.py`](../scripts/extract_candidates.py).

1. **Filter citation events.** Keep events whose primary intent is one of the seven canonical intents
   (`background`, `uses`, `similarities`, `differences`, `motivation`, `extends`, `future_work`), with a
   non-empty citing-paper title and citation context, and whose cited paper is a seed paper.
   Result: 1,687,364 events from 1,335,652 citing papers to 12,590 seed papers.
2. **Split by citing paper.** Shuffle the unique citing papers and assign them 80 / 10 / 10 to
   train / validation / test, so no citing paper appears in two splits (test: 133,566 citing papers,
   168,789 events).
3. **Sample test events.** Within the test split, keep one event per (citing paper, intent) — the first
   by `citation_event_id` — then sample up to 300 events per intent. Result: 1,975 events
   (300 each, except `extends` 182 and `future_work` 293).
4. **Build candidate sets.** For each event, take the cited seed paper and 99 seed papers drawn without
   replacement from the same field (`field_id`), then shuffle the 100.
5. **Validation set.** Steps 3–4 on the validation split, additionally preventing a citing paper from
   appearing under two intents. Result: 1,954 events.

Candidate papers are identified by their row number in `seed_cited_papers_normalized.parquet`
(`seed_index`), so the candidate matrix is a plain integer array.

---

## Regenerate it yourself

Requirements: Python 3.10+, `pip install pandas numpy pyarrow`, about 16 GB of RAM. It takes about
five minutes on a CPU.

```bash
python -I scripts/extract_candidates.py <folder with the two parquet files> <output folder>
```

Outputs:

| File | Content |
|---|---|
| `test_queries_1975.parquet` | Test events: `citation_event_id`, `citing_paper_id`, `target_seed_id`, `target_field_id`, `intent`, `title_text`, `context_text` |
| `test_candidate_matrix.npy` | 1,975 × 100 seed row numbers |
| `test_candidates_long.parquet` / `.csv` | The same matrix as a table: one row per (event, candidate), `is_cited_target = 1` for the cited paper |
| `test_unique_candidate_papers.csv` | The 21,059 seed papers that appear in any test candidate set |
| `valid_queries_1954.parquet`, `valid_candidate_matrix.npy`, `valid_candidates_long.parquet` | Validation set |
| `seed_index.parquet` | Seed row number ↔ paper (DOI, title, journal, creator, field) |
| `extraction_stats.json` | The counts above |

### Check that it is identical

Compare the hashes of the regenerated matrices:

```bash
sha256sum test_candidate_matrix.npy valid_candidate_matrix.npy      # macOS/Linux
certutil -hashfile test_candidate_matrix.npy SHA256                  # Windows
```

| File | Expected SHA-256 |
|---|---|
| `test_candidate_matrix.npy` | `e3d909d4b66033c3ace7a2335ee5112eb7f6e51aed6f65bdc5182a180012a810` |
| `valid_candidate_matrix.npy` | `581180813cb42f1a924deffc068158178597a8391f656f4cffd9f0a2f735d349` |

The CitationHub server reports the hash of the matrix it serves at `/api/citation-search/test/meta`
(`matrix_sha256`), so the set behind the website can be compared with a local regeneration.

---

## How Citation search uses the set

- The page lists the 1,975 test citation events; they can be filtered by keywords (citing title or
  context), intent, and field.
- Selecting one uses its citing title, context, and intent as the query and ranks its 100 candidates
  under three conditions, computed live with frozen SciBERT (`allenai/scibert_scivocab_uncased`):
  **C1** title; **C2** title + 0.75 × context; **C3** title + 0.75 × intent-conditioned context.
- The page shows where the cited paper ranks under each condition and the top 10 candidates for the
  chosen condition, each with the other IDCite citation contexts in which it was cited with that intent.
- **Download CSV** returns all 100 candidates with their metadata, `is_cited_target`, and the scores and
  ranks under C1, C2, and C3, so the ranking can be recomputed or inspected independently.

---

## Data use

The generated files are derived from IDCite and are not redistributed in this repository; regenerate
them from the IDCite release with the script above. Reuse of IDCite follows the dataset license and the
terms of its upstream scholarly sources.
