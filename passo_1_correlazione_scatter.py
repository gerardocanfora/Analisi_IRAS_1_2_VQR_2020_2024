#!/usr/bin/env python3
"""
Passo 1 - Scatterplot e correlazioni Pearson/Spearman tra IRAS1_2 e numero totale di docenti+ricercatori.
Input atteso: ANVUR_con_personale.csv con colonne IRAS1_2 e n_docenti_ricercatori.
Output: CSV con statistiche + PNG scatterplot.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_1")
    parser.add_argument("--x", default="n_docenti_ricercatori")
    parser.add_argument("--y", default="IRAS1_2")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df[args.x] = pd.to_numeric(df[args.x], errors="coerce")
    df[args.y] = pd.to_numeric(df[args.y], errors="coerce")
    data = df[["Istituzione", args.x, args.y]].dropna().copy()

    pearson = data[args.x].corr(data[args.y], method="pearson")
    spearman = data[args.x].corr(data[args.y], method="spearman")

    stats = pd.DataFrame([
        {"metrica": "Pearson r", "valore": pearson},
        {"metrica": "Spearman rho", "valore": spearman},
        {"metrica": "N atenei", "valore": len(data)},
    ])
    stats.to_csv(outdir / "passo_1_correlazioni.csv", index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(data[args.x], data[args.y], alpha=0.75)
    plt.xlabel("Docenti + ricercatori")
    plt.ylabel("IRAS1_2")
    plt.title(f"IRAS1_2 vs dimensione ateneo\nPearson={pearson:.3f}, Spearman={spearman:.3f}")
    plt.tight_layout()
    plt.savefig(outdir / "passo_1_scatter.png", dpi=200)

    print(stats.to_string(index=False))
    print(f"Output salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
