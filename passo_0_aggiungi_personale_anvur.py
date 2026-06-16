#!/usr/bin/env python3
"""
Aggiunge al file ANVUR tre colonne derivate dal file del personale universitario:
- n_professori_ordinari_associati: cod qualifica '1PO e 2PA'
- n_ricercatori: cod qualifica '3RU e 3RTD'
- n_docenti_ricercatori: somma delle due colonne precedenti

Uso:
    python aggiungi_personale_anvur_corretto.py ANVUR.csv personale.csv ANVUR_con_personale_corretto.csv

"""

from __future__ import annotations

import argparse
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
import pandas as pd

QUAL_PROF = "1PO e 2PA"
QUAL_RIC = "3RU e 3RTD"

NOME_ATENEO_OVERRIDE = {
    "Aosta": "Aosta - Università degli studi",
    "Bari": "Bari - Università degli studi",
    "Bari Politecnico": "Bari - Politecnico",
    "Basilicata": "Potenza - Università degli studi della Basilicata",
    "Benevento - Giustino Fortunato": 'Benevento - Università telematica "Giustino Fortunato"',
    "Bolzano": "Bolzano - Libera Università",
    "Bra - Scienze Gastronomiche": "Bra (CN) - Università di Scienze Gastronomiche",
    "Calabria": "Arcavacata di Rende - Università della Calabria",
    "Campania Vanvitelli": 'Napoli - Università degli studi della Campania "Luigi Vanvitelli"',
    "Casamassima LUM": 'Casamassima - Libera Università Mediterranea "Jean Monnet"',
    "CASD": "Roma - CASD - Centro Alti Studi per la Difesa",
    "Cassino": "Cassino - Università degli Studi di Cassino e del Lazio Meridionale",
    "Castellanza LIUC": 'Castellanza - Università "Carlo Cattaneo"',
    "Catanzaro": 'Catanzaro - Università degli studi "Magna Grecia"',
    "Chieti e Pescara": "Chieti e Pescara - Università degli studi Gabriele D'Annunzio",
    "Enna Kore": 'Enna - Libera Università della Sicilia Centrale "KORE"',
    "Firenze IUL": 'Firenze - Università telematica "Italian University line"',
    "GSSI": "L'Aquila - Gran Sasso Science Institute",
    "Insubria": "Varese - Università dell' Insubria",
    "Lucca - IMT": "Lucca - Scuola IMT Alti Studi",
    "Marche Politecnica": "Ancona - Università Politecnica delle Marche",
    "Milano": "Milano - Università degli studi",
    "Milano Bicocca": "Milano-Bicocca - Università degli studi",
    "Milano Bocconi": 'Milano - Università commerciale "Luigi Bocconi"',
    "Milano Cattolica": 'Milano - Università Cattolica del "Sacro Cuore"',
    "Milano HUMANITAS": "Rozzano (MI) Humanitas University",
    "Milano IULM": "Milano - Libera Università di Lingue e Comunicazione (IULM)",
    "Milano Politecnico": "Milano - Politecnico",
    "Milano San Raffaele": "Milano - Università Vita-Salute San Raffaele",
    "Molise": "Campobasso - Università degli studi del Molise",
    "Napoli Benincasa": 'Napoli - Università degli studi "Suor Orsola Benincasa"',
    "Napoli Federico II": 'Napoli - Università degli studi "Federico II"',
    "Napoli II": 'Napoli - Università degli studi della Campania "Luigi Vanvitelli"',
    "Napoli L'Orientale": 'Napoli - Università degli studi "L Orientale"',
    "Napoli Parthenope": 'Napoli - Università degli studi "Parthenope"',
    "Napoli Pegaso": 'Napoli - Università telematica "Pegaso"',
    "Novedrate e-Campus": 'Novedrate (CO) - Università telematica "e-Campus"',
    "Pavia IUSS": "Pavia - Istituto universitario di studi superiori",
    "Perugia Stranieri": "Perugia - Università per stranieri",
    "Piemonte Orientale": 'Vercelli - Università degli studi del Piemonte orientale "A. Avogadro"',
    "Pisa Normale": "Pisa - Scuola normale superiore",
    "Pisa S.Anna": 'Pisa - Scuola superiore studi universitari e perfezionamento "S. Anna"',
    "Reggio Calabria": "Reggio Calabria - Università degli studi Mediterranea",
    "Reggio Calabria - Dante Alighieri": "Reggio Calabria - Università per Stranieri",
    "Roma Biomedico": 'Roma - Università "Campus Bio-Medico"',
    "Roma Europea": "Roma - Università Europea",
    "Roma Foro Italico": 'Roma - Università degli studi del "Foro Italico"',
    "Roma La Sapienza": 'Roma - Università degli studi "La Sapienza"',
    "Roma Link Campus": "Roma - Link Campus University",
    "Roma LUISS": "Roma - LUISS Libera Università internazionale degli studi sociali Guido Carli",
    "Roma LUMSA": "Roma - Libera Università Maria SS.Assunta (LUMSA)",
    "Roma Marconi": 'Roma - Università telematica "Guglielmo Marconi"',
    "Roma Mercatorum": "Roma - Universitas Mercatorum",
    "Roma San Raffaele": 'Roma - Università telematica "San Raffaele" - già "UNITEL"',
    "Roma Tor Vergata": 'Roma - Università degli studi di "Tor Vergata"',
    "Roma Tre": "Roma - III Università degli studi",
    "Roma UNICUSANO": "Roma - Università telematica Niccolò Cusano (già UNISU)",
    "Roma UNINETTUNO": 'Roma - Università telematica internazionale "UNINETTUNO"',
    "Roma UNINT": "Roma - Università degli Studi Internazionali - UNINT",
    "Roma UNITELMA": 'Roma - Università telematica "Unitelma Sapienza"',
    "Saint Camillus University": "Roma - Saint Camillus International",
    "Salento": "Lecce - Università del Salento",
    "Sannio": "Benevento - Università degli studi del Sannio",
    "Siena Stranieri": "Siena - Università per stranieri",
    "SSM": "Napoli - Scuola Superiore Meridionale",
    "Torino Politecnico": "Torino - Politecnico",
    "Torrevecchia Teatina - Leonardo da Vinci": 'Torrevecchia Teatina (CH) - Università telematica "Leonardo da Vinci"',
    "Trieste SISSA": "Trieste - Scuola internazionale superiore di studi avanzati",
    "Tuscia": "Viterbo - Università della Tuscia",
    "Urbino Carlo Bo": 'Urbino - Università degli studi "Carlo Bo"',
    "Venezia Cà Foscari": 'Venezia - Università degli studi "Cà Foscari"',
    "Venezia Iuav": "Venezia - Università IUAV",
}


