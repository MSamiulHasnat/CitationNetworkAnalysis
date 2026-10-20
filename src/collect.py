"""Pull a citation corpus from OpenAlex and write nodes/edges CSVs.

Edge direction: source -> target means source CITES target.
Only edges with both endpoints inside the sample are kept.
"""
import datetime
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"

QUERIES = ["bibliometric", "citation analysis", "co-citation", "bibliographic coupling", "scientometrics"]
PER_QUERY = 100          # top-cited works fetched per query
TARGET_N = 150           # nodes kept after the union
SELECT = "id,doi,title,publication_year,cited_by_count,referenced_works,type"


def fetch(query):
    params = {
        "filter": f'title.search:"{query}",type:article,has_references:true',
        "sort": "cited_by_count:desc",
        "per-page": PER_QUERY,
        "select": SELECT,
    }
    for attempt in range(5):         # OpenAlex occasionally drops TLS connections
        try:
            r = requests.get("https://api.openalex.org/works", params=params, timeout=60)
            r.raise_for_status()
            return r.json()["results"]
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    works = {}
    for q in QUERIES:
        for w in fetch(q):
            works[w["id"]] = w
    ranked = sorted(works.values(), key=lambda w: -w["cited_by_count"])
    (RAW / "works_raw.json").write_text(json.dumps(ranked), encoding="utf-8")

    # optional manual exclusion list (ids of off-topic papers)
    excl_file = ROOT / "data" / "exclude_ids.txt"
    excl = set(excl_file.read_text().split()) if excl_file.exists() else set()
    ranked = [w for w in ranked if w["id"] not in excl]
    seen, dedup = set(), []          # drop duplicate records of the same title
    for w in ranked:
        key = re.sub(r"[^a-z0-9]", "", (w["title"] or "").lower())
        if key and key not in seen:
            seen.add(key)
            dedup.append(w)
    ranked = dedup[:TARGET_N]

    ids = {w["id"] for w in ranked}
    nodes = pd.DataFrame(
        [(w["id"], w["doi"], w["title"], w["publication_year"], w["cited_by_count"]) for w in ranked],
        columns=["id", "doi", "title", "year", "global_cited_by"],
    )
    edges = pd.DataFrame(
        [(w["id"], r) for w in ranked for r in w["referenced_works"] if r in ids],
        columns=["source", "target"],
    ).drop_duplicates()
    nodes.to_csv(PROC / "nodes.csv", index=False, encoding="utf-8")
    edges.to_csv(PROC / "edges.csv", index=False)
    (PROC / "metadata.json").write_text(json.dumps({
        "database": "OpenAlex",
        "queries": QUERIES,
        "filter": 'title.search:"<query>", type:article, has_references:true',
        "sort": "cited_by_count desc",
        "per_query": PER_QUERY,
        "excluded_ids": sorted(excl),
        "retrieved": datetime.date.today().isoformat(),
        "n_edges_before_cleaning": len(edges),
    }, indent=2))
    print(f"nodes={len(nodes)} edges={len(edges)}")


if __name__ == "__main__":
    sys.exit(main())
