#!/usr/bin/env python3
"""
Passo 4 - Simulazione distribuzione fondi proporzionale a IRAS1_2 vs proporzionale a N docenti+ricercatori.
Output: allocazioni, differenze assolute/percentuali e riepilogo soglie.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ANVUR_con_personale.csv")
    parser.add_argument("--outdir", default="output_passo_4")
    parser.add_argument("--fondo", type=float, default=100_000_000)
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

    data["quota_IRAS"] = data[args.y] / data[args.y].sum()
    data["quota_N"] = data[args.x] / data[args.x].sum()
    data["fondi_da_IRAS"] = args.fondo * data["quota_IRAS"]
    data["fondi_da_N"] = args.fondo * data["quota_N"]
    data["differenza_euro"] = data["fondi_da_IRAS"] - data["fondi_da_N"]
    data["differenza_percentuale_su_N"] = data["differenza_euro"] / data["fondi_da_N"] * 100
    data["differenza_assoluta_percentuale"] = data["differenza_percentuale_su_N"].abs()

    data = data.sort_values("differenza_assoluta_percentuale", ascending=False)
    data.to_csv(outdir / "passo_4_simulazione_fondi.csv", index=False)

    summary_rows = []
    for soglia in [1, 2, 5, 10, 20]:
        quota = (data["differenza_assoluta_percentuale"] <= soglia).mean() * 100
        summary_rows.append({"soglia_diff_percentuale": soglia, "percentuale_atenei_entro_soglia": quota})
    summary = pd.DataFrame(summary_rows)
    summary.loc[len(summary)] = ["differenza_media_assoluta_%", data["differenza_assoluta_percentuale"].mean()]
    summary.loc[len(summary)] = ["differenza_mediana_assoluta_%", data["differenza_assoluta_percentuale"].median()]
    summary.to_csv(outdir / "passo_4_riepilogo_soglie.csv", index=False)

    plt.figure(figsize=(8, 6))
    plt.hist(data["differenza_percentuale_su_N"], bins=25)
    plt.axvline(0)
    plt.xlabel("Differenza %: fondi IRAS rispetto a fondi da N")
    plt.ylabel("Numero atenei")
    plt.title("Distribuzione delle variazioni di finanziamento")
    plt.tight_layout()
    plt.savefig(outdir / "passo_4_istogramma_differenze.png", dpi=200)

    print(summary.to_string(index=False))
    print(f"Output salvati in: {outdir.resolve()}")


if __name__ == "__main__":
    main()
