import yfinance as yf
import os
import pandas as pd
import logging
from datetime import datetime, time, timedelta
import traceback
import csv
import sys
from pathlib import Path
import time
import warnings
warnings.filterwarnings("ignore")

# Trova dinamicamente la cartella Backtesting-Trading-Strategies e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Backtesting-Trading-Strategies':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Backtesting-Trading-Strategies
        raise RuntimeError("Errore: Impossibile trovare la cartella Backtesting-Trading-Strategies!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import get_path_specify, project_root, main_project, db_path, manage_symbols_path, utils_path, history_market_data_path, capitalization_path, symbols_info_path, marketFiles, history_volume_data

get_path_specify([db_path, f'{main_project}/symbols', ])

from database import insertDataDB as db, connectDB  as connectDB
from work_historical.symbols import manage_symbol as manage_symbol



def downloadANDSaveStocksData(cur, conn, market):
    """
    Scaricamento dei dati e salvataggio nel database: per lo scaricamento viene controllato se in precedenza i dati fossero già scaricati:
    - se lo sono, vengono scaricati solo i dati mancanti a partire dall'ultimo giorno scaricato;
    - se non lo sono, vengono scaricati i dati storici a partire dall'iscrizione del titolo in borsa.
    
    Args:
        cur: cursore per il database
        conn: connessione al database
        market: mercato di riferimento (es. 'NASDAQ', 'NYSE', 'LARG_COMP_EU')
        
    Returns:
        0: se il processo è completato con successo
    """

    if market == 'NASDAQ':
        # selezione dei simboli azionari per la borsa NASDAQ
        symbols = manage_symbol.get_symbols('NASDAQ', -1)
        
        data_dir = Path(f'{history_market_data_path}/NASDAQ') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'NYSE':
        # selezione dei simboli azionari per la borsa NYSE
        symbols = manage_symbol.get_symbols('NYSE', -1)
        
        data_dir = Path(f'{history_market_data_path}/NYSE') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'LARG_COMP_EU':
        # selezione dei simboli azionari per la borsa LARG_COMP_EU
        symbols = manage_symbol.get_symbols('LARG_COMP_EU', -1)

        data_dir = Path(f'{history_market_data_path}/LARG_COMP_EU') # ---> ./ per esec
        data_dir.mkdir(exist_ok=True)
    
    # Scarica i dati per ciascun simbolo
    for titol in symbols:
        # Definizione del percorso del file CSV in cui salvare i dati
        file_path = data_dir / f"{titol}.csv"
        print(file_path)
        
        # Verifica se il file esiste già: significa che i dati sono già stati scaricati in precedenza
        if file_path.exists() and file_path.is_file() :
            
            # viene caricato il file in un DataFrame Pandas, specificando che non ci sono intestazioni
            df = pd.read_csv(file_path, header=None)
            
            # viene presa l'ultima riga del dataframe e viene trasformato in una lista di valori
            ultima_riga = df.iloc[-1].tolist()
            print(f"Ultima riga {ultima_riga}")
            
            # se l'ultimo valore della colonna "Date" è uguale a "Date", significa che il file è vuoto
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                
                # viene definita la data di partenza per scaricare i dati: in questo caso None e il periodo sarà 'max'
                start_date = None
                continue
            
            # Verifica se la data è più vecchia di 1 giorno:
            x = (datetime.now() - timedelta(days=1)) # data di 1 giorno fa
            y = datetime.now()                       # data odierna
            
            # viene trasformata la data dell'ultima riga in un oggetto datetime, con il formato specificato
            last_date = datetime.strptime(ultima_riga[0], '%Y-%m-%d')
            
            # vengono formattate le date a mezzanotte per un confronto corretto
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)
            x = x.strftime('%Y-%m-%d')
            y = y.strftime('%Y-%m-%d')

            # se l'ultima data è uguale a ieri o oggi, non scaricare nuovamente i dati
            if last_date == x or last_date == y:
                # i dati sono già aggiornati fino a ieri/oggi
                print(f'{titol} already downloaded')
                continue
            else:
                # viene impostata la data di partenza per scaricare i dati mancanti a partire dal giorno successivo all'ultimo scaricato
                start_date = last_date + timedelta(days=1)
        
        # Se il file non esiste, scarica l'intero storico
        else:
            logging.info(f"No file found for {titol}, downloading full dataset.")
                    
            # viene definita la data di partenza per scaricare i dati: in questo caso None e il periodo sarà 'max'
            start_date = None
            
        try:
            # se start_date non è None, vengono scaricati i dati mancanti a partire da start_date
            if start_date:
                data = yf.download(titol, start=start_date.strftime('%Y-%m-%d'), interval='1d', auto_adjust=False)
                data.to_csv(file_path, mode='a')
                #data.to_csv(file_path, mode='a', header=None)
                print(f"---------------")
                
                # vengono inseriti i dati nel database
                fillDB(str(file_path), cur, conn, market=market)
                print(f"Data for {titol} savely successfully in DB.")
            
            # se start_date è None, vengono scaricati tutti i dati storici: grazie al parametro period='max'
            else:
                data = yf.download(titol, period="max", interval='1d', auto_adjust=False)
                if not data.empty:
                    data.to_csv(file_path, mode='w')
                    
                    # vengono inseriti i dati nel database
                    fillDB(str(file_path), cur, conn, market=market)
                    logging.info(f"Data for {titol} updated successfully in DB.")
        
        except Exception as e:
            logging.error(f"Error downloading data for {titol}: {e}")
            
    return 0



