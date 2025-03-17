# Struttura della cartella `data/`

- directory: `dataset/`:
  - Dati per elaborazione dei test e delle simulazioni:

    - `symbols_info/`
      - Contiene i file CSV con la lista dei simboli per ciascun mercato (NASDAQ, NYSE, LARG_COMP_EU, ecc.). Ci sono 2 varianti: ordinati per capitalizzazione e non ordinati. 
      
    - `capitalization/`
      - `by_year/`: Dati di capitalizzazione per titolo e data, suddivisi per anno (es. `1999.csv`, `2000.csv`, …), che elencano tutte le capitalizzazioni di mercato dei titoli di quell’anno.
      - `top_value/`: Dati ordinati per capitalizzazione, suddivisi per anno (`topVal1999.csv`, `topVal2000.csv`, …), titoli già ordinati per capitalizzazione, anch’essi distinti per anno.
      
    - `history_market_data/`
      - Dati di mercato dettagliati, suddivisi a loro volta per mercato (NASDAQ, NYSE, LARG_COMP_EU). Vengono cancellati una volta caricati nel DB.
      - `history_volume_data/`: Dati di mercato relativi al volume scambiato e suddivisi. Utili per la variante operativa relativa alla selezione dei simboli in maniera decrescente alla media del volume scambiato (si trovano i titoli con più operazioni effettuate)

- directory: `anomalies/`:
  - Presenti dei file relativi a delle anomalie rilevate nei dati;

- directory: `result/`:
  - Dati per i risultati dei test/simulazioni;
  - `plot/`: rappresentazioni grafiche dei risultati delle simulazioni generate dal file nel path `test/unit/generate_plot.py`