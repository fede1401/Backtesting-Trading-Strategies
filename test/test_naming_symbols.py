import pandas as pd
import numpy as np
import os
import csv
import sys
from pathlib import Path

# Trova dinamicamente la cartella Backtesting-Trading-Strategies e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Backtesting-Trading-Strategies':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Backtesting-Trading-Strategies
        raise RuntimeError("Errore: Impossibile trovare la cartella Backtesting-Trading-Strategies!")
    current_path = current_path.parent
    
# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import  project_root, marketFiles 


def check_naming_symbols_same():    
    """
    Verifica la presenza di simboli con lo stesso nome "base" (prima del punto) su diversi mercati,
    individuando possibili conflitti durante lo scaricamento dei dati. 
    Per i mercati NASDAQ e NYSE i simboli sono indicati senza punto, mentre per il mercato europeo
    a larga capitalizzazione (LARG_COMP_EU) i simboli sono indicati con un punto, quindi qui potrebbero
    risultiare conflitti.

    Esempi di possibili situazioni:
    1. (NASDAQ o NYSE) e (LARG_COMP_EU): è considerato normale, poiché il simbolo fa riferimento a
       una società quotata su due mercati diversi (USA e mercato europeo a larga capitalizzazione).
    2. (NASDAQ o NYSE) e (NASDAQ o NYSE): potrebbe indicare un conflitto, poiché lo stesso nome
       base compare su due mercati USA differenti.
    3. (LARG_COMP_EU) e (LARG_COMP_EU): è un errore, in quanto lo stesso simbolo base all’interno
       dello stesso mercato (prima della separazione con il punto) crea ambiguità e può compromettere
       il corretto download dei dati.
       Questo significa che lo stesso simbolo è stato scaricato più volte e potrebbe creare delle
       distorsioni nei dati. Ad esempio se lo stesso simbolo è scaricato 3 volte e i prezzo sono
       completamente differenti tra loro, salvataggio nel db si può riferire alle 3 diverse volte 
       e mischiare i dati.
       
    In conclusione i simboli che creano errori sono da non considerare per test e simulazioni. 

    Il processo:
    - Legge l’elenco dei file CSV corrispondenti a vari mercati (contenuti nella lista marketFiles).
    - Per ciascun file, crea un dizionario in cui la chiave è il nome base del simbolo (colonna 'Symbol'
      divisa al primo '.') e il valore è la lista dei file in cui tale nome compare.
    - Se lo stesso nome base appare in più file, ne registra l'occorrenza in un file CSV
      (simbolies_same_name.csv) per facilitare l’individuazione e la gestione delle anomalie.

    Returns:
        None
    """
    # Creazione dizionario per contare quante volte un simbolo è presente
    symbols_dict = {}
    
    for filename in marketFiles:
        f_mark = str(filename)
        
        with open(f'{f_mark}', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
            # Crea un lettore CSV con DictReader
            csv_reader = csv.DictReader(file)
            
            for col in csv_reader:
                if col['Symbol'].split('.')[0] in symbols_dict:
                    symbols_dict[col['Symbol'].split('.')[0]].append(f_mark.split('/')[-1])
                else:
                    symbols_dict[col['Symbol'].split('.')[0]] = [f_mark.split('/')[-1]]
        
    
    for symbol, count in symbols_dict.items():
        if len(count) > 1:
            with open(f"{project_root}/data/anomalies/simbolies_same_name.csv", mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([symbol, count])
    
    return None
                

if __name__ == "__main__":
    check_naming_symbols_same()