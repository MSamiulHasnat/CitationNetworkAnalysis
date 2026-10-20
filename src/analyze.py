"""Compute every number used in the report from data/processed/{nodes,edges}.csv.

Edge direction: source -> target means source CITES target.
Outputs: results/results.json, results/tables/*.csv, results/figures/*.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
RES = ROOT / "results"
TAB = RES / "tables"
FIG = RES / "figures"
SEED = 42
CUTOFF = 2010            # time comparison: network "as of" CUTOFF vs full network
for d in (TAB, FIG):
    d.mkdir(parents=True, exist_ok=True)

nodes = pd.read_csv(PROC / "nodes.csv").drop_duplicates("id").set_index("id")
edges = pd.read_csv(PROC / "edges.csv").drop_duplicates()
meta = json.loads((PROC / "metadata.json").read_text())

# ---- cleaning ---------------------------------------------------------
n_loops = int((edges.source == edges.target).sum())
edges = edges[edges.source != edges.target]
yr = nodes["year"]
bad = edges[yr.reindex(edges.target).values > yr.reindex(edges.source).values]
quality = {"self_loops_removed": n_loops, "edges_citing_newer_paper": len(bad)}
bad.assign(src_year=yr.reindex(bad.source).values,
           tgt_year=yr.reindex(bad.target).values).to_csv(TAB / "edges_citing_newer.csv", index=False)

G = nx.DiGraph()
G.add_nodes_from(nodes.index)
G.add_edges_from(edges.itertuples(index=False, name=None))
label = {i: f"{t[:45]} ({y})" for i, t, y in zip(nodes.index, nodes.title, nodes.year)}


def top(d, k=10):
    s = pd.Series(d).sort_values(ascending=False).head(k)
    return [{"rank": r + 1, "id": i, "title": nodes.title[i], "year": int(nodes.year[i]),
             "value": float(v)} for r, (i, v) in enumerate(s.items())]


def summary(G):
    N, E = G.number_of_nodes(), G.number_of_edges()
    U = G.to_undirected()
    wcc = max(nx.weakly_connected_components(G), key=len)
    L = U.subgraph(wcc)
    return {
        "N": N, "E": E,
        "mean_in_degree": E / N,
        "mean_total_degree": 2 * E / N,
        "density": E / (N * (N - 1)),
        "isolated_nodes": int(sum(1 for n in G if G.degree(n) == 0)),
        "weak_components": nx.number_weakly_connected_components(G),
        "largest_wcc_size": len(wcc),
        "avg_clustering_undirected": nx.average_clustering(U),
        "transitivity_undirected": nx.transitivity(U),
        "avg_path_length_largest_wcc_undirected": nx.average_shortest_path_length(L),
        "diameter_largest_wcc_undirected": nx.diameter(L),
    }


R = {"metadata": meta, "data_quality": quality, "summary": summary(G)}

# ---- centralities -----------------------------------------------------
indeg, outdeg = dict(G.in_degree()), dict(G.out_degree())
btw = nx.betweenness_centrality(G, normalized=True)
pr = nx.pagerank(G, alpha=0.85)
R["top_in_degree"], R["top_out_degree"] = top(indeg), top(outdeg)
R["top_betweenness"], R["top_pagerank"] = top(btw), top(pr)
R["in_degree_max"] = max(indeg.values())
R["frac_zero_in_degree"] = sum(v == 0 for v in indeg.values()) / len(G)

ids = list(G)
rho, p = spearmanr([indeg[i] for i in ids], [pr[i] for i in ids])
rho_g, p_g = spearmanr([indeg[i] for i in ids], [nodes.global_cited_by[i] for i in ids])
R["spearman_indegree_pagerank"] = {"rho": rho, "p": p}
R["spearman_indegree_global_citations"] = {"rho": rho_g, "p": p_g}
r_in = pd.Series(indeg).rank(ascending=False, method="min")
r_pr = pd.Series(pr).rank(ascending=False, method="min")
R["top10_overlap_indegree_pagerank"] = len(set(r_in.nsmallest(10).index) & set(r_pr.nsmallest(10).index))

# ---- communities (Louvain on undirected graph) ------------------------
U = G.to_undirected()
comms = sorted(nx.community.louvain_communities(U, seed=SEED), key=len, reverse=True)
member = {n: k for k, c in enumerate(comms) for n in c}
R["communities"] = {
    "algorithm": f"Louvain (undirected, seed={SEED})",
    "modularity": nx.community.modularity(U, comms),
    "n_communities": len(comms),
    "sizes": [len(c) for c in comms],
}
com_rows = []
for k, c in enumerate(comms):
    if len(c) < 3:
        continue
    t = sorted(c, key=lambda n: -indeg[n])[:3]
    com_rows.append({"community": k, "size": len(c),
                     "median_year": float(np.median([nodes.year[n] for n in c])),
                     "top_papers": " | ".join(label[n] for n in t)})
pd.DataFrame(com_rows).to_csv(TAB / "communities.csv", index=False)
R["community_profiles"] = com_rows

# ---- time comparison --------------------------------------------------
Gold = G.subgraph([n for n in G if nodes.year[n] <= CUTOFF]).copy()
old_in = dict(Gold.in_degree())
R["time_split"] = {
    "cutoff_year": CUTOFF,
    "n_up_to_cutoff": Gold.number_of_nodes(),
    "e_up_to_cutoff": Gold.number_of_edges(),
    "top_in_degree_up_to_cutoff": top(old_in),
}
full_rank = pd.Series(indeg).rank(ascending=False, method="min")
old_rank = pd.Series(old_in).rank(ascending=False, method="min")
rows = []
for i in pd.Series(old_in).sort_values(ascending=False).head(10).index:
    rows.append({"title": label[i], "rank_up_to_cutoff": int(old_rank[i]),
                 "rank_full": int(full_rank[i]), "indeg_up_to_cutoff": old_in[i],
                 "indeg_full": indeg[i]})
R["time_split"]["rank_shift_top10_early"] = rows
age_rho, age_p = spearmanr(nodes.year, pd.Series(indeg).reindex(nodes.index))
R["spearman_year_indegree"] = {"rho": age_rho, "p": age_p}

# ---- tables -----------------------------------------------------------
df = nodes.assign(in_degree=pd.Series(indeg), out_degree=pd.Series(outdeg),
                  betweenness=pd.Series(btw), pagerank=pd.Series(pr),
                  community=pd.Series(member))
df.sort_values("in_degree", ascending=False).to_csv(TAB / "node_metrics.csv")
for k in ("top_in_degree", "top_out_degree", "top_betweenness", "top_pagerank"):
    pd.DataFrame(R[k]).to_csv(TAB / f"{k}.csv", index=False)
pd.DataFrame(rows).to_csv(TAB / "rank_shift_early.csv", index=False)

# ---- figures ----------------------------------------------------------
core = max(nx.weakly_connected_components(G), key=len)
n_iso = G.number_of_nodes() - len(core)
H = G.subgraph(core)
pos = nx.spring_layout(H.to_undirected(), seed=SEED, k=0.6, iterations=300)
cmap = plt.get_cmap("tab10")
fig, ax = plt.subplots(figsize=(11, 9))
nx.draw_networkx_edges(H, pos, ax=ax, alpha=0.3, width=0.5, arrows=True, arrowsize=5,
                       edge_color="#555555")
nx.draw_networkx_nodes(H, pos, ax=ax, node_size=[25 + 40 * indeg[n] for n in H],
                       node_color=[cmap(min(member[n], 9)) for n in H],
                       linewidths=0.4, edgecolors="white")
short = lambda n: nodes.title[n].split(":")[0][:28] + f" ({nodes.year[n]})"
texts = [ax.text(pos[n][0], pos[n][1], short(n), fontsize=7, weight="bold")
         for n in sorted(H, key=lambda n: -indeg[n])[:8]]
try:
    from adjustText import adjust_text
    adjust_text(texts, ax=ax)
except ImportError:
    pass
ax.set_title(f"Largest weak component ({len(core)} of {G.number_of_nodes()} papers; "
             f"{n_iso} papers outside it not drawn)\nsize = in-degree, colour = Louvain community")
ax.axis("off")
fig.tight_layout()
fig.savefig(FIG / "network.png", dpi=200)
plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
vals = np.array(list(indeg.values()))
axs[0].hist(vals, bins=range(0, vals.max() + 2), color="#4c72b0")
axs[0].set_yscale("log")
axs[0].set_xlabel("in-degree")
axs[0].set_ylabel("papers (log)")
axs[0].set_title("In-degree distribution")
axs[1].scatter([indeg[i] for i in ids], [pr[i] for i in ids], s=14, color="#dd8452")
axs[1].set_xlabel("in-degree")
axs[1].set_ylabel("PageRank")
axs[1].set_title(f"PageRank vs in-degree (Spearman rho={rho:.2f})")
fig.tight_layout()
fig.savefig(FIG / "distribution_pagerank.png", dpi=200)
plt.close(fig)

(RES / "results.json").write_text(json.dumps(R, indent=2, default=float), encoding="utf-8")
print(json.dumps({k: R[k] for k in ("summary", "data_quality", "communities")}, indent=2, default=float))
