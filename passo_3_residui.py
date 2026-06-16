#!/usr/bin/env python3
"""
Passo 3 - Analisi dei residui della relazione IRAS1_2 ~ dimensione.
Usa una regressione log-log e produce graduatorie degli atenei sopra/sotto il valore atteso.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_3")
    parser.add_argument("--x", default="n_docenti_ricercatori")
    parser.add_argument("--y", default="IRAS1_2")
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df[args.x] = pd.to_numeric(df[args.x], errors="coerce")
    df[args.y] = pd.to_numeric(df[args.y], errors="coerce")
    data = df[["Istituzione", args.x, args.y]].dropna().copy()
    data = data[(data[args.x] > 0) & (data[args.y] > 0)].copy()

    data["log_N"] = np.log(data[args.x])
    data["log_IRAS1_2"] = np.log(data[args.y])
    beta, alpha = np.polyfit(data["log_N"], data["log_IRAS1_2"], 1)
    data["IRAS1_2_atteso"] = np.exp(alpha + beta * data["log_N"])
    data["residuo_assoluto"] = data[args.y] - data["IRAS1_2_atteso"]
    data["rapporto_osservato_atteso"] = data[args.y] / data["IRAS1_2_atteso"]
    data["scostamento_percentuale"] = (data["rapporto_osservato_atteso"] - 1) * 100

    data = data.sort_values("scostamento_percentuale", ascending=False)
    data.to_csv(outdir / "passo_3_residui_tutti.csv", index=False)
    data.head(args.top).to_csv(outdir / "passo_3_top_sopra_atteso.csv", index=False)
    data.tail(args.top).sort_values("scostamento_percentuale").to_csv(outdir / "passo_3_top_sotto_atteso.csv", index=False)

    plot_data = pd.concat([data.head(args.top), data.tail(args.top)]).sort_values("scostamento_percentuale")
    plt.figure(figsize=(9, 8))
    plt.barh(plot_data["Istituzione"], plot_data["scostamento_percentuale"])
    plt.axvline(0)
    plt.xlabel("Scostamento % da IRAS1_2 atteso date le dimensioni")
    plt.title("Atenei più sopra/sotto il valore atteso")
    plt.tight_layout()
    plt.savefig(outdir / "passo_3_residui_top_bottom.png", dpi=200)

    print("Top sopra il valore atteso:")
    print(data.head(args.top)[["Istituzione", args.y, "IRAS1_2_atteso", "scostamento_percentuale"]].to_string(index=False))
    print(f"\nOutput salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
