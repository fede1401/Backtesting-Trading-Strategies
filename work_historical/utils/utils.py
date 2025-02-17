import sys

sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
# sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent1')
# sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent2')
# sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

import psycopg2
import random
import logging
import pytz
from datetime import datetime, time, timedelta
import time as time_module
import csv
import math
from math import exp
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback
import numpy as np
import time

from pathlib import Path


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
get_path_specify([db_path, symbols_info_path])



# min date for nasdaq and nyse: 1962-01-02 00:00:00 | min date for large: 1972-06-01 00:00:00
# max date for nasdaq, nyse and lage: 2024-12-30 00:00:00
def getRandomDate(cursor):
    # Seleziona un giorno casuale all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla
    # data massima presente nel database cursor.execute("SELECT MAX(time_value_it) - INTERVAL '1 year 2 month 1 days'
    # FROM nasdaq_actions;") max_date = cursor.fetchone()[0]
    max_date = datetime(2023, 11, 1, 0, 0, 0)

    # Determina la data minima (ad esempio, la data più antica nella tabella)
    # cursor.execute("SELECT MIN(time_value_it) + INTERVAL '23 year 11 month 8 day' FROM nasdaq_actions;")
    # min_date = cursor.fetchone()[0]
    min_date = datetime(1999, 1, 1, 0, 0, 0)

    # Seleziona una data casuale all'interno dell'intervallo cursor.execute("SELECT time_value_it FROM nasdaq_actions
    # WHERE time_value_it BETWEEN %s AND %s ORDER BY RANDOM() LIMIT 1;", (min_date, max_date)) trade_date =
    # cursor.fetchone()[0] trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

    # Calcola una data casuale tra min_date e max_date
    while True:
        random_days = random.randint(0, (max_date - min_date).days)
        random_date = min_date + timedelta(days=random_days)

        # Verifica se la data casuale esiste nel database
        cursor.execute(f"SELECT time_value_it FROM nyse_actions WHERE time_value_it = '{random_date}';")
        result = cursor.fetchone()

        if result:  # Data trovata nel database
            # Verifica se la data casuale esiste nel database
            cursor.execute(f"SELECT time_value_it FROM larg_comp_eu_actions WHERE time_value_it = '{random_date}';")
            result1 = cursor.fetchone()

            if result1:
                # Verifica se la data casuale esiste nel database
                cursor.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it = '{random_date}';")
                result2 = cursor.fetchone()

                if result2:
                    trade_date = result[0]

                    trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

                    # Converti la stringa in un oggetto datetime
                    initial_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Aggiungi 1 anno usando relativedelta
                    end_date = initial_date + relativedelta(years=1)
                    # Converti end_date in una stringa formattata
                    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

                    return trade_date, initial_date, end_date

                else:  # Data non trovata nel database
                    continue

            else:  # Data non trovata nel database
                continue
        else:  # Data non trovata nel database
            continue


# for example: 1999-01-01 00:00:00
def getRandomDateBetween(cursor, min_date, max_date):
    # Calcola una data casuale tra min_date e max_date
    while True:
        random_days = random.randint(0, (max_date - min_date).days)
        random_date = min_date + timedelta(days=random_days)

        # Verifica se la data casuale esiste nel database
        cursor.execute(f"SELECT time_value_it FROM nyse_actions WHERE time_value_it = '{random_date}';")
        result = cursor.fetchone()

        if result:  # Data trovata nel database
            # Verifica se la data casuale esiste nel database
            cursor.execute(f"SELECT time_value_it FROM larg_comp_eu_actions WHERE time_value_it = '{random_date}';")
            result1 = cursor.fetchone()

            if result1:
                # Verifica se la data casuale esiste nel database
                cursor.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it = '{random_date}';")
                result2 = cursor.fetchone()

                if result2:
                    trade_date = result[0]

                    trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

                    # Converti la stringa in un oggetto datetime
                    initial_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Aggiungi 1 anno usando relativedelta
                    end_date = initial_date + relativedelta(years=1)
                    # Converti end_date in una stringa formattata
                    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

                    return trade_date, initial_date, end_date

                else:  # Data non trovata nel database
                    continue

            else:  # Data non trovata nel database
                continue
        else:  # Data non trovata nel database
            continue


