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

# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'trading-agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import get_path_specify, project_root, main_project, db_path, manage_symbols_path, utils_path, history_market_data_path, capitalization_path, symbols_info_path, marketFiles 

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
        getMarkCap(marketFiles)
        orderMarkCapYears()
        deleteFilesAboutSingleTitles()
        preprocess_topX_for_year()
        
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