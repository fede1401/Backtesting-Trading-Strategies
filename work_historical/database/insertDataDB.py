from datetime import datetime, timedelta
import psycopg2 
import numpy as np
#import db.connectDB as connectDB
import logging
#import MetaTrader5 as mt5


# Funzione per convertire tipi di dati numpy in tipi di dati Python
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item() # Restituisce un valore scalare dal tipo numpy
    return value # Restituisce direttamente il valore se non è di tipo numpy

################################################################################################

# Funzione per inserire i dati delle azioni NASDAQ nel database
def insertInNasdaqActions(symbol, time_frame, rates, cur):
    for rate in rates:
        print(rate)
        try:
            # Calcola il tempo in formato italiano (sottrae 3 ore dall'orario UNIX)
            time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Calcola il tempo in formato newyorkese (sottrae 9 ore dall'orario UNIX)
            time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)

            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO nasdaq_actions (symbol, time_frame, time_value_IT, time_value_NY, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value_IT, time_value_NY, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    time_value_it,
                    time_value_ny,
                    convert_numpy_to_python(rate['open']),
                    convert_numpy_to_python(rate['high']),
                    convert_numpy_to_python(rate['low']),
                    convert_numpy_to_python(rate['close']),
                    convert_numpy_to_python(rate['tick_volume']),
                    convert_numpy_to_python(rate['spread']),
                    convert_numpy_to_python(rate['real_volume'])
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        finally:
            # Chiude la connessione al database
            cur.close()
            


################################################################################################


# Funzione per inserire i dati dei titoli azionari del NASDAQ scaricati con Yahoo!Finance nel database
def insert_data_in_nasdaq_from_yahoo(symbol, time_frame, rate, cur, conn):
    try:

            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO data_market_nasdaq_symbols (symbol, time_frame, time_value, open_price, high_price, low_price, close_price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[4], '%Y-%m-%d'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3]),
                )
            )        
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[4], '%Y-%m-%d')} salvati nel db.\n")
    return 0

################################################################################################################################################################################################

# Funzione per inserire i dati dei titoli azionari del NYSE scaricati con Yahoo!Finance nel database
def insert_data_in_nyse_from_yahoo(symbol, time_frame, rate, cur, conn):
    try:
            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO data_market_nyse_symbols (symbol, time_frame, time_value, open_price, high_price, low_price, close_price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[4], '%Y-%m-%d'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3])
                )
            )        
            
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[4], '%Y-%m-%d')} salvati nel db.\n")
    return 0


################################################################################################################################################################################################


# Funzione per inserire i dati dei titoli azionari del NYSE scaricati con Yahoo!Finance nel database
def insert_data_in_large_comp_eu_from_yahoo(symbol, time_frame, rate, cur, conn):
    try:
            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO data_market_larg_comp_eu_symbols (symbol, time_frame, time_value, open_price, high_price, low_price, close_price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[4], '%Y-%m-%d'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3])
                )
            )        
            
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[4], '%Y-%m-%d')} salvati nel db.\n")
    return 0

################################################################################################################################################################################################