def fillDB(filename, cur, conn, market):
    """
    Funzione per l'inserimento dei dati nel database: 
    - per ogni file csv contenente i dati di mercato:
        - si scarta la riga di header
        - si estraggono i campi di interesse e si inseriscono nel database (grazie a funzioni specifiche per ogni mercato)
    
    Args:
        filename (str): nome del file csv contenente i dati.
        cur: cursore per il database
        conn: connessione al database
        market: mercato di riferimento (es. 'NASDAQ', 'NYSE', 'LARG_COMP_EU')
    
    Returns:
        0: se l'inserimento è completato con successo
    """
    
    with open(filename, 'r') as file:    
        # per ogni riga del file csv c'è l'inserimento dei dati in un record del database
        for line in file:
                # viene splittata la riga in base al carattere ',' e vengono presi i valori
                infoF = line.split(',')
                # viene controllato che la riga non sia l'intestazione del file, in tal caso non viene inserita nel database
                if infoF[0] != 'Date' and infoF[0] != 'Ticker' and infoF[0] != 'Price':
                    # vengono presi i valori della riga --> price 0, close 1, high 2, low 3, open 4, volume 5
                    
                    symbol = filename.split('/')[13]
                    symbol = symbol.split('.')[0]
                    
                    time_value = infoF[0]
                    
                    close_price = infoF[2]
                    open_price = infoF[5]
                    high_price = infoF[3]
                    low_price = infoF[4]
                    
                    time_frame = '1d'
                    
                    # array che raggruppa i valori per poi inserirli nel DB.
                    rate = [open_price, high_price, low_price, close_price, time_value]
                    print(symbol, rate, '\n')
                    
                    # a seconda del mercato di riferimento vengono inseriti i dati nel database
                    if market == 'NASDAQ':
                        db.insert_data_in_nasdaq_from_yahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'NYSE':
                        db.insert_data_in_nyse_from_yahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'LARG_COMP_EU':
                        db.insert_data_in_large_comp_eu_from_yahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                                
        # chiurusra del file
        file.close()
    return 0
       