def generateiRandomDates(cursor, i):
    # Genera i date casuali all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla data massima presente nel database
    result = []
    for _ in range(i):
        trade_date, initial_date, end_date = getRandomDate(cursor)
        result.append((trade_date, initial_date, end_date))
    return result


def getRandomDate2(cursor):
    # Data massima e minima
    max_date = datetime(2023, 11, 20, 0, 0, 0)
    min_date = datetime(1999, 1, 1, 0, 0, 0)

    # Calcola l'intervallo in giorni
    total_days = (max_date - min_date).days

    # Funzione di peso: assegna probabilità più alte verso date recenti
    def weight_function(day):
        # day è l'indice del giorno rispetto alla min_date
        # Ad esempio, day=0 -> min_date, day=total_days -> max_date
        bias_factor = 0.0005  # Aumenta o diminuisci questo valore per regolare il bias
        return exp(bias_factor * day)

    # Genera una lista di pesi
    weights = [weight_function(day) for day in range(total_days + 1)]

    # Normalizza i pesi
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Seleziona un giorno basato sul peso
    random_day = random.choices(range(total_days + 1), weights=weights, k=1)[0]
    random_date = min_date + timedelta(days=random_day)

    # Verifica se la data casuale esiste nel database
    cursor.execute(f"SELECT time_value_it FROM nyse_actions WHERE time_value_it = '{random_date}';")
    result = cursor.fetchone()

    if result:
        # Ritorna la data trovata
        trade_date = result[0]
        trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

        # Converti la stringa in un oggetto datetime
        initial_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

        # Aggiungi 1 anno usando relativedelta
        end_date = initial_date + relativedelta(years=1)

        # Converti end_date in una stringa formattata
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        return trade_date, initial_date, end_date
    else:
        # Se la data non è valida, riprova
        return getRandomDate(cursor)

def generateiRandomDates2(cursor, i):
    result = []
    for _ in range(i):
        trade_date, initial_date, end_date = getRandomDate2(cursor)
        result.append((trade_date, initial_date, end_date))

    # Ordina le date in ordine crescente in base a `initial_date`
    result.sort(key=lambda x: x[1])  # x[1] è `initial_date`

    return result

###############################################################

def getLastIdTest(cur):
    """
    Funzione utilizzata per recuperare l'ultimo id presente ai testing effettuati e restituire il nuovo che dovrà esere utilizzato.
    
    Args:
        - cur: cursore relativo alla connessione del database.
        
    Returns:
        - l'id che sarà utilizzato per il test attuale.
    """
    # Recupera l'ultimo id del testing
    cur.execute("SELECT id FROM Testing ORDER BY id desc;")
    idTest = cur.fetchone()

    if idTest == None:
        idTest = 0
    else:
        idTest = idTest[0]
        idTest += 1
    return idTest

###############################################################

def clearSomeTablesDB(cur, conn):
    cur.execute("DELETE FROM sale;")
    conn.commit()

    cur.execute("DELETE FROM purchase;")
    conn.commit()

    cur.execute("DELETE FROM logindate;")
    conn.commit()

    cur.execute("DELETE FROM datatrader;")
    conn.commit()

###############################################################

def getValueMiddlePrice(chosen_symbol, market, date, cur):
    start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - timedelta(days=50)
    cur.execute(
        f"SELECT close_price FROM {market} WHERE symbol = '{chosen_symbol}' AND time_value_it BETWEEN '{start_date}' AND '{date}';")
    prices = [row[0] for row in cur.fetchall()]

    if len(prices) == 0:
        return 0  # O gestisci come preferisci il caso senza dati

    return sum(prices) / len(prices)

###############################################################

