#!/usr/bin/env python3
"""
Passo 2 - Regressione log-log: log(IRAS1_2) = alpha + beta log(N).
Output: coefficienti, predizioni/residui, grafico log-log con retta stimata.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_2")
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

    data["log_N"] = np.log(data[args.x])
    data["log_IRAS1_2"] = np.log(data[args.y])

    beta, alpha = np.polyfit(data["log_N"], data["log_IRAS1_2"], 1)
    data["log_IRAS1_2_pred"] = alpha + beta * data["log_N"]
    data["IRAS1_2_pred"] = np.exp(data["log_IRAS1_2_pred"])
    data["residuo_log"] = data["log_IRAS1_2"] - data["log_IRAS1_2_pred"]
    data["rapporto_osservato_predetto"] = data[args.y] / data["IRAS1_2_pred"]

    ss_res = ((data["log_IRAS1_2"] - data["log_IRAS1_2_pred"]) ** 2).sum()
    ss_tot = ((data["log_IRAS1_2"] - data["log_IRAS1_2"].mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot

    summary = pd.DataFrame([{
        "alpha_intercetta": alpha,
        "beta_elasticita": beta,
        "R2_loglog": r2,
        "N_atenei": len(data),
    }])
    summary.to_csv(outdir / "passo_2_regressione_loglog_summary.csv", index=False)
    data.to_csv(outdir / "passo_2_predizioni_residui.csv", index=False)

    x_line = np.linspace(data["log_N"].min(), data["log_N"].max(), 100)
    y_line = alpha + beta * x_line
    plt.figure(figsize=(8, 6))
    plt.scatter(data["log_N"], data["log_IRAS1_2"], alpha=0.75)
    plt.plot(x_line, y_line)
    plt.xlabel("log(docenti + ricercatori)")
    plt.ylabel("log(IRAS1_2)")
    plt.title(f"Regressione log-log: beta={beta:.3f}, R²={r2:.3f}")
    plt.tight_layout()
    plt.savefig(outdir / "passo_2_regressione_loglog.png", dpi=200)

    print(summary.to_string(index=False))
    print(f"Output salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
