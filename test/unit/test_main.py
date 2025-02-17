import sys
from datetime import datetime
import csv
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
get_path_specify([db_path, f'{main_project}/symbols', main_project, utils_path])

from work_historical.database import connectDB

sys.path.append(f'{main_project}/agent1_downloadANDinsertDATA_DB')
sys.path.append(f'{main_project}/agent2')
sys.path.append(f'{main_project}/agent3')
sys.path.append(f'{main_project}/agent4')
sys.path.append(f'{main_project}/agent5_variationNumberTitle')
sys.path.append(f'{main_project}/agent6_selectionSector')
sys.path.append(f'{main_project}/agent7_larger_time_window')
sys.path.append(f'{main_project}/agent8_trailing_stop_loss')

from work_historical.agents import agent1_downloadANDinsertDATA_DB, agent2, agent3, agent4, agent5_variationNumberTitle, agent6_selectionSector, agent7_larger_time_window, agent8_trailing_stop_loss

# Recupero delle capitalizzazioni di mercato per i simboli azionari di ogni mercato.
Path = f'{project_root}/logs'
if not os.path.exists(Path):
    os.mkdir(f'{project_root}/logs')


#import work_historical.agents.agent1_downloadANDinsertDATA_DB
import work_historical.agents.agent2.agent2_markCapDayInitial as agent2_markCapDayInitial
import work_historical.agents.agent2.agent2_selectRandom as agent2_selectRandom
import work_historical.agents.agent3.agent3_markCapDayInitial as agent3_markCapDayInitial
import work_historical.agents.agent3.agent3_selectRandom as agent3_selectRandom
import work_historical.agents.agent4.agent4_markCapDayInitial as agent4_markCapDayInitial
import work_historical.agents.agent4.agent4_selectRandom as agent4_selectRandom
import work_historical.agents.agent5_variationNumberTitle.agent5_markCapDayInitial as agent5_markCapDayInitial
import work_historical.agents.agent5_variationNumberTitle.agent5_selectRandom as agent5_selectRandom
import work_historical.agents.agent6_selectionSector.agent6_markCapDayInitial as agent6_markCapDayInitial
import work_historical.agents.agent7_larger_time_window.agent7_markCapDayInitial as agent7_markCapDayInitial
import work_historical.agents.agent7_larger_time_window.agent7_selectRandom as agent7_selectRandom
import work_historical.agents.agent8_trailing_stop_loss.agent8_markCapDayInitial as agent8_markCapDayInitial
import work_historical.agents.agent8_trailing_stop_loss.agent8_selectRandom as agent8_selectRandom

#from work_historical.utils import generateiRandomDates2
    

# Crea un logger personalizzato per il main
logger_main = logging.getLogger('main')
logger_main.setLevel(logging.INFO)

