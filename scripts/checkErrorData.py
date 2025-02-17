import sys
import logging
import os
from pathlib import Path
import traceback


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

# Ora possiamo importare `config`
get_path_specify([db_path, f'{main_project}/data/anomalies'])

# Importa i moduli personalizzati
from work_historical.database import connectDB


def checkErr(initial_date, end_date, market_data):
    """
    Funzione utilizzata per controllare se ci sono anomalie nei dati di mercato, scaricati dall'agente 1 e salvati nel database.
    
    Args:
        - initial_date: data iniziale del periodo di controllo;
        - end_date: data finale del periodo di controllo;
        - market: mercato da controllare.
        
    Returns:
        - data_by_symbol: dizionario contenente i simboli come chiave e come valore una lista di tuple contenente il tempo, il prezzo di apertura e il prezzo massimo.
    
    """
    try:
        # Connessione al database
        cur, conn = connectDB.connect_data_backtesting()
        
        # recupero dal database del simbolo, del tempo e del prezzo di apertura e massimo, per controllari se ci siano variazioni enormi tra il prezzo di apertura e massimo
        # per un simbolo in un intervallo di tempo ---> errore di scaricamento di dati di mercato oppure evento che scatena un innalzamento del prezzo.
        cur.execute(f"""SELECT symbol, time_value, open_price, high_price 
                    FROM {market_data} 
                    WHERE time_value 
                    BETWEEN '{initial_date}' AND '{end_date}'""")
        
        # Dizionario: {symbol: [(time_value_it, open_price, high_price), ...]}
        data_by_symbol = {}
        for symbol, time_value_it, open_price, high_price in cur.fetchall():
            if symbol not in data_by_symbol.keys():
                data_by_symbol[symbol] = [(time_value_it, open_price, high_price)]
            else:
                data_by_symbol[symbol].append((time_value_it, open_price, high_price))
                
        # Soglia di variazione di open_price
        threshold_abs = 1000
        threshold_pct = 30 #--> 30*100% = 3000% di variazione
        
        # Apriamo il file di report in modalità append        
        with open(f'{main_project}/data/anomalies/errorData_{market_data}.txt', 'a') as file_out:
            file_out.write(f"---------------------------------------------\nControllo anomalie per il mercato: {market_data}\n")
            for symbol, values in data_by_symbol.items():
                # Ordiniamo per data (se non già ordinati)
                values.sort(key=lambda x: x[0])

                # Estraiamo open_price e high_price
                open_prices = [v[1] for v in values]
                high_prices = [v[2] for v in values]

                # 1) Controllo semplice su min e max open price:
                if (max(open_prices) - min(open_prices)) > threshold_abs:
                    # se la differenza tra il minimo e il massimo open price supera una soglia, 
                    # significa che c'è stata una variazione significativa dei prezzi.
                    
                    min_open = min(open_prices)
                    max_high = max(high_prices)
                    
                    # Trova le date corrispondenti
                    min_date = [v[0] for v in values if v[1] == min_open][0]
                    max_date = [v[0] for v in values if v[2] == max_high][0]
                    
                    # Scrivi il report
                    file_out.write(
                        f"Symbol: {symbol}\n"
                        f"Data: Minimum open price: {min_open} in date: {min_date}\n"
                        f"      Maximum high price: {max_high} in date: {max_date}\n\n"
                    )
                
                # 2) Controllo di variazione giornaliera
                anomalies = detect_anomalies_same_and_next_day(values, threshold_abs=threshold_abs, threshold_pct=threshold_pct)
                
                # Se ci sono anomalie, scriviamo un report
                if anomalies:
                    file_out.write(f"SIMBOLO: {symbol}\n")
                    for anom in anomalies:
                        file_out.write(
                            f"  Data: {anom['date_i']} - open_i={anom['open_i']} - high_i={anom['high_i']}\n"
                            f"  Data next: {anom['date_next']} - high_next={anom['high_next']}\n"
                            f"    diff_same_day={anom['diff_same_day']:.2f} "
                            f"({anom['diff_same_day_pct']*100:.2f}%)\n"
                            f"    diff_next_day={anom['diff_next_day']:.2f} "
                            f"({anom['diff_next_day_pct']*100:.2f}%)\n"
                            "\n"
                        )
                    file_out.write("------------------------------------------------------\n")
        
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        logging.shutdown()
        return data_by_symbol
    
    