def delete_files_about_history_market_data():
    """
    Elimina i file contenenti i dati di market cap per ogni singolo titolo per pulizia.
    Args:
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']

    for m in markets:
        for f in os.listdir(f"{history_market_data_path}/{m}"):
            os.remove(f"{history_market_data_path}/{m}/{f}")
    
    return 0




def get_volume_symbols(marketFiles):
    """
    Scaricati i dati relativi al volume degli scambi per ogni simbolo. Per farlo si utilizza la libreria 'yfinance' che permette di scaricare
    il volume degli scambi per ogni simbolo. Questi dati vengono salvati in file CSV all'interno di percorsi specifici per ogni mercato.
    
    Args:
        marketFiles: lista di file csv contenenti i simboli delle azioni con le relative informazioni più importanti da cui selezionare tutti i simboli d'interesse.
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    
    for f_mark in marketFiles:
        f_mark = str(f_mark)
        print(f_mark)
        
        with open(f'{f_mark}', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
            # Crea un lettore CSV con DictReader
            csv_reader = csv.DictReader(file)
            
            # Estrai i simboli. Sostituisci '/' con '-' per una corretta formattazione
            symbols = [col['Symbol'].replace('/', '-') for col in csv_reader]
            
        # Creare una directory per i file di market cap se non esistente:
        Path(f"{history_volume_data}/NASDAQ/all_volume_symbols").mkdir(parents=True, exist_ok=True)
        Path(f"{history_volume_data}/NASDAQ/top_value").mkdir(parents=True, exist_ok=True)
        
        Path(f"{history_volume_data}/NYSE/all_volume_symbols").mkdir(parents=True, exist_ok=True)
        Path(f"{history_volume_data}/NYSE/top_value").mkdir(parents=True, exist_ok=True)
        
        Path(f"{history_volume_data}/LARG_COMP_EU/all_volume_symbols").mkdir(parents=True, exist_ok=True)
        Path(f"{history_volume_data}/LARG_COMP_EU/top_value").mkdir(parents=True, exist_ok=True)
        
        for sy in symbols:
            
            try:
                stock = yf.Ticker(sy)
                
                if f_mark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv':
                    if f"volume_{sy}.csv" in os.listdir(f"{history_volume_data}/NASDAQ/all_volume_symbols"):
                        print(f"Il file volume_{sy}.csv esiste già")
                        continue
                elif f_mark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                    if f"volume_{sy}.csv" in os.listdir(f"{history_volume_data}/NASDAQ/all_volume_symbols"):
                        print(f"Il file volume_{sy}.csv esiste già")
                        continue
                elif f_mark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                    if f"volume_{sy}.csv" in os.listdir(f"{history_volume_data}/NASDAQ/all_volume_symbols"):
                        print(f"Il file volume_{sy}.csv esiste già")
                        continue
                    
                # Ottieni i dati storici
                historical_data = stock.history(period="max")

                historical_data["Volume"] = historical_data["Volume"]
                
                if historical_data.empty:
                    print(f"Attenzione: Nessun dato disponibile per {sy}, salto...")
                    continue  # Salta il salvataggio se non ci sono dati

                
                # Salva i dati in un file CSV
                if f_mark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv':
                    historical_data["Volume"].to_csv(f"{history_volume_data}/NASDAQ/all_volume_symbols/volume_{sy}.csv")
                    print(f"Dati salvati in market_cap_{sy}.csv")
                    
                elif f_mark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                    historical_data["Volume"].to_csv(f"{history_volume_data}/NYSE/all_volume_symbols/volume_{sy}.csv")
                    print(f"Dati salvati in market_cap_{sy}.csv")
                    
                elif f_mark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                    historical_data["Volume"].to_csv(f"{history_volume_data}/LARG_COMP_EU/all_volume_symbols/volume_{sy}.csv")
                    print(f"Dati salvati in market_cap_{sy}.csv")
            
                time.sleep(1)
                
            except Exception as e:
                print(f"Errore durante il download dei dati per il simbolo {sy}: {e}")
                continue
    return 0



def calculate_avg_volume_k(k):
    """
    Funzione utilizzata per calcolare il volume medio degli scambi per ogni simbolo nei k mesi precedenti ad ogni data.
    
    Args:
        k: numero di mesi precedenti per il calcolo del volume medio
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    
    # Set per i simboli processati in questa esecuzione
    processed_symbols_session = set()
    df_cache = {}  # Cache per memorizzare i DataFrame letti per ogni file
    
    for market in ['NASDAQ', 'NYSE', 'LARG_COMP_EU']:
        # Percorso del file CSV aggregato per il mercato corrente
        output_path = f"{history_volume_data}/{market}/all_volume_symbols/all_with_avg.csv"
        processed_symbols_file = set()
        exist_file = False
        
        try:
            if os.path.exists(output_path) and os.stat(output_path).st_size > 0:
                # Carica SOLO la colonna 'symb' per ottenere i simboli già processati
                #df_symbols = pd.read_csv(output_path, usecols=['symb'])
                #processed_symbols_file = set(df_symbols['symb'])
                
                # Legge riga per riga per ottenere i simboli già processati
                with open(output_path, mode='r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        processed_symbols_file.add(row['symb'])
                exist_file = True
            else:
                exist_file = False
        except FileNotFoundError:
            print(f"Errore: Nessun file CSV disponibile per {market}")
            exist_file = False

        market_dir = f"{history_volume_data}/{market}/all_volume_symbols"
        for f in os.listdir(market_dir):
            if f == '.DS_Store':
                continue
            
            # Estrai il simbolo dal nome del file e normalizzalo (rimuovendo spazi e forzando maiuscolo)
            parts = f.split('.')[0].split('_')
            symbol = parts[1].strip().upper()
            
            # Se il simbolo è già stato processato in questa esecuzione, passa al prossimo
            if symbol in processed_symbols_session:
                print(f"Simbolo {symbol} già processato in questa esecuzione, passo al prossimo...")
                continue

            # Se il simbolo è già presente nel file CSV, salta la sua elaborazione
            if exist_file and symbol in processed_symbols_file:
                print(f"Trovato almeno un record con symb={symbol} già nel file, passo al prossimo...")
                continue
            
            # Registra il simbolo come processato per questa esecuzione
            processed_symbols_session.add(symbol)
            print(f"{len(processed_symbols_session)}: Processo simbolo {symbol}. Simboli processati: {processed_symbols_session}")

            # Lista per accumulare le righe da salvare per il simbolo corrente
            rows = []
            file_path = os.path.join(market_dir, f)
            
            # Usa la cache per evitare di rileggere lo stesso file
            if file_path in df_cache:
                df = df_cache[file_path]
            else:
                df = pd.read_csv(file_path)
                # Converte la colonna 'Date' in datetime una sola volta
                try:
                    df['Date'] = pd.to_datetime(df['Date'].str.split(' ').str[0], format='%Y-%m-%d', errors='coerce')
                    df_cache[file_path] = df
                except KeyError:
                    print(f"Errore: Chiave 'Date' non trovata nel file {file_path}")
                    continue
                
            # Itera sul file per ogni riga (utilizziamo csv.DictReader per evitare di processare il DataFrame riga per riga)
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    try:
                        date = row['Date']
                    except KeyError:
                        print(f"Errore: Chiave 'Date' non trovata nel file {file_path}")
                        continue
                    # Estrai l'anno dalla data (si suppone che il formato sia "YYYY-MM-DD ...")
                    year = date.split(' ')[0].split('-')[0]
                    if year < '1999':
                        continue

                    avg_volume = avg_volume_for_single_symbol(df, date, k)
                    if avg_volume is None:
                        continue
                    rows.append({'symb': symbol, 'date': date.split(' ')[0], 'avg_volume': avg_volume})
            
            # Salva i dati ottenuti nel file CSV aggregato
            write_header = not os.path.exists(output_path) or os.stat(output_path).st_size == 0
            with open(output_path, mode='a', newline='') as file2:
                fieldnames = ['date', 'symb', 'avg_volume']
                writer = csv.DictWriter(file2, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerows(rows)
                
                
            # chiusura del file
        # cambio file
        time.sleep(1) # per evitare di sovraccaricare la CPU
        
    # cambio mercato
    return 0
                    


"""
# Crea un dizionario per ogni simbolo, con chiave il simbolo e la data come e valore il volume medio dei k mesi precedenti
                data = {}
                data_intermediate = {}
                
                for row in csv_reader:
                    symbol = f.split('.')[0]
                    symbol = symbol.split('_')[1]
                    date = row['Date'].split('-')[0]
                    data[(symbol, date)] = {}
                    
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    date_obj_minus_k = date_obj - timedelta(days=30*k)
                    if date_obj_minus_k < datetime.strptime(date_initial, '%Y-%m-%d'):
                        # 2 soluzioni: o si esclude questa data e si va avanti, oppure per questa data si considera il volume precedente anche se non di k mesi
                        #data_obj_minus_k = datetime.strptime(date_initial, '%Y-%m-%d')
                        continue
                    else:
                        for row2 in csv_reader:
                            date2 = row['Date'].split('-')[0]
                            date2_obj = datetime.strptime(date2, '%Y-%m-%d')
                            if date2_obj == date_obj_minus_k:
                                data_intermediate[(symbol, date_obj_minus_k, date_obj)] = {}
                                while date2_obj < date_obj:
                                    if (symbol, date_obj_minus_k, date_obj) in data_intermediate.keys():
                                        data_intermediate[(symbol, date_obj_minus_k, date_obj)] += row2['Volume']
                                    else:   
                                        data_intermediate[(symbol, date_obj_minus_k, date_obj)] = row2['Volume']
                                    
                                    date2_obj += next(csv_reader)['Date']
                                    date2_obj = datetime.strptime(date2_obj, '%Y-%m-%d')
                                    
                                break
                
                    # Calcola il volume medio       
                    data_intermediate[(symbol, date_obj_minus_k, date_obj)] = data_intermediate[(symbol, date_obj_minus_k, date_obj)] / k         
                    data[(symbol, date)] = data_intermediate[(symbol, date_obj_minus_k, date_obj)]
                
                # Salva i dati in un file CSV
                output_path = f"{history_volume_data}/{market}/top_value/topVal.csv"
                    
                with open(output_path, mode='w', newline='') as file:
                    fieldnames = ['date', 'symb', 'avg_volume']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)  # Ora è nel formato corretto!
                               
        # chiurusra del file
    # change market
                    
    return 0
                
