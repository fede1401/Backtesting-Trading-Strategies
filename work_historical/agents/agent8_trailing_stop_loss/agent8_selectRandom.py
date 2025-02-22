# import MetaTrader5 as mt5
import sys

import psycopg2
import logging
from datetime import datetime, time, timedelta
import time as time_module
import math
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback
import numpy as np
import time
import random
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

# Ora possiamo importare `config`
get_path_specify([db_path, f'{main_project}/symbols', main_project, utils_path])

# Importa i moduli personalizzati
from database import insertDataDB, connectDB
from symbols import manage_symbol
import agentState
import utils

logger_agent8 = logging.getLogger('agent8')
logger_agent8.setLevel(logging.INFO)

# Evita di aggiungere più volte lo stesso handler
if not logger_agent8.handlers:
    # Crea un file handler che scrive in un file specifico
    file_handler = logging.FileHandler(f'{project_root}/logs/testAgent8.log')
    file_handler.setLevel(logging.INFO)

    # Definisci il formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Aggiungi il file handler al logger
    logger_agent8.addHandler(file_handler)

logger_agent8.propagate = False


"Simboli che presentano anomalie nei dati di mercato"
SYMB_NASD_ANOMALIE= [ 'IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL', 'IPA']

SYMB_NYSE_ANOMALIE = [ 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV' ]

SYMB_LARGE_ANOMALIE = [ 'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ' ]
    
SYMB_TOT_ANOMALIE = ['IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL', 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV',
                      'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ', 'IPA', 'CODA', 'PRO', 'XTP']

"""
Agente che sfrutta la strategia del TSL: trailing stop loss.
Questa strategia si basa sulla vendita di un titolo azionario quando il suo prezzo scende sotto una certa soglia.
L'obiettivo è ottenere un profitto, tenendo salva una percentuale di profitto che il titolo ha già guadagnato.

La strategia si basa su 2 parametri fondamentali:
- alpha: indica la soglia per cui attivare la strategia del TSL. Se il profitto del titolo azionario supera alpha, allora si attiva la strategia del TSL.
- beta: indica la percentuale per cui il prezzo del titolo azionario deve scendere rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.


Esempio:
Supponiamo di acquistare un titolo ad un prezzo di 100 USD.
Inizialmente aspettiamo che il titolo sali di una certa soglia alpha, ad esempio 15%.
Quindi, quando il prezzo raggiunge un prezzo di 115 USD si attiva la strategia.

Ci salviamo e teniamo da parte:
- il prezzo attuale per cui è partita la strategia: x(0)
e calcoliamo:
- la soglia y(0) = (1-beta) * x(0) : ad esempio se beta = 0,05 allora y(0) = 0,95 * 115 = 109,25 USD   

A questo punto ogni giorno di trading si calcola la soglia y:
y ( t + 1 ) = max( y(t), y(t) + ( x(t + 1) - x(t) ) ) ---> dove y(t) rappresenta il valore di y al giorno t e x(t) il valore di x al giorno t (prezzo al giorno t).
Nel calcolo, se il risultato cresce, signifca che il prezzo del titolo azionario sta salendo, quindi la soglia y cresce. Altrimente se il risultato è negativo, significa che il prezzo del titolo azionario sta scendendo, 
quindi la soglia y rimane invariata.

Se il prezzo corrente, cioè il prezzo al giorno t, scende sotto la soglia y, allora si vende il titolo azionario. 
In questo caso si salva una parte di profitti. Ad esempio, se il prezzo corrente è 108 USD e la soglia y è 109,25 USD, allora si vende il titolo azionario e si salva una parte di profitto.

Esempio:
- acquisto titolo a 100 USD
- alpha = 0,15
- beta = 0,05
- prezzo raggiunge 115 USD
- attivazione strategia TSL
- y = 109,25 USD
- x = 115 USD

- prezzo sale a 125 USD
- y = max(109,25, 109,25 + (125 - 115)) = max(109,25, 109,25 + 10) = 109,25 + 10 = 119,25
- x = 125 USD
- prezzo 125 USD > y = 119,25 USD, quindi non si vende il titolo azionario


- prezzo scende a 108 USD
- y = max(119,25, 119,25 + (108 - 125)) = max(119,25, 102,25) = 119,25
- x = 108 USD
- prezzo scende sotto y, quindi si vende il titolo azionario e si salva una parte di profitto


Infine, comprendiamo che:
- alpha deve essere abbastanza alto per garantire un profitto soddisfacente.

Se beta viene impostato ad un valore alto come 0,2, allora :
    - il prezzo del titolo azionario deve scendere del 20% rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.
    Quindi, y iniziale sarebbe stato = (1 - 0,2) * 115 = 92 USD e il prezzo del titolo azionario deve scendere sotto 92 USD per vendere il titolo azionario, 
    quindi non è molto conveniente perchè si rischia di perdere troppo.
    
Se beta viene impostato ad un valore basso come 0,025, allora:
    - il prezzo del titolo azionario deve scendere del 2,5% rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.
    Quindi, y iniziale sarebbe stato = (1 - 0,025) * 115 = 112,125 USD e il prezzo del titolo azionario deve scendere sotto 112,125 USD per vendere il titolo azionario,
    quindi è molto conveniente perchè si rischia di perdere poco.

"""


# Funzione principale per il trading e il caricamento
def main(datesToTrade, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totaledates):
    try:
        logger_agent8.info(f"[SIMULATION START] agent8_selectRandom initiated at {datetime.now()}\n")
        
        # Connessione al database
        cur, conn = connectDB.connect_data_backtesting()

        profitsPerc = []
        profTot = []
        middleSale = []
        middlePurchase = []
        MmiddleTimeSale = []
        middletitleBetterProfit = []
        middletitleWorseProfit = []

        alpha_parameters = [0.05, 0.1, 0.15, 0.2]
        beta_parameters = [0.025, 0.05, 0.1, 0.15, 0.2]

        # Inizio elaborazione per i diversi mercati
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']  #market = ['larg_comp_eu_actions']
        
        for m in market:
            logger_agent8.info(f"[MARKET INFO] Operating on market '{m}'\n")
            
            # Viene selezionato l'ultimo id del test inserito nel database
            idTest = utils.get_last_id_test(cur) 
            
            # viene registrata una riga vuota nel database per separare le simulazioni
            insertDataDB.insert_in_data_simulation(idTest, "------", mean_perc_profit=0, std_dev=0, variance=0, initial_budget= 0, mean_budget_with_profit_usd=0, 
                                                    avg_sale=0, avg_purchase=0, avg_time_sale=0,  best_symbol='----', worst_symbol='-----', timestamp_in = datetime.now(),timestamp_fin=datetime.now(), 
                                                    notes='---', cur=cur, conn=conn)
            
            # Recupero dei simboli azionari per il mercato scelto
            if m == 'nasdaq_actions':
                symbols = manage_symbol.get_symbols('NASDAQ', -1)
                symbolsDispoInDates = symbolsDispoInDatesNasd
                pricesDispoInDates = pricesDispoInDatesNasd
                m = 'data_market_nasdaq_symbols'
            elif m == 'nyse_actions':
                symbols = manage_symbol.get_symbols('NYSE', -1)
                symbolsDispoInDates = symbolsDispoInDatesNyse
                pricesDispoInDates = pricesDispoInDatesNyse
                m = 'data_market_nyse_symbols'
            elif m == 'larg_comp_eu_actions':
                symbols = manage_symbol.get_symbols('LARG_COMP_EU', -1)
                symbolsDispoInDates = symbolsDispoInDatesLarge
                pricesDispoInDates = pricesDispoInDatesLarge
                m = 'data_market_larg_comp_eu_symbols'
                
            for alpha in alpha_parameters:
                for beta in beta_parameters:
                    profitsPerc = []
                    profTot = []
                    middleSale = []
                    middlePurchase = []
                    MmiddleTimeSale = []
                    middletitleBetterProfit = []
                    middletitleWorseProfit = []

                    #idTest = utils.getLastIdTest(cur) 
                    idTest += 1
                    time_stamp_in = datetime.now()

                    total_steps = len(datesToTrade)  # 
                    for step in range(total_steps):
                        # Logica principale
                        utils.clear_tables_db(cur, conn)
                        trade_date, initial_date, endDate = datesToTrade[step]
                        logger_agent8.info(f"[TEST START] Starting test for agent8_selectRandom with ALPHA:{alpha} and BETA:{beta} on initial date {initial_date} at {datetime.now()}")
                        
                        profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit, initial_budget = tradingYear_purchase_one_after_the_other( cur, conn, symbols, trade_date, m, alpha, beta, initial_date, endDate, symbolsDispoInDates, pricesDispoInDates, totaledates[m])

                        # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean( # middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])
                        print( f"\nProfitto per il test {idTest}: agent8_symb_rnd con ALPHA:{alpha} and BETA:{beta}, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step - 1} iterazioni\n")

                        profitPerc = round(profitPerc, 4)
                        
                        if m == 'data_market_nasdaq_symbols':
                            market_to_insert = 'nasdaq'
                        elif m == 'data_market_nyse_symbols':
                            market_to_insert = 'nyse'
                        elif m == 'data_market_larg_comp_eu_symbols':
                            market_to_insert = 'european' 
                        
                        notes = f"Agent8 (TSL, Random), Market:{market_to_insert}, alpha:{alpha}, beta:{beta}. Uses TSL with 100 randomly selected symbols."
                        insertDataDB.insert_in_data_testing(idTest, "agent8_symb_rnd", step, initial_date=initial_date, end_date=endDate, initial_budget=initial_budget, profit_perc=profitPerc, budg_with_profit_USD=profitUSD, market=market_to_insert, n_purchase=nPurchase, n_sale=nSale, middle_time_sale_second=middleTimeSale,
                                                 middle_time_sale_day=(middleTimeSale / 86400), title_better_profit=titleBetterProfit, title_worse_profit=titleWorseProfit, notes=notes, cur=cur, conn=conn)

                        profTot.append(profitUSD)
                        profitsPerc.append(profitPerc)
                        middleSale.append(nSale)
                        middlePurchase.append(nPurchase)
                        MmiddleTimeSale.append(middleTimeSale)
                        middletitleBetterProfit.append(titleBetterProfit)
                        middletitleWorseProfit.append(titleWorseProfit)
                        logger_agent8.info(f"[TEST END] Completed test for agent8_selectRandom with ALPHA:{alpha} and BETA:{beta} on initial date {initial_date} at {datetime.now()}\n\n")

                    # Calcolo delle statistiche
                    mean_profit_perc = round(float(np.mean(profitsPerc)), 4)
                    std_deviation = round(float(np.std(profitsPerc)), 4)
                    varianza = round(float(np.var(profitsPerc)), 4)
                    mean_profit_usd = round(float(np.mean(profTot)), 4)
                    mean_sale = round(float(np.mean(middleSale)), 4)
                    mean_purchase = round(float(np.mean(middlePurchase)), 4)
                    mean_time_sale = round(float(np.mean(MmiddleTimeSale)), 4)

                    dizBetterTitle = {}
                    for title in middletitleBetterProfit:
                        if title != '':
                            if (title in dizBetterTitle):
                                dizBetterTitle[title] += 1
                            else:
                                dizBetterTitle[title] = 1

                    dizWorseTitle = {}
                    for title in middletitleWorseProfit:
                        if title != '':
                            if (title in dizWorseTitle):
                                dizWorseTitle[title] += 1
                            else:
                                dizWorseTitle[title] = 1

                    mean_titleBetterProfit = max(dizBetterTitle, key=dizBetterTitle.get)
                    mean_titleWorseProfit = max(dizWorseTitle, key=dizWorseTitle.get)

                    # logging.info(f"Profitto medio: {mean_profit}, Deviazione standard: {std_deviation}")
                    logger_agent8.info(f"[SIMULATION END] agent8_selectRandom simulation ended with ALPHA:{alpha} and BETA:{beta} at {datetime.now()}\n\n\n\n")
                    
                    if m == 'data_market_nasdaq_symbols':
                        market_to_insert = 'nasdaq'
                    elif m == 'data_market_nyse_symbols':
                        market_to_insert = 'nyse'
                    elif m == 'data_market_larg_comp_eu_symbols':
                        market_to_insert = 'european' 

                    notes = f"Agent8 (TSL, Random), Market:{market_to_insert}, alpha:{alpha}, beta:{beta}. Uses TSL with 100 randomly selected symbols."
                    insertDataDB.insert_in_data_simulation(idTest, "agent8_symb_rnd", mean_perc_profit=mean_profit_perc, std_dev=std_deviation, variance=varianza, initial_budget= initial_budget, 
                                                       mean_budget_with_profit_usd=mean_profit_usd, avg_sale=mean_sale, avg_purchase=mean_purchase, avg_time_sale=(mean_time_sale / 86400), best_symbol=mean_titleBetterProfit, 
                                                       worst_symbol=mean_titleWorseProfit, timestamp_in=time_stamp_in, timestamp_fin=datetime.now(), notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logger_agent8.critical(f"Errore non gestito: {e}")
        logger_agent8.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logger_agent8.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        #logging.shutdown()

################################################################################


def tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, market, alpha, beta, initial_date, endDate, symbolsDispoInDates, pricesDispoInDates, totaledates):
    # Inizializzazione a ogni iterazione
    budgetInvestimenti = initial_budget = 1000 # budget = 
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0 # equity = margin = 0 
    i = 0  # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
    sales = set()
    purchases = {}
    salesDict = {}

    # Inserimento dei dati iniziali dell'agente nel database ---> insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

    stateAgent = agentState.AgentState.SALE

    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    symbolDisp1 = manage_symbol.get_x_symbols_random(initial_date, symbolsDispoInDates, logger_agent8)
    logger_agent8.info(f"[SYMBOL SELECTION] Test 'agent8_selectRandom' in market '{market}' used symbols: {symbolDisp1}")

    # Ottimizzazione 4: Recupera TUTTI i prezzi dei simboli disponibili per il periodo in una sola query
    prices_dict = (pricesDispoInDates[initial_date])[0]

    # Recupero delle date di trading per l'anno corrente
    datesTrade = totaledates[initial_date.strftime('%Y-%m-%d %H:%M:%S')]

    i_for_date = 0

    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

        ######################## inizio SALE
        if stateAgent == agentState.AgentState.SALE or stateAgent == agentState.AgentState.SALE_IMMEDIATE:    # logging.info(f"Agent entrato nello stato Sale\n")

            # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
            for k,v in purchases.items():
            #for pur in purchases:
                ticketP = k
                datePur, volume, symbol, price_purch, tsl, y_i, x_i = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
                
                # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                if ticketP in sales:
                    continue

                price_data = prices_dict.get((symbol, trade_date))   # open | high price
                if price_data:
                    open_price_from_dict, price_current = price_data

                    if price_current == None:
                        continue
                    
                    if tsl:
                        # 2) Se TSL è attiva, aggiorno la soglia y_tsl e vedo se devo vendere.
                        # logging.info(f"Analizzo il simbolo {symbol} per la data {datePur} con prezzo corrente {price_current} e prezzo di acquisto {price_purch}")
                        y_tsl = max( y_i, (y_i + (price_current - x_i) ) )
                        
                        x_anchor = price_current
                        purchases[ticketP] = (datePur, volume, symbol, price_purch, tsl, y_tsl, x_anchor)
                        
                        if price_current <= y_tsl:
                            # Calcolo del profitto:
                            profit = price_current - price_purch
                            perc_profit = profit / price_purch
                            
                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + (price_purch * volume)

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            #profit_10Perc = (profit * 10) / 100
                            #profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + (((profit * 10) / 100) * volume)
                            budgetMantenimento = budgetMantenimento + (((profit * 90) / 100) * volume)

                            ticketSale += 1
                            nSaleProfit += 1

                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                            insertDataDB.insert_sale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_purch, profit, perc_profit, cur, conn)

                            # Calcolo del tempo medio di vendita: cioè il tempo che intercorre tra l'acquisto e la vendita di un titolo azionario
                            middleTimeSale.append((dateObject - datePur).total_seconds())

                            sales.add(ticketP)

                            # Salvataggio del profitto per il titolo azionario creato per ottenere a fine test i titoli azionari con il profitto medio migliore e peggiore 
                            if symbol in titleProfit:
                                titleProfit[symbol] += [perc_profit]
                            else:
                                titleProfit[symbol] = [perc_profit]

                            # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD / initial_budget) * 100

                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                            
                            salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)

                                                                       
                    else:
                        # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                        if price_current > price_purch:  # logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_purch}\n" )

                            # Calcolo del profitto:
                            profit = price_current - price_purch
                            perc_profit = profit / price_purch

                            # Se la percentuale di profitto supera il valore alpha, si attiva la TSL: trailing stop loss
                            if perc_profit > alpha:
                                
                                # Attivazione TSL
                                # calcolo soglia di attivazione TSL
                                x_initial = price_purch
                                y_initial = (1-beta) * price_current
                                
                                tsl = True
                                purchases[ticketP] = (datePur, volume, symbol, price_purch, tsl, y_initial, x_initial)
                                                            
            price_purch = -1
            price_current = -1

            if stateAgent == agentState.AgentState.SALE:
                stateAgent = agentState.AgentState.PURCHASE  # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

            if stateAgent == agentState.AgentState.SALE_IMMEDIATE:
                stateAgent = agentState.AgentState.WAIT  # logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")

        ######################## fine SALE



        ######################## inizio PURCHASE
        if stateAgent == agentState.AgentState.PURCHASE:  # logging.info(f"Agent entrato nello stato Purchase\n")
            giro = 0
            #random.shuffle(symbolDisp1)

            numb_purch = 0
            #i = 0
            # Acquisto di azioni in modo iterativo dal pool di titoli azionari finché c'è budget
            while budgetInvestimenti > 0:

                # Se sono stati visti tutti i titoli azionari e non c'è nulla da acquistare allora si esce dal ciclo
                if giro == len(symbolDisp1):
                    if numb_purch == 0:
                        break
                
                # Se sono stati visti tutti i titoli azionari e c'è qualcosa da acquistare allora si ricomincia a vedere i titoli azionario dal primo
                if i == len(symbolDisp1):   
                    i = 0

                # Scelta del simbolo azionario da acquistare tra quelli disponibili
                chosen_symbol = symbolDisp1[i]

                # incremento variabili per il ciclo
                i += 1
                giro += 1

                # Recupero del prezzo di apertura e  del simbolo azionario scelto
                price_data = prices_dict.get((chosen_symbol, trade_date))   # price_data = [open , high price]
                if price_data == None:
                    continue

                if price_data:
                    price, _ = price_data  # price = price_data[0] : corrisponde al prezzo di apertura del simbolo azionario scelto

                    if price == None:  # logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                        continue

                    if price == 0:  # Se il prezzo è = 0, allora non si può acquistare
                        continue

                        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database: ---> if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:

                    # Calcolo volume e aggiornamento budget
                    volumeAcq = float(10 / price)  # volumeAcq = float(math.floor(10 / price))
                    if volumeAcq == 0:
                        continue
                    ticketPur += 1
                    dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insert_purchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                    numb_purch += 1
                    budgetInvestimenti -= (price * volumeAcq)
                    
                    tsl = False
                    y_initial = 0
                    x_initial = 0
                    
                    purchases[ticketPur] = [dateObject, volumeAcq, chosen_symbol, price, tsl, y_initial, x_initial]

            # Dopo lo stato di acquisto il programma entra nello stato di attesa
            stateAgent = agentState.AgentState.SALE_IMMEDIATE  # logging.info(f"Cambio di stato da PURCHASE a SALE IMMEDIATE\n\n")
        ######################## fine PURCHASE



        ######################## inizio WAIT
        if stateAgent == agentState.AgentState.WAIT:  # logging.info(f"Agent entrato nello stato Wait\n")

            i_for_date += 1
            if i_for_date < len(datesTrade):
                trade_date = datesTrade[i_for_date]
                #trade_date = str(trade_date[0])
                trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

            if i_for_date >= len(datesTrade):
                
                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for k,v in purchases.items():
                #for pur in purchases:
                    ticketP = k
                    datePur, volume, symbol, price_purch, tsl, y_initial, x_initial = v[0], v[1], v[2], v[3], v[4], v[5], v[6]

                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if ticketP in sales:
                        continue

                    price_data = prices_dict.get((symbol, trade_date))
                    if price_data:
                        open_price_from_dict, price_current = price_data

                        if price_current == None:
                            continue

                        if price_current > price_purch:
                                # Calcolo del profitto:
                                profit = price_current - price_purch
                                perc_profit = profit / price_purch

                                # Vendiamo per l'ultima volta e teniamo nel deposito.
                                budgetMantenimento = budgetMantenimento + (price_purch * volume) + (profit * volume)

                                ticketSale += 1

                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insert_sale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_purch, profit, perc_profit, cur, conn)

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                                profitTotalUSD += profit * volume
                                profitTotalPerc = (profitTotalUSD / initial_budget) * 100

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)

                        else:
                                # Non c'è profitto, vendiamo al prezzo corrente.
                                budgetMantenimento = budgetMantenimento + (price_current * volume)

                                ticketSale += 1

                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insert_sale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_purch, 0, 0, cur, conn)

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)
                break

            stateAgent = agentState.AgentState.SALE

        ######################## fine WAIT

    purForLog = ''     
    for k, v in titleProfit.items():
        #titleProfit[k] = round
        purForLog += f'{k}: {len(v)}, '
    logger_agent8.info(f"[PURCHASE INFO] Number of purchases: {len(purchases)}; Purchase details: {purForLog}")
    
    # return profitTotalPerc
    maxT, minT = '', ''
    maxP, minP = 0, 1000000000
    for k, v in titleProfit.items():
        for value in v:
            if value > 40:
                logger_agent8.info(f"[PROFIT INFO] Highest profit recorded for symbol {k}: {value}%")
        titleProfit[k] = float(np.mean(v))
        if titleProfit[k] > maxP:
            maxP = titleProfit[k]
            maxT = k
        if titleProfit[k] < minP:
            minP = titleProfit[k]
            minT = k
        
    profitNotReinvestedPerc = ((profitNotReinvested - initial_budget) / initial_budget ) * 100

    logger_agent8.info(f"[OVERALL PROFIT] Overall profit percentage: {profitNotReinvestedPerc}%")
    
    if profitNotReinvestedPerc > 250:
        for tick, infoS in salesDict.items():
            logger_agent8.info(
                f"[TRANSACTION] {tick}: Purchase Date: {infoS[1]}, Sale Date: {infoS[0]}, TicketAcq: {infoS[2]}, "
                f"Volume: {round(float(infoS[3]), 4)}, Symbol: {infoS[4]}, Current Sale Price: {round(float(infoS[5]))}, "
                f"Purchase Price: {round(float(infoS[6]))}, Profit: {round(float(infoS[7]))}, Fractional percentage: {infoS[8]}, Profit percentage: {round(float(infoS[8] * 100), 4)}"
            )
            
    if middleTimeSale == []:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, 0, maxT, minT, initial_budget

    else:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(np.mean(middleTimeSale)), maxT, minT, initial_budget


if __name__ == "__main__":
    print()
