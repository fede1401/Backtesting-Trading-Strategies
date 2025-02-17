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

# Importa i moduli personalizzati
from database import insertDataDB, connectDB
from symbols import manage_symbol
import agentState
import utils

logger_agent3 = logging.getLogger('agent3')
logger_agent3.setLevel(logging.INFO)

# Evita di aggiungere più volte lo stesso handler
if not logger_agent3.handlers:
    # Crea un file handler che scrive in un file specifico
    file_handler = logging.FileHandler(f'{project_root}/logs/testAgent3.log')
    file_handler.setLevel(logging.INFO)

    # Definisci il formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Aggiungi il file handler al logger
    logger_agent3.addHandler(file_handler)

logger_agent3.propagate = False


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
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ', 'IPA']



# Funzione principale per il trading e il caricamento
def main(datesToTrade, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge,  totaledates):
    try:
        logger_agent3.info(f"Start agent3_selectRandom: {datetime.now()} \n")

        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        profitsPerc = []
        profTot = []
        middleSale = []
        middlePurchase = []
        MmiddleTimeSale = []
        middletitleBetterProfit = []
        middletitleWorseProfit = []

        list_take_profit = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

        # Inizio elaborazione per i diversi mercati
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']
        
        for m in market:
            logger_agent3.info(f"\n\nWork with market {m} : {datetime.now()}")
            
            # Viene selezionato l'ultimo id del test inserito nel database
            idTest = utils.getLastIdTest(cur)
            
            # viene registrata una riga vuota nel database per separare le simulazioni
            insertDataDB.insertInMiddleProfit(idTest, "------", roi=0, devstandard=0, var=0, middleProfitUSD=0, middleSale=0, middlePurchase=0, middleTimeSale=0,  middletitleBetterProfit='----', middletitleWorseProfit=0, notes='---', cur=cur, conn=conn)
            
            # Recupero dei simboli azionari per il mercato scelto
            if m == 'nasdaq_actions':
                symbols = manage_symbol.get_symbols('NASDAQ', -1)
                symbolsDispoInDates = symbolsDispoInDatesNasd
                pricesDispoInDates = pricesDispoInDatesNasd
            elif m == 'nyse_actions':
                symbols = manage_symbol.get_symbols('NYSE', -1)
                symbolsDispoInDates = symbolsDispoInDatesNyse
                pricesDispoInDates = pricesDispoInDatesNyse
            elif m == 'larg_comp_eu_actions':
                symbols = manage_symbol.get_symbols('LARG_COMP_EU', -1)
                symbolsDispoInDates = symbolsDispoInDatesLarge
                pricesDispoInDates = pricesDispoInDatesLarge

            for i in range(len(list_take_profit)):  # Per ogni valore di Take Profit (1%-10%)
                profitsPerc = []
                profTot = []
                middleSale = []
                middlePurchase = []
                MmiddleTimeSale = []
                middletitleBetterProfit = []
                middletitleWorseProfit = []

                TK = list_take_profit[i]
                #logging.info(f"Start simulation with {TK} agent3_selectRandom : {datetime.now()}")

                #idTest = utils.getLastIdTest(cur) 
                idTest += 1

                total_steps = len(datesToTrade)  # 
                for step in range(total_steps):
                    # Logica principale
                    utils.clearSomeTablesDB(cur, conn)
                    trade_date, initial_date, endDate = datesToTrade[step]
                    logger_agent3.info(f"Start test with {TK} agent3_selectRandom in initial date {initial_date} : {datetime.now()}")

                    profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit = tradingYear_purchase_one_after_the_other( cur, conn, symbols, trade_date, m, TK, initial_date, endDate,  dizMarkCap, symbolsDispoInDates, pricesDispoInDates, totaledates[m])

                    # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean( # middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])

                    print( f"\nProfitto per il test {idTest}: agent3_symb_rnd con TP={TK}%, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step - 1} iterazioni\n")

                    profitPerc = round(profitPerc, 4)
                    insertDataDB.insertInTesting(idTest, "agent3_symb_rnd", step, initial_date=initial_date, end_date=endDate, profitPerc=profitPerc, profitUSD=profitUSD, market=m, nPurchase=nPurchase, nSale=nSale, middleTimeSaleSecond=middleTimeSale,
                                                 middleTimeSaleDay=(middleTimeSale / 86400), titleBetterProfit=titleBetterProfit, titleWorseProfit=titleWorseProfit, notes=f"TAKE PROFIT = {TK}% ", cur=cur, conn=conn)

                    profTot.append(profitUSD)
                    profitsPerc.append(profitPerc)
                    middleSale.append(nSale)
                    middlePurchase.append(nPurchase)
                    MmiddleTimeSale.append(middleTimeSale)
                    middletitleBetterProfit.append(titleBetterProfit)
                    middletitleWorseProfit.append(titleWorseProfit)
                    logger_agent3.info(f"End test with {TK} agent3_selectRandom in initial date {initial_date} : {datetime.now()}\n\n")

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
                logger_agent3.info(f"End simulation with {TK} agent3_selectRandom : {datetime.now()} \n\n\n\n")


                notes = f"TP:{TK}%, {m}, agent3 with random choises of 100 symbols, buy one after the other if the price current is lower than mean price of purchase of the last 50 days."
                insertDataDB.insertInMiddleProfit(idTest, "agent3_symb_rnd", roi=mean_profit_perc, devstandard=std_deviation, var=varianza, middleProfitUSD=mean_profit_usd, middleSale=mean_sale, middlePurchase=mean_purchase,
                                                  middleTimeSale=(mean_time_sale / 86400), middletitleBetterProfit=mean_titleBetterProfit, middletitleWorseProfit=mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logger_agent3.critical(f"Errore non gestito: {e}")
        logger_agent3.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logger_agent3.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        #logging.shutdown()

################################################################################


def tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, market, TP, initial_date, endDate, dizMarkCap, symbolsDispoInDates, pricesDispoInDates, totaledates):
    # Inizializzazione a ogni iterazione
    budgetInvestimenti = initial_budget = 1000 # budget = 
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0 # equity = margin = 0 
    i = 0  # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
    sales = set()
    purchases = set()    
    salesDict = {}


    # Inserimento dei dati iniziali dell'agente nel database ---> insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

    stateAgent = agentState.AgentState.SALE

    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    symbolDisp1 =  manage_symbol.get_x_symbols_random(initial_date, symbolsDispoInDates, logger_agent3)
    logger_agent3.info(f"Test agent3_symb_rnd in {market} with this symbols : {symbolDisp1}")
    
    # Ottimizzazione 4: Recupera TUTTI i prezzi dei simboli disponibili per il periodo in una sola query
    prices_dict = (pricesDispoInDates[initial_date])[0]

    # Ottengo tutte le date per l'iterazione:
    datesTrade = totaledates[initial_date.strftime('%Y-%m-%d %H:%M:%S')]

    i_for_date = 0
    
    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE or stateAgent == agentState.AgentState.SALE_IMMEDIATE: #logging.info(f"Agent entrato nello stato Sale\n")
                
                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for pur in purchases:
                    datePur, ticketP, volume, symbol, price_open = pur[0], pur[1], pur[2], pur[3], pur[4]
                    
                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if ticketP in sales:
                        continue                # ordine già venduto

                    price_data = prices_dict.get((symbol, trade_date))
                    if price_data:
                        open_price_from_dict, price_current = price_data

                        if price_current == None:
                            continue

                        # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                        if price_current > price_open:   #logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                            # Calcolo del profitto:
                            profit = price_current - price_open
                            perc_profit = profit / price_open

                            if perc_profit > TP:

                                # aggiorno il budget
                                budgetInvestimenti = budgetInvestimenti + ( price_open * volume )

                                # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                                profit_10Perc = (profit * 10) / 100
                                profit_90Perc = (profit * 90) / 100
                                budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                                budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                                ticketSale += 1
                                nSaleProfit += 1

                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                #datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)

                                middleTimeSale.append((dateObject - datePur).total_seconds())

                                sales.add(ticketP)

                                if symbol in titleProfit:
                                    titleProfit[symbol] += [perc_profit]
                                else:
                                    titleProfit[symbol] = [perc_profit]

                                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                                profitTotalUSD += profit * volume
                                profitTotalPerc = (profitTotalUSD/initial_budget)*100


                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested/initial_budget)*100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_open, profit, perc_profit)

                                # Aggiornamento dello stato dell'agent nel database
                                #insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                #logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current},
                                # prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                
                if stateAgent == agentState.AgentState.SALE:
                    stateAgent = agentState.AgentState.PURCHASE  # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

                if stateAgent == agentState.AgentState.SALE_IMMEDIATE:
                    stateAgent = agentState.AgentState.WAIT  # logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")

            ######################## fine SALE

            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:   #logging.info(f"Agent entrato nello stato Purchase\n")
                                
                j = 0      # indice utilizzato per passare alla giornata successiva se non si riesce a comprare nulla.
                numb_purch = 0
                #i = 0
                
                # Acquisto di azioni in modo iterativo dal pool di titoli azionari finché c'è budget
                while budgetInvestimenti > 0:
                       
                    # Se sono stati visti tutti i titoli azionari e c'è ancora budget per acquistare si ricomincia da capo
                    if j == len(symbolDisp1):
                        if numb_purch == 0:
                            break
                    
                    if i == len(symbolDisp1):
                        i = 0
                    
                    chosen_symbol = symbolDisp1[i]  #chosen_symbol = symbolDisp[random.randint(0, len(symbolDisp) - 1)]
                    
                    i += 1

                    price_data = prices_dict.get((chosen_symbol, trade_date))
                    if price_data == None:
                        j += 1
                        continue
                    
                    if price_data:
                        price, _ = price_data

                        if price == None:  #logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                            j += 1
                            continue

                        #price = price[0]
                        if price == 0:  # Se il prezzo è = 0, allora non si può acquistare
                            j += 1
                            continue

                        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database:
                        #if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:

                        middlePrice = utils.getValueMiddlePrice(chosen_symbol, market, trade_date, cur)

                        if price < middlePrice:

                            # Calcolo volume e aggiornamento budget
                            volumeAcq = float(10 / price)
                            if volumeAcq == 0:
                                continue
                            ticketPur += 1
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento nel database
                            insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                            budgetInvestimenti -= (price * volumeAcq)
                            
                            purchases.add((dateObject, ticketPur, volumeAcq, chosen_symbol, price))

                            # Aggiornamento stato
                            #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                # Logging dell'acquisto
                                #if logging.getLogger().isEnabledFor(logging.INFO):
                                    #logging.info(f"Acquistata azione {chosen_symbol} in data: {trade_date}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                        else:
                            j += 1

                            continue

                        #else:
                        #    if logging.getLogger().isEnabledFor(logging.INFO):
                        #        logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")


                # Dopo lo stato di acquisto il programma entra nello stato di attesa
                stateAgent = agentState.AgentState.SALE_IMMEDIATE

            ######################## fine PURCHASE

            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:  #logging.info(f"Agent entrato nello stato Wait\n")
                
                # Aggiornamento dello stato dell'agent nel database
                #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                i_for_date += 1
                if i_for_date < len(datesTrade):
                    trade_date = datesTrade[i_for_date]
                    #trade_date = str(trade_date[0])
                    trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

                #if trade_date >= endDate:
                if i_for_date >= len(datesTrade):
                    
                    # Si vendono tutte le azioni rimanenti.
  
                    # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                    for pur in purchases:
                        datePur, ticketP, volume, symbol, price_open = pur[0], pur[1], pur[2], pur[3], pur[4]
                        
                        # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                        if ticketP in sales:
                            continue
                        
                        price_data = prices_dict.get((symbol, trade_date))
                        if price_data:
                            open_price_from_dict, price_current = price_data

                            if price_current == None:
                                continue
                        
                        #if result:
                            # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
                        #    price_current = result[0]
                            
                            if price_current > price_open:   
                                # Calcolo del profitto:
                                profit = price_current - price_open
                                perc_profit = profit / price_open
                            
                                # Vendiamo per l'ultima volta e teniamo nel deposito.
                                budgetMantenimento = budgetMantenimento + (price_open * volume) + (profit * volume)
                                
                                ticketSale += 1
                            
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale( dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn )

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                                profitTotalUSD += profit * volume
                                profitTotalPerc = (profitTotalUSD / initial_budget) * 100
                                    
                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_open, profit, perc_profit)
                            
                            else:
                                # Non c'è profitto, vendiamo al prezzo corrente.
                                budgetMantenimento = budgetMantenimento + (price_current * volume)

                                ticketSale += 1
                                
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, 0, 0, cur, conn )

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_open, profit, perc_profit)
                    break

                stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT
            
    purForLog = ''     
    for k, v in titleProfit.items():
        #titleProfit[k] = round
        purForLog += f'{k}: {len(v)}, '
    logger_agent3.info(f"Numero acquisti: {len(purchases)}, acquisti: {purForLog}")
    
    #return profitTotalPerc
    maxT, minT = '', ''
    maxP, minP = 0, 1000000000
    for k, v in titleProfit.items():
        for value in v:
            if value > 40:
                logger_agent3.info(f"Profit high for {k}: {value}%")
        titleProfit[k] = float(np.mean(v))
        if titleProfit[k] > maxP:
            maxP = titleProfit[k]
            maxT = k
        if titleProfit[k] < minP:
            minP = titleProfit[k]
            minT = k
            
    profitNotReinvestedPerc = ((profitNotReinvested - initial_budget) / initial_budget ) * 100
    logger_agent3.info(f"Profitto in percentuale : {profitNotReinvestedPerc} %")
    
    if profitNotReinvestedPerc > 250:
        for tick, infoS in salesDict.items():
            logger_agent3.info(f"{tick}: date purchase: {infoS[1]}, data sale: {infoS[0]}, ticketAcq: {infoS[2]}, volume: {infoS[3]}, simbolo: {infoS[4]}, prezzo corrente di vendita: {infoS[5]}, prezzo acquisto: {infoS[6]}, profitto: {infoS[7]}, profitto percentuale: {infoS[8]}")
            
    if middleTimeSale == []:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, 0, maxT, minT

    else:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(
            np.mean(middleTimeSale)), maxT, minT




if __name__ == "__main__":
    print()