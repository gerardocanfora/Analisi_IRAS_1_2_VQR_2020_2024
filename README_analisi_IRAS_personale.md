# Analisi IRAS1_2 vs dimensione del personale

python3 passo_0_aggiungi_personale_anvur.py ANVUR_estratto_6_34.csv personale_as_downloaded.csv ANVUR_con_personale.csv

Input predefinito per tutti gli altri script: `ANVUR_con_personale.csv`.

python3 passo_1_correlazione_scatter.py
python3 passo_2_regressione_loglog.py
python3 passo_3_residui.py
python3 passo_4_simulazione_fondi.py --fondo 100000000
python3 passo_5_correlazione_quote.py
python3 passo_6_rank_kendall.py

Ogni script crea una cartella `output_passo_X` con CSV e grafici PNG.

Dipendenze: pandas, numpy, matplotlib; scipy 