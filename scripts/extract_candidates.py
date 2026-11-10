"""
Regenerate the CitationHub Citation search evaluation set from the IDCite
Parquet files: 1,975 test and 1,954 validation citation events, each with a
fixed set of 100 same-field candidate seed papers.

Only pandas, numpy and pyarrow are needed (no model). The output depends only
on the two input files and RANDOM_SEED = 42, so the same inputs always produce
byte-identical candidate matrices (see docs/evaluation-dataset.md for the
expected SHA-256 hashes).

Usage:
    python -I extract_candidates.py <folder with the IDCite parquet files> <out_dir>

Inputs (from the IDCite release):
    citation_events_enriched.parquet
    seed_cited_papers_normalized.parquet
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

EVENT_PATH = BASE / "citation_events_enriched.parquet"
SEED_PATH = BASE / "seed_cited_papers_normalized.parquet"

RANDOM_SEED = 42
N_PER_INTENT = 300
CANDIDATE_SIZE = 100
CANONICAL_INTENTS = ["background", "uses", "similarities", "differences",
                     "motivation", "extends", "future_work"]

# ---------------- 1. Load ----------------
events = pd.read_parquet(EVENT_PATH, columns=[
    "citation_event_id", "citing_paper_id", "cited_seed_paper_id",
    "citing_title", "primary_intent", "contexts"])
seeds = pd.read_parquet(SEED_PATH, columns=[
    "seed_paper_id", "doi", "title", "publication_name", "creator",
    "group", "category", "field_id", "cover_date", "citedby_count"])
print(f"events={len(events):,} seeds={len(seeds):,}")

# ---------------- 2. Filter events and split by citing paper (80/10/10) ----------------
def normalize_context(x):
    if x is None:
        return ""
    if isinstance(x, (np.ndarray, list, tuple)):
        return " ".join(str(v).strip() for v in x if v is not None and str(v).strip())
    return str(x).strip()

events["context_text"] = events["contexts"].apply(normalize_context)
events = events.drop(columns=["contexts"])
events["title_text"] = events["citing_title"].fillna("").astype(str).str.strip()
events["intent"] = events["primary_intent"].fillna("").astype(str).str.strip()

clean = events[events["intent"].isin(CANONICAL_INTENTS)].copy()
del events
clean = clean[clean["title_text"].ne("") & clean["context_text"].ne("")
              & clean["citing_paper_id"].notna() & clean["cited_seed_paper_id"].notna()].copy()
seed_ids = set(seeds["seed_paper_id"].astype(str))
clean["cited_seed_paper_id"] = clean["cited_seed_paper_id"].astype(str)
clean = clean[clean["cited_seed_paper_id"].isin(seed_ids)].copy()

stats = {
    "filtered_events": len(clean),
    "unique_citing": clean["citing_paper_id"].nunique(),
    "unique_cited_seeds": clean["cited_seed_paper_id"].nunique(),
}

unique_sources = clean["citing_paper_id"].drop_duplicates().to_numpy()
rng = np.random.default_rng(RANDOM_SEED)
rng.shuffle(unique_sources)
N = len(unique_sources)
n_train, n_valid = int(N * 0.80), int(N * 0.10)
train_sources = set(unique_sources[:n_train])
valid_sources = set(unique_sources[n_train:n_train + n_valid])
test_sources = set(unique_sources[n_train + n_valid:])
train_df = clean[clean["citing_paper_id"].isin(train_sources)]
valid_df = clean[clean["citing_paper_id"].isin(valid_sources)].copy()
test_df = clean[clean["citing_paper_id"].isin(test_sources)].copy()
stats.update({
    "train_sources": len(train_sources), "valid_sources": len(valid_sources),
    "test_sources": len(test_sources), "train_events": len(train_df),
    "valid_events": len(valid_df), "test_events": len(test_df),
})
del clean, train_df

# ---------------- 3. Test queries: one event per (citing paper, intent), up to 300 per intent ----------------
test_unique = (test_df.sort_values("citation_event_id")
               .drop_duplicates(subset=["citing_paper_id", "intent"], keep="first").copy())
parts = []
for intent in CANONICAL_INTENTS:
    subset = test_unique[test_unique["intent"] == intent].copy()
    parts.append(subset.sample(n=min(N_PER_INTENT, len(subset)), random_state=RANDOM_SEED))
test_q = pd.concat(parts, ignore_index=True).reset_index(drop=True)

# ---------------- 4. Candidates: cited paper + 99 random same-field seed papers ----------------
seeds = seeds.copy()
seeds["seed_paper_id"] = seeds["seed_paper_id"].astype(str)
seeds = seeds.reset_index(drop=True)
seed_id_to_idx = {s: i for i, s in enumerate(seeds["seed_paper_id"])}
seed_id_to_field = dict(zip(seeds["seed_paper_id"], seeds["field_id"]))
field_to_indices = {f: g.index.to_numpy() for f, g in seeds.groupby("field_id", sort=False)}


def add_targets(q):
    q = q.copy()
    q["target_seed_id"] = q["cited_seed_paper_id"].astype(str)
    q["target_field_id"] = q["target_seed_id"].map(seed_id_to_field)
    return q


def build_candidates(q, rng):
    mats = []
    for _, row in q.iterrows():
        pos = seed_id_to_idx[row["target_seed_id"]]
        pool = field_to_indices[row["target_field_id"]]
        neg_pool = pool[pool != pos]
        assert len(neg_pool) >= CANDIDATE_SIZE - 1
        neg = rng.choice(neg_pool, size=CANDIDATE_SIZE - 1, replace=False)
        cands = np.concatenate([np.array([pos], dtype=int), neg])
        rng.shuffle(cands)
        mats.append(cands)
    return np.vstack(mats)


test_q = add_targets(test_q)
test_matrix = build_candidates(test_q, np.random.default_rng(RANDOM_SEED))

# ---------------- 5. Validation queries (no citing paper repeated across intents) ----------------
valid_unique = (valid_df.sort_values("citation_event_id")
                .drop_duplicates(subset=["citing_paper_id", "intent"], keep="first").copy())
vparts, used = [], set()
for intent in CANONICAL_INTENTS:
    subset = valid_unique[valid_unique["intent"] == intent].copy()
    subset = subset[~subset["citing_paper_id"].isin(used)]
    s = subset.sample(n=min(N_PER_INTENT, len(subset)), random_state=RANDOM_SEED)
    used.update(s["citing_paper_id"].tolist())
    vparts.append(s)
valid_q = add_targets(pd.concat(vparts, ignore_index=True).reset_index(drop=True))

# ---------------- 6. Validation candidates ----------------
valid_matrix = build_candidates(valid_q, np.random.default_rng(42))

# ---------------- Save ----------------
seed_meta = seeds[["seed_paper_id", "doi", "title", "publication_name", "creator",
                   "group", "category", "field_id", "cover_date", "citedby_count"]]


def long_table(q, mat, split):
    rows = []
    for qi in range(len(q)):
        target_idx = seed_id_to_idx[q.iloc[qi]["target_seed_id"]]
        for pos, sidx in enumerate(mat[qi]):
            rows.append((split, qi, q.iloc[qi]["citation_event_id"], pos, int(sidx),
                         int(sidx == target_idx)))
    df = pd.DataFrame(rows, columns=["split", "query_idx", "citation_event_id",
                                     "candidate_position", "seed_index", "is_cited_target"])
    return df.join(seed_meta, on="seed_index")


qcols = ["citation_event_id", "citing_paper_id", "target_seed_id", "target_field_id",
         "intent", "title_text", "context_text"]
test_q[qcols].to_parquet(OUT / "test_queries_1975.parquet", index=False)
valid_q[qcols].to_parquet(OUT / "valid_queries_1954.parquet", index=False)
np.save(OUT / "test_candidate_matrix.npy", test_matrix)
np.save(OUT / "valid_candidate_matrix.npy", valid_matrix)
seed_meta.reset_index().rename(columns={"index": "seed_index"}).to_parquet(
    OUT / "seed_index.parquet", index=False)

test_long = long_table(test_q, test_matrix, "test")
valid_long = long_table(valid_q, valid_matrix, "valid")
test_long.to_parquet(OUT / "test_candidates_long.parquet", index=False)
valid_long.to_parquet(OUT / "valid_candidates_long.parquet", index=False)
test_long.to_csv(OUT / "test_candidates_long.csv", index=False, encoding="utf-8-sig")

# Unique seed papers that appear in any test candidate set
uniq = (test_long.groupby("seed_index")
        .agg(n_queries_as_candidate=("query_idx", "size"),
             n_queries_as_target=("is_cited_target", "sum"))
        .join(seed_meta).reset_index()
        .sort_values("n_queries_as_candidate", ascending=False))
uniq.to_csv(OUT / "test_unique_candidate_papers.csv", index=False, encoding="utf-8-sig")

stats.update({
    "test_queries": len(test_q), "valid_queries": len(valid_q),
    "test_matrix_shape": str(test_matrix.shape), "valid_matrix_shape": str(valid_matrix.shape),
    "test_unique_candidate_papers": len(uniq),
    "test_unique_targets": test_q["target_seed_id"].nunique(),
    "test_intent_counts": test_q["intent"].value_counts().reindex(CANONICAL_INTENTS).to_dict(),
    "valid_intent_counts": valid_q["intent"].value_counts().reindex(CANONICAL_INTENTS).to_dict(),
    "test_dup_citing": int(test_q["citing_paper_id"].duplicated().sum()),
    "valid_dup_citing": int(valid_q["citing_paper_id"].duplicated().sum()),
    "test_first_candidates_row0": test_matrix[0][:10].tolist(),
})
pd.Series(stats).to_json(OUT / "extraction_stats.json", indent=2, force_ascii=False)
for k, v in stats.items():
    print(f"{k}: {v}")
