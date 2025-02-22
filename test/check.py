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

from manage_module import get_path_specify, project_root, main_project, db_path, manage_symbols_path, utils_path, history_market_data_path, capitalization_path, symbols_info_path, marketFiles 



df = pd.read_csv(f"{project_root}/test/avg.csv")
values = [df['Volume'].values]
print(values)
print(np.mean(values))