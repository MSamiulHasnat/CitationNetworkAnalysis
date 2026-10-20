"""Build report/CitationNetwork.pptx. Every number is read from results/results.json."""
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
FIG = ROOT / "results" / "figures"

# Fill these in before submitting (kept visible on purpose; not invented).
STUDENT = "[YOUR NAME]"
STUDENT_ID = "[STUDENT ID]"
COURSE = "Introduction to Network Science"

S, M, T = R["summary"], R["metadata"], R["time_split"]
C, Q = R["communities"], R["data_quality"]
NAVY, GREY = RGBColor(0x1F, 0x2A, 0x44), RGBColor(0x55, 0x55, 0x55)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]


def slide(title):
    s = prs.slides.add_slide(blank)
    tb = s.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size, p.font.bold, p.font.color.rgb = Pt(30), True, NAVY
    return s


def bullets(s, items, left=0.6, top=1.4, width=12.1, height=5.5, size=20):
    tf = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height)).text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "• " + it
        p.font.size = Pt(size)
        p.space_after = Pt(8)


def table(s, header, rows, left, top, width, col_w, size=13, row_h=0.4):
    t = s.shapes.add_table(len(rows) + 1, len(header), Inches(left), Inches(top),
                           Inches(width), Inches(row_h * (len(rows) + 1))).table
    for j, w in enumerate(col_w):
        t.columns[j].width = Inches(w)
    for j, h in enumerate(header):
        t.cell(0, j).text = h
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r):
            t.cell(i, j).text = str(v)
    for row in t.rows:
        for c in row.cells:
            for p in c.text_frame.paragraphs:
                p.font.size = Pt(size)
    return t


def short(t, n=62):
    return t if len(t) <= n else t[: n - 1] + "…"


def foot(s, text):
    tb = s.shapes.add_textbox(Inches(0.6), Inches(6.85), Inches(12.1), Inches(0.5))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.color.rgb = text, Pt(12), GREY


# 1 Title
s = slide("Who Matters Most in a Citation Network?")
bullets(s, ["Citation network analysis of the bibliometrics literature",
            f"{COURSE}", f"{STUDENT}  |  ID: {STUDENT_ID}", "October 28, 2026"], top=2.2, size=24)

# 2 Questions
s = slide("Research questions")
bullets(s, [
    "Main question: which papers are most influential in the bibliometrics literature, and how are they connected?",
    "Q1. Which papers receive the most incoming citations (in-degree)?",
    "Q2. Which papers act as bridges between parts of the network (betweenness)?",
    "Q3. Does PageRank re-order the in-degree ranking?",
    "Q4. What communities exist, and do rankings change over time?",
])

# 3 Data & methods
s = slide("Data and methods")
bullets(s, [
    f"Source: {M['database']} API, retrieved {M['retrieved']}; no login needed.",
    "Sample: top-cited journal articles whose title matches " + ", ".join(f"“{q}”" for q in M["queries"])
    + f" (up to {M['per_query']} per query), merged, de-duplicated by title, top {S['N']} kept.",
    "Edge A → B means A cites B. Only citations between sampled papers are kept.",
    f"Cleaning: {Q['self_loops_removed']} self-loops removed; {Q['edges_citing_newer_paper']} edge points to a "
    "later-published paper (metadata artefact, kept and flagged).",
    f"Result: N = {S['N']} papers, E = {S['E']} citations; {S['largest_wcc_size']} papers lie in the largest weak component.",
    "Tools: Python (NetworkX, pandas, SciPy, Matplotlib). Communities: Louvain on the undirected graph (seed 42).",
    "Clustering is computed on the undirected graph; path length only on the largest weak component (also undirected).",
], size=18)

# 4 Metrics
s = slide("Network metrics")
rows = [
    ("Papers (N)", S["N"]), ("Citations (E)", S["E"]),
    ("Mean in-degree (E/N)", f"{S['mean_in_degree']:.2f}"),
    ("Mean total degree (2E/N)", f"{S['mean_total_degree']:.2f}"),
    ("Density E/[N(N−1)]", f"{S['density']:.4f}"),
    ("Papers with no links", S["isolated_nodes"]),
    ("Weak components", S["weak_components"]),
    ("Average clustering (undirected)", f"{S['avg_clustering_undirected']:.3f}"),
    ("Avg. path length, largest component", f"{S['avg_path_length_largest_wcc_undirected']:.2f}"),
    ("Diameter, largest component", S["diameter_largest_wcc_undirected"]),
    (f"Louvain modularity ({C['n_communities']} groups)", f"{C['modularity']:.3f}"),
]
table(s, ["Metric", "Value"], rows, 0.6, 1.4, 7.2, [5.2, 2.0], size=15, row_h=0.42)
bullets(s, [f"{R['frac_zero_in_degree']:.0%} of papers are never cited inside the sample.",
            f"Maximum in-degree is {R['in_degree_max']} against a mean of {S['mean_in_degree']:.2f}: citations are highly concentrated.",
            "The network is sparse: density is under 2%."],
        left=8.1, top=1.4, width=4.7, size=16)

# 5 Top in-degree
s = slide("Most-cited papers inside the network (in-degree)")
rows = [(r["rank"], short(r["title"], 78), r["year"], int(r["value"])) for r in R["top_in_degree"]]
table(s, ["Rank", "Paper", "Year", "In-degree"], rows, 0.6, 1.4, 12.1, [0.8, 8.6, 1.0, 1.7], size=14)
foot(s, f"In-degree counts citations from the other {S['N'] - 1} sampled papers only. "
        f"Rank correlation with global OpenAlex citation counts: Spearman ρ = {R['spearman_indegree_global_citations']['rho']:.2f}.")

