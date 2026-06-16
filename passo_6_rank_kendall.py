#!/usr/bin/env python3
"""
Passo 6 - Confronto delle classifiche IRAS1_2 vs personale: Spearman, Kendall tau e variazioni di rango.
Output: CSV ranking, statistiche e grafico delta rango.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def kendall_tau_a(x, y):
    """Kendall tau semplice senza correzione per pari merito. Sufficiente come fallback."""
    n = len(x)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            prod = dx * dy
            if prod > 0:
                concordant += 1
            elif prod < 0:
                discordant += 1
    denom = n * (n - 1) / 2
    return (concordant - discordant) / denom if denom else float("nan")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_6")
    parser.add_argument("--x", default="n_docenti_ricercatori")
    parser.add_argument("--y", default="IRAS1_2")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df[args.x] = pd.to_numeric(df[args.x], errors="coerce")
    df[args.y] = pd.to_numeric(df[args.y], errors="coerce")
    data = df[["Istituzione", args.x, args.y]].dropna().copy()
    data = data[(data[args.x] > 0) & (data[args.y] > 0)].copy()

    data["rank_IRAS1_2"] = data[args.y].rank(ascending=False, method="min")
    data["rank_personale"] = data[args.x].rank(ascending=False, method="min")
    data["delta_rank"] = data["rank_IRAS1_2"] - data["rank_personale"]
    data["abs_delta_rank"] = data["delta_rank"].abs()
    data = data.sort_values("abs_delta_rank", ascending=False)
    data.to_csv(outdir / "passo_6_ranking.csv", index=False)

    spearman = data["rank_IRAS1_2"].corr(data["rank_personale"], method="spearman")
    try:
        from scipy.stats import kendalltau
        kendall = kendalltau(data["rank_IRAS1_2"], data["rank_personale"]).statistic
    except Exception:
        kendall = kendall_tau_a(data["rank_IRAS1_2"].to_list(), data["rank_personale"].to_list())

    stats = pd.DataFrame([
        {"metrica": "Spearman sui ranghi", "valore": spearman},
        {"metrica": "Kendall tau", "valore": kendall},
        {"metrica": "spostamento medio assoluto di rango", "valore": data["abs_delta_rank"].mean()},
        {"metrica": "spostamento mediano assoluto di rango", "valore": data["abs_delta_rank"].median()},
    ])
    stats.to_csv(outdir / "passo_6_statistiche_ranking.csv", index=False)

    plot_data = data.head(args.top).sort_values("abs_delta_rank")
    plt.figure(figsize=(9, 8))
    plt.barh(plot_data["Istituzione"], plot_data["delta_rank"])
    plt.axvline(0)
    plt.xlabel("Rank IRAS1_2 - rank personale")
    plt.title("Atenei con maggiore spostamento di posizione")
    plt.tight_layout()
    plt.savefig(outdir / "passo_6_delta_rank_top.png", dpi=200)

    print(stats.to_string(index=False))
    print(f"Output salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