"""
                
           
                    
def avg_volume_for_single_symbol(df, test_date_str, k):
    """
    Calcola il volume medio nei k mesi precedenti la test_date per un singolo simbolo.
    
    Args:
        df: DataFrame con i dati letti dal file CSV del simbolo.
        test_date_str: data target in formato 'YYYY-MM-DD' (es. '2001-01-01')
        k: numero di mesi precedenti da considerare
    
    Returns:
        avg_volume: il volume medio, oppure None se non ci sono dati sufficienti.
    """

    # Converte test_date in un Timestamp tz-naive
    test_date = pd.to_datetime(test_date_str).replace(tzinfo=None)
    
    #test_date = pd.to_datetime(test_date_str)
    # Calcola la data di inizio: k mesi indietro (approssimando 30 giorni per mese)
    start_date = test_date - timedelta(days=30*k)
    
    # Filtra il DataFrame per il range desiderato
    #df_period = df[(pd.to_datetime(df['Date']) >= start_date) & (pd.to_datetime(df['Date']) < test_date)]
    df_period = df[(df['Date'] >= start_date) & (df['Date'] < test_date)]
    
    if df_period.empty or df_period.shape[0] < k*20:
        return None
    
    # Calcola la media del volume (convertiamo in int se necessario)
    df_period['Volume'] = pd.to_numeric(df_period['Volume'], errors='coerce')
    avg_volume = df_period['Volume'].mean()
    
    return avg_volume





def order_volume_years():
    """
    Ordina i file CSV di volume dei simboli (salvati in {history_volume_data}/{market}/all_volume_symbols/*) per anno e 
    li salva in una cartella separata ({history_volume_data}/{market}/by_year/...).
    Questo garantisce di avere i dati ordinati per anno e pronti per l'analisi.
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    # Definisco gli anni ammessi in un set per un controllo rapido
    allowed_years = {str(y) for y in range(1999, 2025)}
    
    # Per ogni mercato:
    for market in ['NASDAQ', 'NYSE', 'LARG_COMP_EU']:
        input_path = f"{history_volume_data}/{market}/all_volume_symbols/all_with_avg.csv"
        output_dir = f"{history_volume_data}/{market}/by_year"
        
        # Se la directory di output non esiste, la creo
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Dizionario per gestire i file handle aperti per ciascun anno
        file_handles = {}
        
        try:
            with open(input_path, mode='r') as infile:
                csv_reader = csv.DictReader(infile)
                for row in csv_reader:
                    # Estrazione dell'anno dalla data (si assume formato "YYYY-MM-DD ...")
                    year = row['date'].split('-')[0]
                    if year in allowed_years:
                        # Se il file per quell'anno non è già aperto, lo apro in modalità append
                        if year not in file_handles:
                            file_handles[year] = open(f"{output_dir}/{year}.csv", mode='a')
                        # Scrivo la riga nel file corrispondente
                        symb = row['symb']
                        file_handles[year].write(f"{symb},{row['date']},{row['avg_volume']}\n")
        except FileNotFoundError:
            print(f"File non trovato per il mercato {market}")
        finally:
            # Chiudo tutti i file handle aperti
            for fh in file_handles.values():
                fh.close()
                
    return 0





def preprocess_top_X_for_year():
    """
    Preprocessa i file topX per ogni anno. Nel dettaglio si vanno a ordinare i simboli per ogni data dell'anno considerato in maniera decrescente per volume e si 
    salvano in un file CSV.
    
    Args: 
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    try:
        for m in ['NASDAQ', 'NYSE', 'LARG_COMP_EU']:
            for f in os.listdir(f"{history_volume_data}/{m}/by_year"):
                if f == '.DS_Store': #or f.startswith("top"):
                    continue
                
                with open(f"{history_volume_data}/{m}/by_year/{f}", mode='r') as file:
                    dates = {}
                    for row in file:
                        if row.strip() == 'symbol,date,avg_volume':  # Ignora l'header
                            continue
                        
                        # memorizzo le informazioni delle capitalizzazioni di mercato in delle variabili che poi creeranno il dizionario.
                        symb, date, volume = row.strip().split(',')
                        
                        # Elimina l'ora
                        #date = date[0:-6]
                        
                        # se la data non è presente nel dizionario, la aggiunge, altrimenti aggiunge il simbolo e la capitalizzazione di mercato alla data corrispondente.
                        if date not in dates:
                            dates[date] = [(symb, float(volume))]
                        else:
                            dates[date].append((symb, float(volume)))
                    
                    # Ordina per volume decrescente
                    dates = {k: sorted(v, key=lambda x: x[1], reverse=True) for k, v in dates.items()}
                    
                    # Converti in lista di dizionari
                    rows = []
                    for date, values in dates.items():
                        symbol_market_cap_str = "; ".join([f"{symb[0]}" for symb in values])  # Converti lista in stringa
                        rows.append({'date': date, 'symb': symbol_market_cap_str})
                    
                    # Scrivi nel CSV
                    year = f.split('.')[0]
                    output_path = f"{history_volume_data}/{m}/top_value/topVal{year}.csv"
                    
                    with open(output_path, mode='w', newline='') as file:
                        fieldnames = ['date', 'symb']
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)  # Ora è nel formato corretto!
        
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
        
    finally:
        logging.info(f"Preprocessing completato.")
        return 0








def getMarkCap(marketFiles):    
    """
    Scarica i dati storici di capitalizzazione di mercato per ogni simbolo. Per farlo si utilizza la libreria 'yfinance' che permette di scaricare 
    shares_outstanding: cioè il numero di azioni in circolazione e il prezzo di chiusura. La market cap è data dal prodotto di questi due valori.
    Questi dati vengono salvati in file CSV all'interno di percorsi specifiche per ogni mercato.
    
    Args:
        marketFiles: lista di file csv contenenti i simboli delle azioni con le relative informazioni più importanti da cui selezionare tutti i simboli d'interesse.
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    # Funzione che può essere sostituita in qualche file poiché si ripete
    for fmark in marketFiles:
        fmark = str(fmark)
        print(fmark)
        
        with open(f'{fmark}', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
            # Crea un lettore CSV con DictReader
            csv_reader = csv.DictReader(file)
            
            # Estrai i simboli. Sostituisci '/' con '-' per una corretta formattazione
            symbols = [col['Symbol'].replace('/', '-') for col in csv_reader]
            
        # Creare una directory per i file di market cap se non esistente:
        Path(f"{capitalization_path}/NASDAQ/all_mark_cap").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/NASDAQ/by_year").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/NASDAQ/top_value").mkdir(parents=True, exist_ok=True)
        
        Path(f"{capitalization_path}/NYSE/all_mark_cap").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/NYSE/by_year").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/NYSE/top_value").mkdir(parents=True, exist_ok=True)
        
        Path(f"{capitalization_path}/LARG_COMP_EU/all_mark_cap").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/LARG_COMP_EU/by_year").mkdir(parents=True, exist_ok=True)
        Path(f"{capitalization_path}/LARG_COMP_EU/top_value").mkdir(parents=True, exist_ok=True)
        
        # Per ogni simbolo scarica i dati storici e calcola la market cap (data dalle azioni in circolazione * prezzo di chiusura)
        for sy in symbols:
            # Crea un oggetto Ticker per il simbolo corrente
            stock = yf.Ticker(sy)
                        
            # Se il file market_cap_{sy}.csv esiste già, passa al simbolo successivo
            if fmark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv"':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/NASDAQ/all_mark_cap"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/NYSE/all_mark_cap"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/LARG_COMP_EU/all_mark_cap"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
            
            # Ottieni il numero di azioni in circolazione
            shares_outstanding = stock.info.get("sharesOutstanding")
            
            if shares_outstanding == None:
                print(f"Shares outstanding non trovato per {sy}")
                continue
            
            # Scarica i prezzi storici
            historical_data = stock.history(period="max")  # Ultimi 5 anni

            if historical_data.empty:
                print(f"Dati storici non trovati per {sy}")
                continue
            
            # Calcola la market cap storica: numero di azioni in circolazione * prezzo di chiusura
            historical_data["Market Cap"] = historical_data["Close"] * shares_outstanding

            # Salva i dati in un file CSV
            if fmark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/NASDAQ/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/NYSE/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/LARG_COMP_EU/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
            
            time.sleep(1)

            # Mostra i primi valori
            #print(historical_data[["Close", "Market Cap"]].head())
    return 0
        

def orderMarkCapYears():
    """
    Ordina i file CSV di capitalizzazione di mercato (salvati nel percorso /data/dataset/capitalization/{market}/all_mark_cap/*) per anno e 
    li salva in una cartella separata. (/by_year/...). Questo ci garantisce di avere i dati ordinati per anno e pronti per l'analisi.
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    market = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    
    yearFile = ['1999.csv', '2000.csv', '2001.csv', '2002.csv', '2003.csv', '2004.csv', '2005.csv', '2006.csv', '2007.csv', '2008.csv', '2009.csv', '2010.csv', '2011.csv', 
                '2012.csv', '2013.csv', '2014.csv', '2015.csv', '2016.csv', '2017.csv', '2018.csv', '2019.csv', '2020.csv', '2021.csv', '2022.csv', '2023.csv', '2024.csv']
    
    topFiles = ['topVal1999.csv', 'topVal2000.csv', 'topVal2001.csv', 'topVal2002.csv', 'topVal2003.csv', 'topVal2004.csv', 'topVal2005.csv', 'topVal2006.csv', 'topVal2007.csv', 
                'topVal2008.csv', 'topVal2009.csv', 'topVal2010.csv', 'topVal2011.csv', 'topVal2012.csv', 'topVal2013.csv', 'topVal2014.csv', 'topVal2015.csv', 'topVal2016.csv', 
                'topVal2017.csv', 'topVal2018.csv', 'topVal2019.csv', 'topVal2020.csv', 'topVal2021.csv', 'topVal2022.csv', 'topVal2023.csv', 'topVal2024.csv']
    
    countNasd = countNys = countEur = 0
    
    # Conta il numero di file per ogni mercato per un controllo
    for mark in market:
        for _ in os.listdir(f"{capitalization_path}/{mark}/all_mark_cap"):
            if mark == 'NASDAQ':
                countNasd += 1
            elif mark == 'NYSE':
                countNys += 1
            elif mark == 'LARG_COMP_EU':
                countEur += 1
    
    print("countNasd", ": ", countNasd, ",  " ,"countNys", ": ",  countNys,  ",  " ,"countEu", ": ", countEur)
    
    i = 0
    
    # Per ogni mercato:
    for mark in market:
        # Ordina i file csv per anno
        for f in os.listdir(f"{capitalization_path}/{mark}/all_mark_cap"):
            if (f == '.DS_Store'):
            #if (f in yearFile) or (f == '.DS_Store') or (f in topFiles):
                continue
            i += 1
            print(f"{i}, : {f}")
            
            # Va a riempire i file di capitalizzazione di mercato e li ordina per anno.
            with open(f"{capitalization_path}/{mark}/all_mark_cap/{f}", mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    
                    for d in ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                            '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']:
                        
                        v = row['Date'].split('-')[0]
                        if v == d:
                            fileX = open(f"{capitalization_path}/{mark}/by_year/{d}.csv", mode='a')
                            symb = (f.split('.')[0]).split('_')[2]
                            fileX.write(symb + ',' + row['Date'] + ',' + row['Market Cap'] + '\n')
                            fileX.close()
                        #print(row['Symbol'], row['Market Cap'])
            print()

        i = 0
    return 0


def deleteFilesAboutSingleTitles():
    """
    Elimina i file contenenti i dati di capitalizzazione di mercato per ogni singolo titolo per pulizia.
    
    Args: 
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    yearFile = ['1999.csv', '2000.csv', '2001.csv', '2002.csv', '2003.csv', '2004.csv', '2005.csv', '2006.csv', '2007.csv', '2008.csv', '2009.csv', '2010.csv', '2011.csv', 
                '2012.csv', '2013.csv', '2014.csv', '2015.csv', '2016.csv', '2017.csv', '2018.csv', '2019.csv', '2020.csv', '2021.csv', '2022.csv', '2023.csv', '2024.csv']

    for m in markets:
        for f in os.listdir(f"{capitalization_path}/{m}/all_mark_cap"):
            os.remove(f"{capitalization_path}/{m}/all_mark_cap/{f}")
    
    return 0

             
def preprocess_topX_for_year():
    """
    Preprocessa i file topX per ogni anno. Nel dettaglio si vanno a ordinare i simboli per ogni data dell'anno considerato in maniera decrescente per capitalizzazione e si 
    salvano in un file CSV.
    
    Args: 
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU'] #markets = ['LARG_COMP_EU']
    try:
        for m in markets:
            for f in os.listdir(f"{capitalization_path}/{m}/by_year"):
                if f == '.DS_Store': #or f.startswith("top"):
                    continue
                
                with open(f"{capitalization_path}/{m}/by_year/{f}", mode='r') as file:
                    dates = {}
                    for row in file:
                        if row.strip() == 'symbol,date,market_cap':  # Ignora l'header
                            continue
                        
                        # memorizzo le informazioni delle capitalizzazioni di mercato in delle variabili che poi creeranno il dizionario.
                        symb, date, mrkcap = row.strip().split(',')
                        
                        # Elimina l'ora
                        date = date[0:-6]
                        
                        # se la data non è presente nel dizionario, la aggiunge, altrimenti aggiunge il simbolo e la capitalizzazione di mercato alla data corrispondente.
                        if date not in dates:
                            dates[date] = [(symb, float(mrkcap))]
                        else:
                            dates[date].append((symb, float(mrkcap)))
                    
                    # Ordina per market cap decrescente
                    dates = {k: sorted(v, key=lambda x: x[1], reverse=True) for k, v in dates.items()}
                    
                    # Converti in lista di dizionari
                    rows = []
                    for date, values in dates.items():
                        symbol_market_cap_str = "; ".join([f"{symb[0]}" for symb in values])  # Converti lista in stringa
                        rows.append({'date': date, 'symb': symbol_market_cap_str})
                    
                    # Scrivi nel CSV
                    year = f.split('.')[0]
                    output_path = f"{capitalization_path}/{m}/top_value/topVal{year}.csv"
                    
                    with open(output_path, mode='w', newline='') as file:
                        fieldnames = ['date', 'symb']
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)  # Ora è nel formato corretto!
        
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
        
    finally:
        logging.info(f"Preprocessing completato.")
        return 0



                

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_data_backtesting()
        
        # Scarica e salva i dati per i mercati specificati
        #market = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
        market = ['NYSE', 'LARG_COMP_EU']
        #for m in market:
        #    downloadANDSaveStocksData(cur, conn, m)
                
        #delete_files_about_history_market_data()
        #getMarkCap(marketFiles)
        #orderMarkCapYears()
        #deleteFilesAboutSingleTitles()
        #preprocess_topX_for_year()
        calculate_avg_volume_k(6)
        #get_volume_symbols(marketFiles)
        order_volume_years()
        preprocess_top_X_for_year()
        
        
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}")
    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
    
    # Chiudi il cursore e la connessione
    cur.close()
    conn.close()
    
    return 0



if __name__ == '__main__':
    main()  # Eseguire il trading agent