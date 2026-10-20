# Citation Network Analysis: Who Matters Most?

Course project for **Introduction to Network Science** (due **28 October 2026**).
A directed citation network of the bibliometrics literature, built from OpenAlex and analysed with
Python and NetworkX. Every number in the final slide deck is generated from the data by the scripts
in this repository.

## 1. Project description

**Main question:** which papers are most influential in the bibliometrics literature, and how are
they connected?

A citation network treats papers as nodes and citations as directed edges. **Edge direction:**
`A -> B` means *A cites B*. Papers that many others cite have high in-degree. Papers that connect
otherwise separate groups have high betweenness. Papers cited by other well-cited papers get a high
PageRank.

**Scope of the sample**
- Database: OpenAlex (free, no login, returns each paper's reference list).
- Records: journal articles whose title matches "bibliometric", "citation analysis", "co-citation",
  "bibliographic coupling" or "scientometrics", ranked by global citation count.
- The top 100 per query are merged, de-duplicated by title, and the top 150 are kept.
- Only citations between sampled papers become edges (a closed sample).

## 2. Research questions

| # | Question | Measure |
|---|---|---|
| Main | Who matters most in the citation network? | all measures below |
| Q1 | Which papers receive the most incoming citations? | in-degree |
| Q2 | Which papers bridge different parts of the network? | betweenness centrality |
| Q3 | Does PageRank change the in-degree ranking? | PageRank, Spearman correlation, top-10 overlap |
| Q4 | What communities exist? | Louvain communities, modularity |
| Q5 | Do the rankings change over time? | network up to 2010 versus the full network |

### Findings (from `results/results.json`)

- **Size:** N = 150 papers, E = 424 citations. This replaces the template's unverified draft values
  (150 nodes, 620 edges, mean in-degree 4.13, density 0.028).
- **Density and degree:** mean in-degree 2.83, density 0.019. The network is sparse. 33% of papers
  are never cited inside the sample, and the maximum in-degree is 41.
- **Connectivity:** 133 of 150 papers are in the largest weak component. Average path length there
  is 2.92 and the diameter is 7 (both on the undirected graph).
- **Q1:** the top in-degree paper is *Co-citation in the scientific literature* (1973), with in-degree 41.
  Next are the VOSviewer paper (2009, 31) and *Bibliographic coupling between scientific papers*
  (1963, 18).
- **Q2:** the top betweenness scores go to recent review and method papers, led by *How to conduct a
  bibliometric analysis* (2021). Foundational papers are cited heavily but sit at path endpoints, so
  they score low.
- **Q3:** in-degree and PageRank rankings are strongly correlated (Spearman rho = 0.96) but only
  6 of the top 10 papers are shared.
- **Q4:** Louvain finds 24 groups (modularity 0.42). Seven groups have 10 or more papers, and the
  rest are small groups or papers with no in-sample links.
- **Q5:** the 1973 co-citation paper is first both up to 2010 and in the full network. Several other early papers
  fall in the full ranking. Older papers collect more in-sample citations (Spearman rho between
  year and in-degree = -0.61).
- **Data quality:** 4 self-loops were removed. 1 edge points to a later-published paper (listed in
  `results/tables/edges_citing_newer.csv`).

### Limitations

- Database coverage: OpenAlex differs from Web of Science and Scopus.
- Sampling: a title-keyword search ranked by global citations. Applied bibliometric studies
  (management, tourism, AI) dominate the recent papers.
- Closed sample: in-degree counts only citations from the other 149 papers, not total citations.
- Citation age: older papers had longer to be cited. Self-citations are not removed.
- Louvain is stochastic (seed fixed at 42), and the 2010 cutoff is a choice.
- Citation counts measure attention, not quality.

## 3. Questions asked while building this project

These are the questions and requests that shaped the project, with where each is answered.

1. **"Understand my requirements and generate a proper plan."** The plan covered five phases:
   scope and data, cleaning and verification, analysis, writing, then QA and submission (see section 6).
2. **"Which database?"** OpenAlex. Scopus and Web of Science are not needed.
3. **"Can the real data be retrieved?"** An earlier attempt was blocked by a network policy
   (403 on api.openalex.org). In this run the API was reachable and the data is real. Nothing was invented.
4. **"Are the template's numbers (150 nodes, 620 edges, 4.13, 0.028) correct?"** No. The data gives
   N = 150, E = 424, mean in-degree 2.83 and density 0.019. Mean in-degree = E/N and
   density = E/[N(N-1)].
5. **"Did the first sample work?"** No. A plain keyword search returned off-topic papers (SHELX, SciPy,
   edgeR) and only 78 edges. Restricting to title matches fixed this and gave 424 edges.
6. **"How should isolated papers and the largest component be handled?"** All 150 papers are
   kept for degree measures. Path length and diameter use the largest weak component only.
   The network figure draws the 133 papers in the largest component.
7. **"Which communities are there and what are they?"** See `results/tables/communities.csv`.
   Groups are computed from structure only; labelling them by topic is a manual step.
8. **"Finish the project and execute it in a proper structure."** See sections 4 and 5.

## 4. Repository layout

```
src/collect.py        OpenAlex -> data/processed/{nodes,edges}.csv + metadata.json
src/analyze.py        metrics, communities, time split -> results/
src/build_deck.py     results.json -> report/CitationNetwork.pptx (no hard-coded numbers)
data/raw/             raw API response (works_raw.json)
data/processed/       nodes.csv, edges.csv, metadata.json (query, filter, retrieval date)
data/exclude_ids.txt  optional: OpenAlex ids of off-topic papers to drop (create if needed)
results/results.json  every computed number
results/tables/       node_metrics.csv, top_*.csv, communities.csv, rank_shift_early.csv, ...
results/figures/      network.png, distribution_pagerank.png
report/               CitationNetwork.pptx and its PDF export
requirements.txt
```

## 5. How to run

```
python -m pip install -r requirements.txt
python src/collect.py      # needs internet; writes data/processed/*
python src/analyze.py      # writes results/*
python src/build_deck.py   # writes report/CitationNetwork.pptx
```

Before submitting, set `STUDENT` and `STUDENT_ID` at the top of `src/build_deck.py`, then re-run it.
Re-running `collect.py` later can shift N and E slightly, because OpenAlex rankings change over time.
If it does, re-run `analyze.py` and `build_deck.py` so every slide number still matches.

## 6. Plan and status

| When | Phase | Status |
|---|---|---|
| Oct 20-21 | Scope and data (OpenAlex) | done: 150 nodes, 428 raw edges |
| Oct 22 | Clean and verify N and E | done: 424 edges after cleaning, quality checks in results.json |
| Oct 23-24 | Metrics, communities, time split, figures | done |
| Oct 25-26 | Slides and discussion | draft generated; read and edit the wording |
| Oct 27 | Proofread, check every number against results.json | to do |
| Oct 28 | Submit | to do |

**Still to do by hand:**
- Fill in your name and student ID.
- Skim the 150 titles for off-topic papers and use `data/exclude_ids.txt` to drop any.
- Check the slide layout against the example student projects (Mahnoor001.pdf, Mahnoor002.pdf),
  which were not available in this repository.

## 7. Methods summary

- **Network:** directed graph, `A -> B` = A cites B, self-loops and duplicate edges removed.
- **Mean in-degree** = E/N. **Density** = E/[N(N-1)]. **Mean total degree** = 2E/N.
- **Centrality:** in-degree, out-degree, directed betweenness (normalised), PageRank (alpha 0.85).
- **Clustering and transitivity:** on the undirected version of the graph.
- **Path length and diameter:** on the largest weak component, undirected.
- **Communities:** Louvain on the undirected graph (seed 42), reported with modularity.
- **Time comparison:** the sub-network of papers published up to 2010 versus the full network.
  Ranks use "min" ties.
- **Rank agreement:** Spearman correlation (in-degree vs PageRank, vs global citations, and vs publication year).
