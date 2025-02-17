
import pandas as pd
import csv
import random
import traceback
import sys
from pathlib import Path


# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
print(current_path)
while current_path.name != 'trading-agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import get_path_specify, symbols_info_path 

get_path_specify([ "symbols_info_path"])


"Simboli che presentano anomalie nei dati di mercato"
SYMB_NASD_ANOMALIE= [ 'IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL']

SYMB_NYSE_ANOMALIE = [ 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV' ]

SYMB_LARGE_ANOMALIE = [ 'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ' ]
    
SYMB_TOT_ANOMALIE = ['IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL', 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV',
                      'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ', 'IPA']
    
# Funzione per leggere i simboli Nasdaq da un file CSV
def symbolsNyseCSV():    
    # Apri il file CSV in modalità lettura
    with open(f'{symbols_info_path}/NYSE/nyse_symbols.csv', mode='r') as file:
        
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        return [col['Symbol'] for col in csv_reader]


# Funzione per ottenere i simboli ordinati per capitalizzazione di mercato in ordine decrescente
def getSymbolsNYSECapDesc():
    # Ottieni i simboli accettati dal broker Tickmill
    symbolsAccepted = symbolsNyseCSV()

    # Dizionario per memorizzare i simboli e la loro capitalizzazione di mercato
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv(f'{symbols_info_path}/NYSE/nyse_symbols.csv')

    # Ordina il DataFrame in base alla colonna 'Market Cap' in ordine decrescente
    df_sorted = df.sort_values(by='Market Cap', ascending=False)

    # Salva il DataFrame ordinato in un nuovo file CSV
    df_sorted.to_csv(f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv', index=False)
    
    return 0



def get_symbols(market, i):
    if market == 'NASDAQ':
        file_str = f'{symbols_info_path}/{market}/nasdaq_symbols_sorted.csv'
    elif market == 'NYSE':
        file_str = f'{symbols_info_path}/{market}/nyse_symbols_sorted.csv'
    elif market == 'LARG_COMP_EU':
        file_str = f'{symbols_info_path}/{market}/largest_companies_EU.csv'

    # Apri il file CSV in modalità lettura
    with open(file_str, mode='r') as file: 
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        if i == -1:
            symbols =[col['Symbol'] for col in csv_reader if col['Symbol'] not in SYMB_TOT_ANOMALIE]
        else:
            for col in csv_reader:
                if col['Symbol'] not in SYMB_TOT_ANOMALIE:
                    symbols.append(col['Symbol']) 
                    if len(symbols) == i:
                        break
        
    # Ritorna la lista dei simboli
    return symbols



def get_x_symbols_ordered_by_market_cap(market, initial_date, x, dizMarkCap, symbolsDispoInDates, logger):
    try:
        # estrazione della data iniziale su cui effettuare la simulazione di trading
        year = str(initial_date).split('-')[0]
        
        # selezione della nomenclatura corretta per il mercato
        if market == 'nasdaq_actions':
            strMark = 'NASDAQ'
        elif market == 'nyse_actions':
            strMark = 'NYSE'
        elif market == 'larg_comp_eu_actions':
            strMark = 'LARG_COMP_EU'
        
        # selezione dei simboli in base alla capitalizzazione di mercato per l'anno selezionato e la data iniziale della simulazione
        symbXSelect = dizMarkCap[strMark][year][initial_date.strftime('%Y-%m-%d %H:%M:%S')]
        symbXSelect = symbXSelect[0].split(';')
        # selezione dei primi x simboli
        symbXSelect = symbXSelect[0:x]
        
        # selezione dei simboli disponibili per la data iniziale della simulazione
        finalSymbXSelect = []        
        for symb in symbXSelect:
            if symb.replace(' ', '') in symbolsDispoInDates[initial_date]:
                # se il simbolo non presenta anomalie nei dati di mercato lo aggiungo alla lista
                if symb.replace(' ', '') not in SYMB_TOT_ANOMALIE:
                    finalSymbXSelect.append(symb.replace(' ', ''))
        
    except Exception as e:
        logger.critical(f"Errore non gestito: {e}")
        logger.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return finalSymbXSelect



# Recupero dei 100 simboli azionari a random disponibili per le date di trading scelte.
def get_x_symbols_random(initial_date, symbolsDispoInDates, logger):
    try:        
        valid_symbols = [s for s in symbolsDispoInDates[initial_date] if s not in SYMB_TOT_ANOMALIE]

        # Poi fai il sample dalla lista già filtrata:
        symbSelect100 = random.sample(valid_symbols, 100)
                
    except Exception as e:
        logger.critical(f"Errore non gestito: {e}")
        logger.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return symbSelect100



def get_x_symbols_ordered_by_market_cap_for_sector( market, initial_date, perc, dizMarkCap, dizSymbSect):
    year = str(initial_date).split('-')[0]
        
    if market == 'nasdaq_actions':
        strMark = 'NASDAQ'
    elif market == 'nyse_actions':
        strMark = 'NYSE'
    elif market == 'larg_comp_eu_actions':
        strMark = 'LARG_COMP_EU'
        
    symbXSelect = dizMarkCap[strMark][year][initial_date.strftime('%Y-%m-%d %H:%M:%S')]
    
    symbXSelect = symbXSelect[0].split(';')
    symbXSelect = [symb.strip() for symb in symbXSelect]
    
    # a questo punto dobbiamo prendere il x% dei simboli azionari con maggiore capitalizzazione per ogni settore
    
    symbXSelect2 = [s for s in symbXSelect if s not in SYMB_TOT_ANOMALIE]
    
    dizNew = {}
    symbolToUse = []
    for k, v in dizSymbSect[strMark].items():
        for s in symbXSelect2:
            if s in v:
                if k not in dizNew:
                    dizNew[k] = [s]
                else:
                    dizNew[k].append(s)
                
    for k,v in dizNew.items():
        if len(v) > 1:
            n = int(len(v) * perc)
            symbolToUse += v[:n]
        else:
            symbolToUse += v            
                
    return symbolToUse




if __name__ == '__main__':

    print(get_symbols('NASDAQ',-1))
    
    
    