def normalizza_nome(s: str) -> str:
    s = str(s).lower().strip()
    s = s.replace("\x96", "-").replace("–", "-").replace("—", "-")
    s = s.replace("’", "'").replace("`", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r'["“”]', " ", s)
    stop = r"\b(universita|universita degli studi|degli studi|libera universita|telematica|politecnico|scuola|superiore|istituto|di|del|della|delle|degli|dei|e|the|gia)\b"
    s = re.sub(stop, " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def leggi_anvur(path: Path) -> pd.DataFrame:
    preview = pd.read_csv(path, nrows=3, header=None, dtype=str)
    header_row = 1 if "Istituzione" in preview.iloc[1].astype(str).tolist() else 0
    df = pd.read_csv(path, header=header_row, dtype=str)
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    df = df[df["Istituzione"].notna()].copy()
    df["Istituzione"] = df["Istituzione"].str.strip()
    return df


def scegli_nome_effettivo(nome_desiderato: str, personale_names: list[str]) -> str:
    """Restituisce il nome effettivamente presente nel file personale."""
    if nome_desiderato in personale_names:
        return nome_desiderato
    target = normalizza_nome(nome_desiderato)
    norm_to_names = {}
    for n in personale_names:
        norm_to_names.setdefault(normalizza_nome(n), []).append(n)
    if target in norm_to_names:
        return norm_to_names[target][0]
    best_name = max(personale_names, key=lambda n: SequenceMatcher(None, target, normalizza_nome(n)).ratio())
    return best_name


def crea_mappa_nomi(anvur_names: list[str], personale_names: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for nome in anvur_names:
        if nome in NOME_ATENEO_OVERRIDE:
            mapping[nome] = scegli_nome_effettivo(NOME_ATENEO_OVERRIDE[nome], personale_names)
            continue
        key = normalizza_nome(nome)

        candidati_esatti = [
            f"{nome} - Università degli studi",
            f"{nome} - Universita degli studi",
        ]
        for cand in candidati_esatti:
            eff = scegli_nome_effettivo(cand, personale_names)
            if normalizza_nome(eff) == normalizza_nome(cand):
                mapping[nome] = eff
                break
        if nome in mapping:
            continue

        best_name = None
        best_score = -1.0
        for nome_pers in personale_names:
            score = SequenceMatcher(None, key, normalizza_nome(nome_pers)).ratio()
            if score > best_score:
                best_score = score
                best_name = nome_pers
        if best_score < 0.55:
            raise ValueError(
                f"Match incerto per '{nome}'. Miglior candidato: '{best_name}' "
                f"(score={best_score:.2f}). Aggiungi un override in NOME_ATENEO_OVERRIDE."
            )
        mapping[nome] = best_name

    inv = {}
    for k, v in mapping.items():
        inv.setdefault(v, []).append(k)
    duplicati = {v: ks for v, ks in inv.items() if len(ks) > 1}
    if duplicati:
        print("ATTENZIONE: piu' istituzioni ANVUR mappate allo stesso ateneo MUR:")
        for v, ks in duplicati.items():
            print(f"  {v}: {', '.join(ks)}")
    return mapping


def aggiungi_personale(anvur_csv: Path, personale_csv: Path, output_csv: Path, anno: str | None = None) -> None:
    anvur = leggi_anvur(anvur_csv)
    personale = pd.read_csv(personale_csv, dtype=str)
    personale.columns = [str(c).replace("\ufeff", "").strip() for c in personale.columns]

    colonne_richieste = {"ANNO", "NOME_ATENEO", "COD_QUALIFICA", "N_PERS"}
    mancanti = colonne_richieste - set(personale.columns)
    if mancanti:
        raise ValueError(f"Nel file personale mancano queste colonne: {sorted(mancanti)}")

    personale["N_PERS"] = pd.to_numeric(personale["N_PERS"], errors="coerce").fillna(0).astype(int)
    if anno is None:
        anno = str(int(pd.to_numeric(personale["ANNO"], errors="coerce").max()))
    personale = personale[personale["ANNO"].astype(str) == str(anno)].copy()

    agg = (
        personale[personale["COD_QUALIFICA"].isin([QUAL_PROF, QUAL_RIC])]
        .groupby(["NOME_ATENEO", "COD_QUALIFICA"], as_index=False)["N_PERS"]
        .sum()
        .pivot(index="NOME_ATENEO", columns="COD_QUALIFICA", values="N_PERS")
        .fillna(0)
        .astype(int)
        .rename(columns={QUAL_PROF: "n_professori_ordinari_associati", QUAL_RIC: "n_ricercatori"})
        .reset_index()
    )
    for col in ["n_professori_ordinari_associati", "n_ricercatori"]:
        if col not in agg.columns:
            agg[col] = 0
    agg["n_docenti_ricercatori"] = agg["n_professori_ordinari_associati"] + agg["n_ricercatori"]

    mapping = crea_mappa_nomi(anvur["Istituzione"].tolist(), agg["NOME_ATENEO"].tolist())
    anvur["NOME_ATENEO_PERSONALE"] = anvur["Istituzione"].map(mapping)

    out = anvur.merge(
        agg[["NOME_ATENEO", "n_professori_ordinari_associati", "n_ricercatori", "n_docenti_ricercatori"]],
        left_on="NOME_ATENEO_PERSONALE",
        right_on="NOME_ATENEO",
        how="left",
    ).drop(columns=["NOME_ATENEO"])

    missing = out[out["n_docenti_ricercatori"].isna()][["Istituzione", "NOME_ATENEO_PERSONALE"]]
    if len(missing):
        raise ValueError("Alcune istituzioni non sono state agganciate:\n" + missing.to_string(index=False))

    for col in ["n_professori_ordinari_associati", "n_ricercatori", "n_docenti_ricercatori"]:
        out[col] = out[col].fillna(0).astype(int)

    out.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Creato: {output_csv}")
    print(f"Anno personale usato: {anno}")
    print(f"Righe ANVUR: {len(out)}")
    print(f"Righe con totale docenti+ricercatori = 0: {(out['n_docenti_ricercatori'] == 0).sum()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggiunge conteggi personale al file ANVUR.")
    parser.add_argument("anvur_csv", type=Path)
    parser.add_argument("personale_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--anno", default=None, help="Anno da usare; default: anno piu' recente nel file personale")
    args = parser.parse_args()
    aggiungi_personale(args.anvur_csv, args.personale_csv, args.output_csv, args.anno)


if __name__ == "__main__":
    main()
