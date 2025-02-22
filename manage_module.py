from pathlib import Path

# Trova il percorso assoluto dello script corrente (config.py)
project_root = Path(__file__).resolve()

# Risali finché non trovi 'Backtesting-Trading-Strategies'
while project_root.name != 'Backtesting-Trading-Strategies':
    if project_root == project_root.parent:  # Se arrivi alla root del file system
        raise RuntimeError("Errore: Impossibile trovare la cartella Backtesting-Trading-Strategies!")
    project_root = project_root.parent  # Risali di un livello

# Percorsi principali del progetto
# relativi al software 
main_project = project_root / "work_historical"
db_path = main_project / "database"
manage_symbols_path = main_project / "symbols"
utils_path = main_project / "utils"

# relativi ai dati
history_market_data_path = project_root / "data" / "dataset" / "history_market_data"
capitalization_path = project_root / "data" / "dataset" / "capitalization"
symbols_info_path = project_root / "data" / "dataset" / "symbols_info"
history_volume_data = history_market_data_path / "history_volume_data"

# stampa dei percorsi
print(f"""project_root: {project_root}\n
            main_project: {main_project}\n
            db_path: {db_path}\n
            manage_symbols_path: {manage_symbols_path}\n
            utils_path: {utils_path}\n\n
            history_market_data_path: {history_market_data_path}\n
            capitalization_path: {capitalization_path}\n
            symbols_info_path: {symbols_info_path}\n
        """
    )

# Lista dei file di mercato
marketFiles = [
    symbols_info_path / "NASDAQ/nasdaq_symbols_sorted.csv",
    symbols_info_path / "NYSE/nyse_symbols_sorted.csv",
    symbols_info_path / "LARG_COMP_EU/largest_companies_EU.csv"
]


import sys



def get_project_root() -> Path:
    """
    Funzione che permette di ottenere il percorso della root del progetto.
    
    Args: None
    
    Returns:
        - project_root: percorso della root del progetto.
    """
    return project_root



def get_path_specify(which):
    """
    Funzione che permette di aggiungere al path di sistema i moduli specificati.

    Args:
        - which: lista di stringhe contenenti i percorsi dei moduli da aggiungere al path di sistema.
        
    Returns:
        - 0 se l'operazione è andata a buon fine.
    """
    #root = get_project_root()
    for w in which:
        sys.path.append(f"{w}")
    return 0