# Evita di aggiungere più handler in esecuzioni ripetute
if not logger_main.hasHandlers():
    file_handler = logging.FileHandler(f"{project_root}/logs/main.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger_main.addHandler(file_handler)

logger_main.propagate = False  # Evita la propagazione


def main():
    cur, conn = connectDB.connect_nasdaq()
    #datesToTrade1 = generateiRandomDates2(cur, 80)
        
    logger_main.info("Start simulations!\n")
    
    """cur.execute("select initial_date, end_date from testing where id=1 order by initial_date;")
    datesToTrade1 = {(d[0].strftime('%Y-%m-%d %H:%M:%S'), d[0], d[1].strftime('%Y-%m-%d %H:%M:%S')) for d in cur.fetchall()} 
    datesToTrade1 = list(datesToTrade1)
    datesToTrade1.append(('2008-11-17 00:00:00', datetime.strptime('2008-11-17 00:00:00', '%Y-%m-%d %H:%M:%S'), '2009-11-17 00:00:00'))
    datesToTrade1.append(('2023-05-19 00:00:00', datetime.strptime('2023-05-19 00:00:00', '%Y-%m-%d %H:%M:%S'), '2023-05-19 00:00:00'))
    print(datesToTrade1)
    """
    datesToTrade1 = [('1999-12-17 00:00:00', datetime(1999, 12, 17, 0, 0), '2000-12-17 00:00:00'), ('2000-05-19 00:00:00', datetime(2000, 5, 19, 0, 0), '2001-05-19 00:00:00'), 
                     ('2000-06-07 00:00:00', datetime(2000, 6, 7, 0, 0), '2001-06-07 00:00:00'), ('2000-10-24 00:00:00', datetime(2000, 10, 24, 0, 0), '2001-10-24 00:00:00'), 
                     ('2002-04-29 00:00:00', datetime(2002, 4, 29, 0, 0), '2003-04-29 00:00:00'), ('2002-09-30 00:00:00', datetime(2002, 9, 30, 0, 0), '2003-09-30 00:00:00'), 
                     ('2002-11-25 00:00:00', datetime(2002, 11, 25, 0, 0), '2003-11-25 00:00:00'), ('2003-07-10 00:00:00', datetime(2003, 7, 10, 0, 0), '2004-07-10 00:00:00'), 
                     ('2004-06-02 00:00:00', datetime(2004, 6, 2, 0, 0), '2005-06-02 00:00:00'), ('2004-08-30 00:00:00', datetime(2004, 8, 30, 0, 0), '2005-08-30 00:00:00'), 
                     ('2005-11-23 00:00:00', datetime(2005, 11, 23, 0, 0), '2006-11-23 00:00:00'), ('2006-03-03 00:00:00', datetime(2006, 3, 3, 0, 0), '2007-03-03 00:00:00'), 
                     ('2006-12-29 00:00:00', datetime(2006, 12, 29, 0, 0), '2007-12-29 00:00:00'), ('2007-08-27 00:00:00', datetime(2007, 8, 27, 0, 0), '2008-08-27 00:00:00'), 
                     ('2008-10-08 00:00:00', datetime(2008, 10, 8, 0, 0), '2009-10-08 00:00:00'), ('2009-05-18 00:00:00', datetime(2009, 5, 18, 0, 0), '2010-05-18 00:00:00'), 
                     ('2009-06-29 00:00:00', datetime(2009, 6, 29, 0, 0), '2010-06-29 00:00:00'), ('2011-03-24 00:00:00', datetime(2011, 3, 24, 0, 0), '2012-03-24 00:00:00'), 
                     ('2011-06-03 00:00:00', datetime(2011, 6, 3, 0, 0), '2012-06-03 00:00:00'), ('2011-09-29 00:00:00', datetime(2011, 9, 29, 0, 0), '2012-09-29 00:00:00'), 
                     ('2012-08-24 00:00:00', datetime(2012, 8, 24, 0, 0), '2013-08-24 00:00:00'), ('2013-03-19 00:00:00', datetime(2013, 3, 19, 0, 0), '2014-03-19 00:00:00'), 
                     ('2014-05-14 00:00:00', datetime(2014, 5, 14, 0, 0), '2015-05-14 00:00:00'), ('2014-08-26 00:00:00', datetime(2014, 8, 26, 0, 0), '2015-08-26 00:00:00'), 
                     ('2014-10-14 00:00:00', datetime(2014, 10, 14, 0, 0), '2015-10-14 00:00:00'), ('2015-12-09 00:00:00', datetime(2015, 12, 9, 0, 0), '2016-12-09 00:00:00'), 
                     ('2016-02-09 00:00:00', datetime(2016, 2, 9, 0, 0), '2017-02-09 00:00:00'), ('2016-04-07 00:00:00', datetime(2016, 4, 7, 0, 0), '2017-04-07 00:00:00'), 
                     ('2016-05-04 00:00:00', datetime(2016, 5, 4, 0, 0), '2017-05-04 00:00:00'), ('2016-06-03 00:00:00', datetime(2016, 6, 3, 0, 0), '2017-06-03 00:00:00'), 
                     ('2016-08-11 00:00:00', datetime(2016, 8, 11, 0, 0), '2017-08-11 00:00:00'), ('2017-03-07 00:00:00', datetime(2017, 3, 7, 0, 0), '2018-03-07 00:00:00'), 
                     ('2017-12-06 00:00:00', datetime(2017, 12, 6, 0, 0), '2018-12-06 00:00:00'), ('2018-02-02 00:00:00', datetime(2018, 2, 2, 0, 0), '2019-02-02 00:00:00'), 
                     ('2018-03-21 00:00:00', datetime(2018, 3, 21, 0, 0), '2019-03-21 00:00:00'), ('2018-04-16 00:00:00', datetime(2018, 4, 16, 0, 0), '2019-04-16 00:00:00'), 
                     ('2018-07-06 00:00:00', datetime(2018, 7, 6, 0, 0), '2019-07-06 00:00:00'), ('2018-07-06 00:00:00', datetime(2018, 7, 6, 0, 0), '2019-07-06 00:00:00'), 
                     ('2018-11-16 00:00:00', datetime(2018, 11, 16, 0, 0), '2019-11-16 00:00:00'), ('2019-02-22 00:00:00', datetime(2019, 2, 22, 0, 0), '2020-02-22 00:00:00'), 
                     ('2019-04-05 00:00:00', datetime(2019, 4, 5, 0, 0), '2020-04-05 00:00:00'), ('2019-04-11 00:00:00', datetime(2019, 4, 11, 0, 0), '2020-04-11 00:00:00'),
                     ('2019-04-22 00:00:00', datetime(2019, 4, 22, 0, 0), '2020-04-22 00:00:00'), ('2019-05-09 00:00:00', datetime(2019, 5, 9, 0, 0), '2020-05-09 00:00:00'), 
                     ('2019-07-11 00:00:00', datetime(2019, 7, 11, 0, 0), '2020-07-11 00:00:00'), ('2019-08-06 00:00:00', datetime(2019, 8, 6, 0, 0), '2020-08-06 00:00:00'), 
                     ('2019-09-20 00:00:00', datetime(2019, 9, 20, 0, 0), '2020-09-20 00:00:00'), ('2019-11-14 00:00:00', datetime(2019, 11, 14, 0, 0), '2020-11-14 00:00:00'), 
                     ('2020-03-31 00:00:00', datetime(2020, 3, 31, 0, 0), '2021-03-31 00:00:00'), ('2020-05-20 00:00:00', datetime(2020, 5, 20, 0, 0), '2021-05-20 00:00:00'), 
                     ('2020-06-10 00:00:00', datetime(2020, 6, 10, 0, 0), '2021-06-10 00:00:00'), ('2020-07-21 00:00:00', datetime(2020, 7, 21, 0, 0), '2021-07-21 00:00:00'), 
                     ('2020-08-26 00:00:00', datetime(2020, 8, 26, 0, 0), '2021-08-26 00:00:00'), ('2020-12-01 00:00:00', datetime(2020, 12, 1, 0, 0), '2021-12-01 00:00:00'), 
                     ('2020-12-11 00:00:00', datetime(2020, 12, 11, 0, 0), '2021-12-11 00:00:00'), ('2021-02-12 00:00:00', datetime(2021, 2, 12, 0, 0), '2022-02-12 00:00:00'), 
                     ('2021-02-26 00:00:00', datetime(2021, 2, 26, 0, 0), '2022-02-26 00:00:00'), ('2021-03-18 00:00:00', datetime(2021, 3, 18, 0, 0), '2022-03-18 00:00:00'), 
                     ('2021-06-02 00:00:00', datetime(2021, 6, 2, 0, 0), '2022-06-02 00:00:00'), ('2021-08-06 00:00:00', datetime(2021, 8, 6, 0, 0), '2022-08-06 00:00:00'), 
                     ('2021-09-14 00:00:00', datetime(2021, 9, 14, 0, 0), '2022-09-14 00:00:00'), ('2021-11-10 00:00:00', datetime(2021, 11, 10, 0, 0), '2022-11-10 00:00:00'),
                     ('2022-01-11 00:00:00', datetime(2022, 1, 11, 0, 0), '2023-01-11 00:00:00'), ('2022-04-14 00:00:00', datetime(2022, 4, 14, 0, 0), '2023-04-14 00:00:00'), 
                     ('2022-07-13 00:00:00', datetime(2022, 7, 13, 0, 0), '2023-07-13 00:00:00'), ('2022-08-10 00:00:00', datetime(2022, 8, 10, 0, 0), '2023-08-10 00:00:00'), 
                     ('2022-09-02 00:00:00', datetime(2022, 9, 2, 0, 0), '2023-09-02 00:00:00'), ('2022-09-14 00:00:00', datetime(2022, 9, 14, 0, 0), '2023-09-14 00:00:00'), 
                     ('2022-11-09 00:00:00', datetime(2022, 11, 9, 0, 0), '2023-11-09 00:00:00'), ('2022-12-02 00:00:00', datetime(2022, 12, 2, 0, 0), '2023-12-02 00:00:00'), 
                     ('2023-01-04 00:00:00', datetime(2023, 1, 4, 0, 0), '2024-01-04 00:00:00'), ('2023-01-09 00:00:00', datetime(2023, 1, 9, 0, 0), '2024-01-09 00:00:00'), 
                     ('2023-03-06 00:00:00', datetime(2023, 3, 6, 0, 0), '2024-03-06 00:00:00'), ('2023-03-10 00:00:00', datetime(2023, 3, 10, 0, 0), '2024-03-10 00:00:00'),
                     ('2023-03-13 00:00:00', datetime(2023, 3, 13, 0, 0), '2024-03-13 00:00:00'), ('2023-09-20 00:00:00', datetime(2023, 9, 20, 0, 0), '2024-09-20 00:00:00'),
                     ('2023-10-11 00:00:00', datetime(2023, 10, 11, 0, 0), '2024-10-11 00:00:00')]


    # creiamo un dizionario in cui per ogni data iniziale della lista datesToTrade1, inseriamo la lista delle date di trading che vanno da quella data iniziale fino alla data finale (cioè un anno dopo la data iniziale)
    # questo permette la ripetzione di questo passaggi per ogni agente che effettua simulazioni.
    totalDates = {}
    markets = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions'] # markets = ['nasdaq_actions']
    for market in markets:
        totalDates[market] = {}
        for date_ in datesToTrade1:
            # Ottengo tutte le date per l'iterazione:
            cur.execute(f"SELECT distinct time_value_it FROM {market} WHERE time_value_it > '{date_[0]}' and time_value_it < '{date_[2]}' order by time_value_it;")
            totalDates[market][date_[0]] = [date_[1]] + [d[0] for d in cur.fetchall()]
            
            #datesTrade = cur.fetchall()
        #end for
    
    #end for
    
    logger_main.info(f"Find dates to trade. \n")
    
    #agent2.agent2_markCapDayInitial.main(datesToTrade1, {}, {}, {}, {}, {}, {}, {}, totalDates)
    
    

    ############################################################################################
    #print(datesToTrade1)
    
    
    logger_main.info(f"Start program: {datetime.now()}")
    
    marksCap = ['topVal1999', 'topVal2000', 'topVal2001', 'topVal2002', 'topVal2003', 'topVal2004', 'topVal2005', 'topVal2006', 'topVal2007', 'topVal2008', 'topVal2009', 
                'topVal2010', 'topVal2011', 'topVal2012', 'topVal2013', 'topVal2014', 'topVal2015', 'topVal2016', 'topVal2017', 'topVal2018', 'topVal2019', 'topVal2020', 
                'topVal2021', 'topVal2022', 'topVal2023', 'topVal2024']
    
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU'] 
    
    dizMarkCap = {}
    for mark in markets:
        dizMarkCap[mark] = {}
        for top in marksCap:
            with open(f'{capitalization_path}/{mark}/top_value/{top}.csv', mode='r') as file:
                year = top[-4:]
                if mark not in dizMarkCap[mark]:
                    dizMarkCap[mark][year] = {}
                for row in csv.DictReader(file):
                    if row['date'] not in dizMarkCap[mark][year]:
                        dizMarkCap[mark][year][row['date']] = []
                    dizMarkCap[mark][year][row['date']].append(row['symb'])
                    
    logger_main.info(f"Find market capitalization. \n")
    
    ############################################################################################
    
    # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
    symbolsDispoInDatesNasd = {}
    symbolsDispoInDatesNyse = {}
    symbolsDispoInDatesLarge = {} 
    markets = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions'] # markets = ['nasdaq_actions']
    for mark in markets:
        for date in datesToTrade1:
            # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
            cur.execute(f"SELECT distinct(symbol) FROM {mark} WHERE time_value_it BETWEEN '{date[0]}' AND '{date[2]}';")
            if mark == 'nasdaq_actions':
                symbolsDispoInDatesNasd[date[1]] = [sy[0] for sy in cur.fetchall()]
            elif mark == 'nyse_actions':
                symbolsDispoInDatesNyse[date[1]] = [sy[0] for sy in cur.fetchall()]
            else:
                symbolsDispoInDatesLarge[date[1]] = [sy[0] for sy in cur.fetchall()]
                
    logger_main.info(f"Find symbols available. \n")
    
    ############################################################################################            
            
    # Recupero dei prezzi di apertura e chiusura per i simboli azionari disponibili nelle date di trading scelte in "priceDisp"
    pricesDispoInDatesNasd = {}
    pricesDispoInDatesNyse = {}
    pricesDispoInDatesLarge = {}
    markets = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']  #markets = ['nasdaq_actions']
    for mark in markets:
        for date in datesToTrade1:
                
                """if mark == 'nasdaq_actions':
                    last_date_year = (list(dizMarkCap['NASDAQ'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['NASDAQ'][date[2][0:4]][last_date_year])[0].split(';') 
                    symbolsF = symbolsF[0:500]
                    
                if mark == 'nyse_actions':
                    last_date_year = (list(dizMarkCap['NYSE'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['NYSE'][date[2][0:4]][last_date_year])[0].split(';')
                    symbolsF = symbolsF[0:500]
                
                if mark == 'larg_comp_eu_actions':
                    last_date_year = (list(dizMarkCap['LARG_COMP_EU'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['LARG_COMP_EU'][date[2][0:4]][last_date_year])[0].split(';')
                    symbolsF = symbolsF[0:500]
                """    
            
                # Recupero dei prezzi di apertura e chiusura per i simboli azionari disponibili nelle date di trading scelte in "priceDisp"
                cur.execute(f"SELECT symbol, time_value_it, open_price, high_price FROM {mark} WHERE time_value_it BETWEEN '{date[0]}' AND '{date[2]}'")
                #cur.execute( f"SELECT symbol, time_value_it, open_price, high_price FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")

                if mark == 'nasdaq_actions':
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesNasd[date[1]] = [prices_dict]
                elif mark == 'nyse_actions':
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesNyse[date[1]] = [prices_dict]
                else:
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesLarge[date[1]] = [prices_dict]    
    
    logger_main.info(f"Find prices available. \n")
    
    cur.close()
    conn.close()
    
    ############################################################################################
    
    logger_main.info(f"Start agents. \n")
    
    # Esecuzione degli agenti con le varie strategie
    
    logger_main.info(f"Start agent2 with select title for better cap in day initial.")
    agent2_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent2 with select title for better cap in day initial. \n")
    #agent2.agent2_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
        
    logger_main.info(f"Start agent2 with random select title.")
    agent2_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent2 with random select title. \n\n")
    
    ####################################
    
    logger_main.info(f"Start agent3 with select title for better cap in day initial.")
    agent3_markCapDayInitial.main(datesToTrade1,  dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent3 with select title for better cap in day initial. \n")
    #agent3.agent3_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
        
    logger_main.info(f"Start agent3 with random select title.")
    agent3_selectRandom.main(datesToTrade1,  dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent3 with random select title. \n\n")
    
    ####################################
    
    logger_main.info(f"Start agent7 with select title for better cap in day initial.")
    agent7_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent7 with select title for better cap in day initial. \n")
    #agent7_larger_time_window.agent7_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    logger_main.info(f"Start agent7 with random select title.")
    agent7_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent7 with random select title. \n\n")

    ####################################

    logger_main.info(f"Start agent8 with select title for better cap in day initial. ")
    agent8_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent8 with select title for better cap in day initial.\n")
    
    logger_main.info(f"Start agent8 with random select title.")
    agent8_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent8 with random select title. \n\n")
    
    ####################################
    
    # Creazione del dizionario per la simulazione dell'agente 6 con la suddivisione dei titoli in settori.
    """
    Il dizionario assumerà la forma seguente:
    {
        'nasdaq': {'Sector1': ['Symbol1', 'Symbol2', ...], 
                    'Sector2': ['Symbol3', 'Symbol4', ...], 
                    ...},
        'nyse': {'Sector1': ['Symbol5', 'Symbol6', ...], 
                'Sector2': ['Symbol7', 'Symbol8', ...], 
                    ...},
        'large': {'Sector1': ['Symbol9', 'Symbol10', ...], 
                    'Sector2': ['Symbol11', 'Symbol12', ...], 
                    ...}
    }
    """
    dizSymbSect = dict()
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    
    for mark in markets:
        if mark == 'NASDAQ':
            strMark = 'nasdaq_symbols_sorted'
        elif mark == 'NYSE':
            strMark = 'nyse_symbols_sorted'
        elif mark == 'LARG_COMP_EU':
            strMark = 'largest_companies_EU'
            
        dizSymbSect[mark] = {}
        with open (f"{symbols_info_path}/{mark}/{strMark}.csv", mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                row['Symbol'] = row['Symbol'].strip()
                if row['Sector'] != None:
                    sector = row['Sector'].strip()
                if sector not in dizSymbSect[mark]:
                    dizSymbSect[mark][sector] = [row['Symbol']]
                else:
                    dizSymbSect[mark][sector].append(row['Symbol'])

    logger_main.info(f"Start agent6 with select title for better cap in day initial.")
    agent6_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, 
                                                         symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, 
                                                         pricesDispoInDatesLarge, totalDates, dizSymbSect)
    logger_main.info(f"End agent6 with select title for better cap in day initial. \n\n")
    
    ####################################
    
    
    logger_main.info(f"Start agent5 with select title for better cap in day initial.")
    agent5_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, 
                                                              symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, 
                                                              pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent5 with select title for better cap in day initial. \n")
    
    #agent5_variationNumberTitle.agent5_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    logger_main.info(f"Start agent5 with random select title.")
    agent5_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, 
                                                         symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, 
                                                         pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent5 with random select title. \n\n")
     
    ####################################
    
    logger_main.info(f"Start agent4 with select title for better cap in day initial. ")
    agent4_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent4 with select title for better cap in day initial. \n")
    #agent4.agent4_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    logger_main.info(f"Start agent4 with random select title. ")
    agent4_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totalDates)
    logger_main.info(f"End agent4 with random select title. \n\n")


    logger_main.info("Fine simulazione !!!!!")
    print("Fine simulazione")
    return

if __name__ == '__main__':
    main()


 