# Funzione per inserire un acquisto di un simbolo azionario nel database
def insert_purchase (date, ticket, volume, symbol, price, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Purchase
            cur.execute(
                "INSERT INTO purchase (purchase_date, created_at, ticket, volume, symbol, price) "
                "VALUES (%s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (purchase_date, created_at, symbol) DO NOTHING",
                (
                    date,
                    datetime.now(),
                    ticket,
                    convert_numpy_to_python(volume),
                    symbol,
                    convert_numpy_to_python(price)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        #print("Dati relative all'acquisto dell'azione salvati nel db.\n")

        
################################################################################################################################################################################################


# Funzione per inserire una vendita (chiusura di una posizione) di un simbolo azionario nel database
def insert_sale (date_sale, date_purch, ticket_pur, ticket_sale, volume, symbol, price_sale, price_purchase, profit_USD, profit_perc, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Sale
            cur.execute(
                """
                INSERT INTO sale (sale_date, purchase_date, created_at, ticket_purchase, ticket_sale, symbol, price_sale, 
                                    price_purchase, volume, profit_usd, profit_perc)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (sale_date, created_at, symbol) DO NOTHING
                """,
                (
                    date_sale,
                    date_purch,
                    datetime.now(),
                    ticket_pur,
                    ticket_sale,
                    symbol,
                    convert_numpy_to_python(price_sale),
                    convert_numpy_to_python(price_purchase),
                    convert_numpy_to_python(volume), 
                    convert_numpy_to_python(profit_USD),
                    convert_numpy_to_python(profit_perc)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
        #print("Dati relativi alla vendita dell'azione salvati nel db.\n")

       
################################################################################################################################################################################################ 


def insert_in_data_testing(id, agent, number_test, initial_date, end_date, initial_budget, profit_perc, budg_with_profit_USD , market, n_purchase, n_sale, middle_time_sale_second, middle_time_sale_day, title_better_profit, title_worse_profit, notes, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
            cur.execute(
                """
                INSERT INTO testing_data (id, agent, number_test, market, initial_date, end_date, initial_budget_usd, budget_with_profit_usd,
                                    profit_perc, n_purchase, n_sale, avg_sale_time_seconds, avg_sale_time_days, best_profit_symbol, worst_profit_symbol, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) 
                """,
                (
                    convert_numpy_to_python(id),
                    agent, 
                    convert_numpy_to_python(number_test),
                    market,
                    initial_date, 
                    end_date,
                    convert_numpy_to_python(initial_budget),
                    convert_numpy_to_python(round(budg_with_profit_USD, 4)),
                    convert_numpy_to_python(profit_perc),
                    convert_numpy_to_python(n_purchase),
                    convert_numpy_to_python(n_sale),
                    convert_numpy_to_python(round(middle_time_sale_second, 4)),
                    convert_numpy_to_python(round(middle_time_sale_day, 4)),
                    title_better_profit, 
                    title_worse_profit,
                    notes
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        #print("Dati relativi al  salvati nel db.\n")


################################################################################################################################################################################################

# idTest, "agent2", roi=mean_profit_perc, devstandard = std_deviation, var= varianza, middleProfitUSD =mean_profit_usd,
                                                  #middleSale = mean_sale, middlePurchase = mean_purchase, middleTimeSale = mean_time_sale, middletitleBetterProfit = mean_titleBetterProfit,
                                                   # middletitleWorseProfit = mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

def insert_in_data_simulation(test_id, agent, mean_perc_profit, std_dev, variance,initial_budget, mean_budget_with_profit_usd, avg_sale, avg_purchase, avg_time_sale, best_symbol, worst_symbol, timestamp_in, timestamp_fin, notes, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
            cur.execute(
                """
                INSERT INTO simulation_data (test_id, agent, mean_perc_profit, std_dev, variance, initial_budget, mean_budget_with_profit_usd, avg_sale, avg_purchase, avg_time_sale, best_symbol, worst_symbol, timestamp_in, timestamp_fin, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s, %s) 
                """,
                (
                    convert_numpy_to_python(test_id),
                    agent, 
                    convert_numpy_to_python(round(mean_perc_profit, 4)),
                    convert_numpy_to_python(round(std_dev, 4)),
                    convert_numpy_to_python(round(variance, 4)),
                    convert_numpy_to_python(initial_budget),
                    convert_numpy_to_python(round(mean_budget_with_profit_usd, 4)),
                    convert_numpy_to_python(round(avg_sale, 4)),
                    convert_numpy_to_python(round(avg_purchase, 4)),
                    convert_numpy_to_python(round(avg_time_sale, 4)),
                    best_symbol,
                    worst_symbol,
                    timestamp_in,
                    timestamp_fin,
                    notes
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        #print("Dati relativi al  salvati nel db.\n")

################################################################################################################################################################################################