def detect_anomalies_same_and_next_day(data, threshold_abs=1000, threshold_pct=30):
    """
    Funzione per rilevare anomalie nei dati di mercato in base alla differenza tra il prezzo di apertura e il prezzo massimo 
    nella stessa giornata e il giorno successivo.
    
    Args:
        - data: lista di tuple (time_value, open_price, high_price) ----> si assume sia ORDINATA per data.
        - threshold_abs: soglia di differenza assoluta oltre la quale considerare un'anomalia
        - threshold_pct: soglia di variazione percentuale oltre la quale considerare un'anomalia

    Returns: 
        - anomalies: lista di dizionari con i dettagli delle anomalie rilevate
    """
    
    anomalies = []
    
    # Scorriamo fino al penultimo elemento (per poter confrontare con i+1)
    for i in range(len(data) - 1):
        date_i, open_i, high_i = data[i]
        date_next, open_next, high_next = data[i + 1]
        
        # -- Confronto stesso giorno dei prezzi iniziale e più alto (open_i vs high_i) --
        diff_same_day = abs(open_i - high_i)
        diff_same_day_pct = (diff_same_day / abs(open_i)) if open_i != 0 else 0
        
        # -- Confronto giorno successivo dei prezzi iniziale e più alto (open_i vs high_(i+1)) --
        diff_next_day = abs(open_i - high_next)
        diff_next_day_pct = (diff_next_day / abs(open_i)) if open_i != 0 else 0
        
        # Controlli su percentuale
        anomaly_same_day =  (diff_same_day_pct > threshold_pct)
        anomaly_next_day =  (diff_next_day_pct > threshold_pct)
        
        if anomaly_same_day or anomaly_next_day:
            anomalies.append({
                "date_i": date_i,
                "open_i": open_i,
                "high_i": high_i,
                "date_next": date_next,
                "high_next": high_next,
                "diff_same_day": diff_same_day,
                "diff_same_day_pct": diff_same_day_pct,
                "diff_next_day": diff_next_day,
                "diff_next_day_pct": diff_next_day_pct
            })
    
    return anomalies


    
    

if __name__ == '__main__':
    dates = [('1999-01-01 00:00:00', '2000-01-01 00:00:00'), ('2000-01-01 00:00:00', '2001-01-01 00:00:00'), ('2001-01-01 00:00:00', '2002-01-01 00:00:00'),
             ('2002-01-01 00:00:00', '2003-01-01 00:00:00'), ('2003-01-01 00:00:00', '2004-01-01 00:00:00'), ('2004-01-01 00:00:00', '2005-01-01 00:00:00'),
             ('2006-01-01 00:00:00', '2007-01-01 00:00:00'), ('2007-01-01 00:00:00', '2008-01-01 00:00:00'), ('2008-01-01 00:00:00', '2009-01-01 00:00:00'),
             ('2010-01-01 00:00:00', '2011-01-01 00:00:00'), ('2011-01-01 00:00:00', '2012-01-01 00:00:00'), ('2012-01-01 00:00:00', '2013-01-01 00:00:00'),
             ('2014-01-01 00:00:00', '2015-01-01 00:00:00'), ('2015-01-01 00:00:00', '2016-01-01 00:00:00'), ('2016-01-01 00:00:00', '2017-01-01 00:00:00'),
             ('2018-01-01 00:00:00', '2019-01-01 00:00:00'), ('2019-01-01 00:00:00', '2020-01-01 00:00:00'), ('2020-01-01 00:00:00', '2021-01-01 00:00:00'),
             ('2022-01-01 00:00:00', '2023-01-01 00:00:00'), ('2023-01-01 00:00:00', '2024-01-01 00:00:00'), ('2024-01-01 00:00:00', '2025-01-01 00:00:00')]   
    
    market_data = ['data_market_nasdaq_symbols', 'data_market_nyse_symbols', 'data_market_larg_comp_eu_symbols']
    
    for mark in market_data:
        for date in dates:
            checkErr(date[0], date[1], mark) # 1 anno