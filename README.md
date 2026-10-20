# Citation Network Analysis: Who Matters Most?

Course project for **Introduction to Network Science** (due **28 October 2026**).
A directed citation network of the bibliometrics literature, built from OpenAlex and analysed with
Python and NetworkX. Every number in the final slide deck is generated from the data by the scripts
in this repository.

**Presentation (Canva):** [Citation Network Analysis, 13 slides](https://www.canva.com/d/bIn8BtE9-fGY0yv)

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

## 8. How do I prepare my project presentation?

The deck `report/CitationNetwork.pptx` has 13 slides. This section explains how to turn it into a
talk. Check your course brief for the time limit and slide limit first. The timings below assume a
10-minute talk with 2-3 minutes for questions; scale them up or down to fit.

### 8.1 Preparation timeline (Oct 20-28)

| Day | Task | Output |
|---|---|---|
| Oct 25-26 | Set `STUDENT` and `STUDENT_ID` in `src/build_deck.py`, re-run it, then read every slide on screen | final deck |
| Oct 26 | Remove off-topic papers if any (see section 6), then re-run all three scripts | numbers match the data |
| Oct 26 | Write a speaker-notes script for each slide (use 8.3) | notes |
| Oct 27 | Rehearse aloud twice with a timer, once in front of someone | timing within limit |
| Oct 27 | Prepare answers to the questions in 8.5 | Q&A prep |
| Oct 27 | Export the PDF and copy the deck to a USB drive and cloud storage | backups |
| Oct 28 | Open the deck on the presentation computer before your slot | no surprises |

### 8.2 The story in one minute

Learn this first. Every slide supports it.

> "I asked who matters most in the bibliometrics literature. I built a citation network of 150
> highly cited papers from OpenAlex, with 424 citations between them. The answer depends on the
> measure. The 1973 co-citation paper has the most citations inside the network. PageRank mostly
> agrees but reorders the top. The papers that bridge groups are recent review and method papers, not
> the classics. The network is sparse but connected, with moderate community structure."

Keep the order **question, data, measures, findings, limits, conclusion**. Do not start with tools.

### 8.3 Slide-by-slide guide (13 slides, about 10 minutes)

| # | Slide | Time | What to say | Evidence on the slide |
|---|---|---|---|---|
| 1 | Title | 0:15 | Your name, ID, course, and the one-line topic. | name and ID (fill in first) |
| 2 | Research questions | 0:45 | State the main question, then Q1-Q4 in one breath each. Say that "matters" is measured in three ways. | the five questions |
| 3 | Data and methods | 1:30 | Source (OpenAlex, retrieved 2026-10-20), the keyword query, de-duplication, top 150, closed sample. Say that `A -> B` means A cites B. Mention the 4 self-loops removed. | N = 150, E = 424 |
| 4 | Network metrics | 1:00 | Read the table top to bottom. Stress sparse (density 0.019) but connected (133 of 150 papers in one component). Say that 33% of papers are never cited inside the sample. | metrics table |
| 5 | Most-cited papers (in-degree) | 1:00 | The 1973 co-citation paper leads with 41, then VOSviewer (2009) with 31. Explain that this counts only citations from the other sampled papers. | top-10 table |
| 6 | The network figure | 0:45 | Explain encodings: size is in-degree, colour is community. Say that the 17 papers outside the main component are not drawn. Point at the largest nodes. | network.png |
| 7 | In-degree versus PageRank | 1:00 | Correlation is 0.96, yet only 6 of the top 10 are shared. PageRank rewards being cited by well-cited papers. | scatter and table |
| 8 | Bridge papers (betweenness) | 1:00 | Top bridges are recent reviews and method papers, such as the 2021 guidelines paper. Classics are cited a lot but are not on paths between others. | betweenness table |
| 9 | Communities | 0:45 | Louvain finds 24 groups with modularity 0.42. Seven groups have 10 or more papers. Say that labels come from structure, not topic. | communities table |
| 10 | Rankings through time | 0:45 | Compare the network up to 2010 (61 papers, 93 citations) with the full network. The 1973 paper stays first. Several early papers fall. | rank-shift table |
| 11 | Limitations | 0:45 | Pick the three that matter most: database coverage, keyword sampling, closed sample. Mention citation age briefly. | bullet list |
| 12 | Conclusions | 0:30 | Answer the main question in two sentences. End with "citation counts show attention, not quality". | summary |
| 13 | References | 0:00 | Do not read it. Leave it up during questions. | references |

Total is about 10 minutes. If you are short of time, cut slide 9 to one sentence and merge 10 into 12.
If you have more time, spend it on slides 7 and 8, which are the most interesting findings.

### 8.4 How to speak to each kind of slide

- **Table slides (4, 5, 8, 9, 10):** never read every row. Say what the table shows, give the top
  one or two rows, then state the takeaway. Example: "The top paper is the 1973 co-citation paper
  with 41 citations. VOSviewer follows with 31. After that the counts drop quickly."
- **Figure slides (6, 7):** first explain what the axes or encodings mean, then say what to look at,
  then give the conclusion. Do not skip the encoding explanation.
- **Method slides (3):** one sentence per decision, with a reason. "I kept only citations between
  sampled papers, so every edge is verifiable in my data."
- **Numbers:** round when speaking ("about 2%" for density 0.019, "about a third" for 33%), but the slide keeps the exact value.
- **Claims:** do not say "small-world" or "strong communities". Your numbers are a path length of
  2.92, clustering of 0.21 and modularity of 0.42. Say "moderate community structure".
- **Honesty about the sample:** say once, early, that these are the 150 most-cited papers matching
  the keywords, not the whole literature.

### 8.5 Questions to expect and how to answer

| Question | Answer |
|---|---|
| Why OpenAlex instead of Web of Science or Scopus? | It is free, needs no login, and returns each paper's reference list, which an edge list needs. The limitation is that coverage differs. |
| Why 150 papers? | It is large enough to show structure and small enough to check every edge. The count came from the data, not from the template draft. |
| Why is the in-degree so low (mean 2.83) compared with real citation counts? | In-degree counts citations from the other 149 sampled papers only (a closed sample). Global counts are far larger. They correlate only moderately (Spearman rho 0.35). |
| What is the difference between in-degree and PageRank? | In-degree counts citations. PageRank also weights each citation by how important the citing paper is. |
| What does betweenness tell you here? | How often a paper lies on shortest citation paths between other papers. High values mean bridges between groups. |
| Why do old papers have high in-degree? | They had longer to be cited. Year and in-degree have a Spearman correlation of -0.61. This is a limitation, not a finding about quality. |
| Why does Louvain give 24 groups? | Papers with no in-sample links each form their own group. Seven groups have 10 or more papers. |
| Is Louvain result stable? | The seed is fixed at 42 for reproducibility. Another seed could shift borders slightly. Say that you did not test it if you did not. |
| What about the 1 edge that points to a newer paper? | It is a metadata artefact (a citation to a later version), kept and listed in `results/tables/edges_citing_newer.csv`. |
| Why a 2010 cutoff? | It splits the sample into a smaller early network (61 papers) and the full one. It is a choice and could be changed in `analyze.py`. |
| Could the keyword search have missed important papers? | Yes. Only papers with these words in the title are included. This is stated on the limitations slide. |
| Did you check self-citation? | Self-loops (a paper citing itself) were removed. Author self-citation was not checked. |
| How can I reproduce your results? | Run the three scripts in section 5. All numbers come from `results/results.json`. |

If you do not know an answer, say what you did and did not test, then say what you would do next.

### 8.6 Design and delivery checklist

**Slides**
- One message per slide, stated in the title or the footer.
- Check text is readable from the back of the room (tables are 11-15 pt, so consider trimming rows if the screen is small).
- Open the network figure at full size once to make sure labels are legible.
- Same fonts and colours throughout; the deck is generated, so a change in `src/build_deck.py` applies everywhere.
- The title slide has your real name and ID, not the placeholders.

**Numbers**
- Re-run the three scripts after any data change, then open the deck and compare each table with `results/results.json`.
- No "unverified" or draft values left (150/620/4.13/0.028 appear nowhere).
- The tools listed on the Methods slide are the ones you used (Python, NetworkX, pandas, SciPy, Matplotlib). Gephi is not used, so do not mention it unless you add it.

**Delivery**
- Rehearse out loud with a timer at least twice. Cut content, not speed, if you run over.
- Face the audience, not the screen. Point at the figure, then return to eye contact.
- Pause after the main finding on slide 5 and after the conclusion.
- Know your first sentence and your last sentence by heart.

**Backups**
- PDF copy of the deck (`report/CitationNetwork.pdf`; regenerate it with PowerPoint after edits).
- A copy on a USB drive and one in cloud storage.
- The repository link: https://github.com/MSamiulHasnat/CitationNetworkAnalysis

### 8.7 Optional extras if you have time

- Add a Gephi version of the network figure (size by in-degree, colour by community) and export it as a PNG. Mention Gephi on the Methods slide only if you do this.
- Add one slide with a short topic label for each large community, after you have looked at the
  papers in `results/tables/communities.csv` and `results/tables/node_metrics.csv`.
- Add a sensitivity check: change `CUTOFF` or `SEED` in `src/analyze.py` and note whether the top findings hold.
- Add a one-slide summary at the end (the story in 8.2) to leave on screen during questions.