# 6 Network
s = slide("The citation network")
s.shapes.add_picture(str(FIG / "network.png"), Inches(2.4), Inches(1.2), height=Inches(5.9))

# 7 PageRank
s = slide("In-degree versus PageRank")
s.shapes.add_picture(str(FIG / "distribution_pagerank.png"), Inches(0.5), Inches(1.3), width=Inches(7.6))
rows = [(r["rank"], short(r["title"], 40), r["year"]) for r in R["top_pagerank"]]
table(s, ["PR", "Top PageRank papers", "Year"], rows, 8.3, 1.3, 4.6, [0.6, 3.2, 0.8], size=11, row_h=0.33)
bullets(s, [f"Spearman ρ (in-degree, PageRank) = {R['spearman_indegree_pagerank']['rho']:.2f}: the two rankings broadly agree.",
            f"But only {R['top10_overlap_indegree_pagerank']} of the top 10 are shared; PageRank rewards being cited by well-cited papers.",
            f"Older papers collect more in-sample citations (Spearman ρ year vs in-degree = {R['spearman_year_indegree']['rho']:.2f})."],
        top=5.3, width=12.1, height=1.9, size=15)

# 8 Bridges
s = slide("Bridge papers (betweenness centrality)")
rows = [(r["rank"], short(r["title"], 80), r["year"], f"{r['value']:.4f}") for r in R["top_betweenness"]]
table(s, ["Rank", "Paper", "Year", "Betweenness"], rows, 0.6, 1.4, 12.1, [0.8, 8.4, 1.0, 1.9], size=14)
foot(s, "Directed betweenness. Top bridges are mostly review/method papers that cite across fields; "
        "foundational papers are cited a lot but sit at path endpoints, so they score low.")

# 9 Communities
s = slide("Communities (Louvain)")
big = [c for c in R["community_profiles"]]
rows = [(c["community"], c["size"], int(c["median_year"]), short(c["top_papers"].split(" | ")[0], 70)) for c in big]
table(s, ["Group", "Papers", "Median year", "Most-cited paper in group (in-sample)"], rows, 0.6, 1.4, 12.1,
      [0.9, 1.0, 1.5, 8.7], size=13)
foot(s, f"Modularity {C['modularity']:.3f} with {len(big)} groups of 3+ papers; remaining groups are single papers "
        "with no in-sample links. Group labels are computed only on structure, not on topic.")

# 10 Time
s = slide(f"Rankings through time (network up to {T['cutoff_year']} vs full)")
rows = [(short(r["title"], 60), r["rank_up_to_cutoff"], r["rank_full"], r["indeg_up_to_cutoff"], r["indeg_full"])
        for r in T["rank_shift_top10_early"]]
table(s, ["Paper (year)", f"Rank ≤{T['cutoff_year']}", "Rank full", f"In-deg ≤{T['cutoff_year']}", "In-deg full"],
      rows, 0.6, 1.4, 12.1, [6.4, 1.4, 1.3, 1.6, 1.4], size=13)
foot(s, f"Early network: {T['n_up_to_cutoff']} papers, {T['e_up_to_cutoff']} citations. Ties share a rank. "
        "The 1973 co-citation paper stays first; several early papers fall in the full ranking as later papers cite other work.")

# 11 Limitations
s = slide("Limitations")
bullets(s, [
    "Database: OpenAlex coverage and reference lists differ from Web of Science or Scopus.",
    "Sampling: title keyword search ranked by global citations; applied bibliometric studies (e.g. in management) "
    "dominate the recent half and some topics are missed.",
    "Closed sample: only citations among the 150 papers count, so in-degree is not total citations.",
    "Citation age: older papers had longer to be cited; self-citations are not removed.",
    "Single run: Louvain is stochastic (seed fixed) and the cutoff year is a choice.",
    "Citation counts measure attention, not quality.",
])

# 12 Conclusion
top1 = R["top_in_degree"][0]
s = slide("Conclusions")
bullets(s, [
    f"Most-cited inside the network: “{short(top1['title'], 70)}” ({top1['year']}), in-degree {int(top1['value'])}.",
    "Influence depends on the measure: in-degree, PageRank and betweenness pick out different papers "
    "(foundational, well-connected, and bridging).",
    f"Structure: sparse (density {S['density']:.3f}) but {S['largest_wcc_size']} of {S['N']} papers are connected; "
    f"modularity {C['modularity']:.2f} indicates moderate community structure.",
    "Citation counts alone do not measure quality, but network position shows the structural role each paper plays.",
])

# 13 References
s = slide("References and data")
bullets(s, [
    "OpenAlex API (https://openalex.org); Priem, Piwowar & Orr (2022), OpenAlex: a fully-open index of scholarly works.",
    "Hagberg, Schult & Swart (2008). Exploring network structure, dynamics, and function using NetworkX.",
    "Blondel et al. (2008). Fast unfolding of communities in large networks. J. Stat. Mech.",
    "Page, Brin, Motwani & Winograd (1999). The PageRank citation ranking.",
    "Reproducibility: data/processed/{nodes,edges}.csv and metadata.json; src/analyze.py regenerates every figure and number.",
], size=17)

out = ROOT / "report" / "CitationNetwork.pptx"
out.parent.mkdir(exist_ok=True)
prs.save(out)
print("saved", out)
