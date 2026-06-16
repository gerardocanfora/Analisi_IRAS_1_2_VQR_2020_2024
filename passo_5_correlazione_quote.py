#!/usr/bin/env python3
"""
Passo 5 - Correlazione tra quote di riparto: quota IRAS1_2 vs quota personale.
Output: CSV quote, statistiche di correlazione, scatterplot quote.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_5")
    parser.add_argument("--x", default="n_docenti_ricercatori")
    parser.add_argument("--y", default="IRAS1_2")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df[args.x] = pd.to_numeric(df[args.x], errors="coerce")
    df[args.y] = pd.to_numeric(df[args.y], errors="coerce")
    data = df[["Istituzione", args.x, args.y]].dropna().copy()
    data = data[(data[args.x] > 0) & (data[args.y] > 0)].copy()

    data["quota_IRAS1_2"] = data[args.y] / data[args.y].sum()
    data["quota_personale"] = data[args.x] / data[args.x].sum()
    data["differenza_quote"] = data["quota_IRAS1_2"] - data["quota_personale"]
    data["differenza_quote_pp"] = data["differenza_quote"] * 100
    data.to_csv(outdir / "passo_5_quote.csv", index=False)

    stats = pd.DataFrame([
        {"metrica": "Pearson quote", "valore": data["quota_IRAS1_2"].corr(data["quota_personale"], method="pearson")},
        {"metrica": "Spearman quote", "valore": data["quota_IRAS1_2"].corr(data["quota_personale"], method="spearman")},
        {"metrica": "somma differenze assolute quote", "valore": data["differenza_quote"].abs().sum()},
        {"metrica": "differenza media assoluta in punti percentuali", "valore": data["differenza_quote_pp"].abs().mean()},
    ])
    stats.to_csv(outdir / "passo_5_correlazione_quote.csv", index=False)

    plt.figure(figsize=(7, 7))
    plt.scatter(data["quota_personale"], data["quota_IRAS1_2"], alpha=0.75)
    min_v = min(data["quota_personale"].min(), data["quota_IRAS1_2"].min())
    max_v = max(data["quota_personale"].max(), data["quota_IRAS1_2"].max())
    plt.plot([min_v, max_v], [min_v, max_v])
    plt.xlabel("Quota personale")
    plt.ylabel("Quota IRAS1_2")
    plt.title("Quote di riparto: IRAS1_2 vs personale")
    plt.tight_layout()
    plt.savefig(outdir / "passo_5_scatter_quote.png", dpi=200)

    print(stats.to_string(index=False))
    print(f"Output salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
