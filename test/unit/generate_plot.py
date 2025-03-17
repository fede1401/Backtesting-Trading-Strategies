import sys
from datetime import datetime
import csv
import logging
import os
from pathlib import Path
import traceback
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

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

# Ora possiamo importare `config`
get_path_specify([db_path, f'{main_project}/symbols', main_project, utils_path])

from work_historical.database import connectDB




############################################################################################################
# PROFITTO PERCENTUALE MEDIO E DEVIAZIONE STANDARD.

def plot_mean_profit_every_agent(cur):
    """
    Recupera i i profitti percentuali per ogni agente, ne calcola la media e crea un barplot:
        - con asse X = agente, 
        - asse Y = media del profitto percentuale.
    
    Args:
        cur: oggetto cursor per eseguire query
    
    Returns:
        None
    """
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    data_list = []
    
    for ag in agents:
        query = f"SELECT profit_perc FROM testing_data WHERE agent='{ag}';"
        cur.execute(query)
        
        profits = [row[0] for row in cur.fetchall()]
        mean_profit = np.mean(profits) if len(profits) > 0 else 0
        
        data_list.append({"agent": ag, "mean_profit": mean_profit})
    # end for
    
    df = pd.DataFrame(data_list)
    
    # Ordiniamo i valori per colore più chiaro/scuro
    norm = plt.Normalize(df["mean_profit"].min(), df["mean_profit"].max())
    colors = plt.cm.Blues(norm(df["mean_profit"]))  # Più alto il valore, più scuro il colore
    
    # Migliorare la visibilità del colore più chiaro rendendolo più scuro
    colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
    
    fig = plt.figure(figsize=(12, 6))
    #sns.barplot(x="agent", y="mean_profit", data=df, palette=colors)
    sns.barplot(x="agent", y="mean_profit", hue="agent", data=df, palette=colors, legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Agente")
    plt.ylabel("Profitto Percentuale Medio")
    plt.title("Profitto Medio per Agente (Barplot)")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
    
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_agent.png", dpi=fig.dpi)

    plt.show()
    
    
    return 0



def plot_dev_std_every_agent(cur):
    """
    Recupera i i profitti percentuali per ogni agente, ne calcola la media e crea un barplot:
        - con asse X = agente, 
        - asse Y = media del profitto percentuale.
    
    Args:
        cur: oggetto cursor per eseguire query
    
    Returns:
        None
    """

    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    data_list = []
    
    for ag in agents:
        query = f"SELECT profit_perc FROM testing_data WHERE agent='{ag}';"
        cur.execute(query)
        results = cur.fetchall()
        
        profits = [row[0] for row in results]
        dev_std = np.std(profits) if len(profits) > 0 else 0
        data_list.append({"agent": ag, "dev_std": dev_std})

    
    df = pd.DataFrame(data_list)
    
    # Ordiniamo i valori per colore più chiaro/scuro
    norm = plt.Normalize(df["dev_std"].min(), df["dev_std"].max())
    colors = plt.cm.Reds(norm(df["dev_std"]))  # Più alto il valore, più scuro il colore
    
    # Migliorare la visibilità del colore più chiaro rendendolo più scuro
    colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
    
    fig = plt.figure(figsize=(12, 6))
    #sns.barplot(x="agent", y="dev_std", data=df, palette=colors)
    sns.barplot(x="agent", y="dev_std", hue="agent", data=df, palette=colors, legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Agente")
    plt.ylabel("Deviazione standard")
    plt.title("Deviazione standard per Agente (Barplot)")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
    
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/dev_std_every_agent.png", dpi=fig.dpi)

    plt.show()
    
    
    return 0
    



def plot_mean_profit_every_agent_market(cur):
    """
    Recupera i i profitti percentuali per ogni agente, ne calcola la media e crea un barplot:
        - con asse X = agente, 
        - asse Y = media del profitto percentuale.
    
    Args:
        cur: oggetto cursor per eseguire query
    
    Returns:
        None
    """
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
        
    for mark in ['nasdaq', 'nyse', 'european']:
        
        data_list = []
        
        for ag in agents:
            query = f"SELECT profit_perc FROM testing_data WHERE agent='{ag}' and market='{mark}';"
            cur.execute(query)
            
            profits = [row[0] for row in cur.fetchall()]
            mean_profit = np.mean(profits) if len(profits) > 0 else 0
            
            data_list.append({"agent": ag, "mean_profit": mean_profit})
        # end for
    
        df = pd.DataFrame(data_list)
        
        # Ordiniamo i valori per colore più chiaro/scuro
        norm = plt.Normalize(df["mean_profit"].min(), df["mean_profit"].max())
        colors = plt.cm.Blues(norm(df["mean_profit"]))  # Più alto il valore, più scuro il colore
        
        # Migliorare la visibilità del colore più chiaro rendendolo più scuro
        colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
        
        fig = plt.figure(figsize=(12, 6))
        #sns.barplot(x="agent", y="mean_profit", data=df, palette=colors)
        sns.barplot(x="agent", y="mean_profit", hue="agent", data=df, palette=colors, legend=False)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Agente")
        plt.ylabel(f"Profitto Percentuale Medio per {mark}")
        plt.title(f"Profitto Medio per Agente (Barplot) {mark}")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
        
        plt.tight_layout()
        
        plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_agent_{mark}.png", dpi=fig.dpi)

        plt.show() # Mostra il plot
    
    
    return 0




############################################################################################################

# PROFITTO MEDIO TAKE PROFIT

def plot_mean_profit_every_take_profit(cur):
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",  "agent7_symb_rnd", "agent7_top_avg_vol"
    ]

    
    TAKE_PROFIT = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for ag in agents:
        data_list = []
        for tp in TAKE_PROFIT:
        
            query = f"SELECT profit_perc FROM testing_data WHERE agent='{ag}' AND notes LIKE 'TP:{tp}\%%';"
            cur.execute(query)
            
            profits = [row[0] for row in cur.fetchall()]
            mean_profit = np.mean(profits) if len(profits) > 0 else 0
            
            data_list.append({"take_profit": tp, "mean_profit": mean_profit})
        # end for
        
        df = pd.DataFrame(data_list)
            
        # Ordiniamo i valori per colore più chiaro/scuro
        norm = plt.Normalize(df["mean_profit"].min(), df["mean_profit"].max())
        colors = plt.cm.Blues(norm(df["mean_profit"]))  # Più alto il valore, più scuro il colore
            
        # Migliorare la visibilità del colore più chiaro rendendolo più scuro
        colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
            
        fig = plt.figure(figsize=(12, 6))
        df["take_profit"] = df["take_profit"].astype(str)
            #sns.barplot(x="agent", y="mean_profit", data=df, palette=colors)
        sns.barplot(x="take_profit", y="mean_profit", hue="take_profit", data=df, palette=colors, width=0.8, dodge=False)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Valore Take Profit")
        plt.ylabel("Profitto Percentuale Medio")
        plt.title(f"Profitto Medio per {ag} con valori di TAKE PROFIT. (Barplot)")
        plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
            
        plt.tight_layout()
            
        plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_agent_take_profit_{ag}.png", dpi=fig.dpi)

        plt.show()
    
    
    return 0











############################################################################################################
# DISTRIBUZIONI

# DISTRIBUZIONE DEI PROFITTI PERCENTUALI OTTENUTI NEI TEST
def plot_distribution_mean_profit(cur):
    """
    Funzione utilizzata per recuperare le percentuali dei profitti dei test e generare la distribuzione dei risultati.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
    
    # Query to get data results
    query = "SELECT profit_perc FROM testing_data;"
    
    # Execute query
    cur.execute(query)
    
    # Estrai i valori in un array numpy
    profits_percs = np.array([row[0] for row in cur.fetchall()])
    
    print(max(profits_percs))
    print(min(profits_percs))
    
    # Calcola e mostra media e deviazione standard
    mean_val = np.mean(profits_percs)
    std_val = np.std(profits_percs)
    
    
    # Genera l'istogramma dei risultati
    fig = plt.figure(figsize=(10,6))
    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_val:.2f}%')
    plt.axvline(mean_val + std_val, color='green', linestyle='--', linewidth=2, label=f'StdDev: {std_val:.2f}%')
    plt.legend()
    
    plt.hist(profits_percs, bins=30, density=True, color='skyblue', alpha=0.7)
    plt.xlabel("Profitto Percentuale")
    plt.ylabel("Densità di Probabilità")
    plt.title("Distribuzione dei Profitti Percentuali dai Test")
    
    plt.grid(True)
    
    plt.savefig(f"{project_root}/data/result/plot/distribution_mean_profit.png", dpi=fig.dpi)

    plt.show()
    
    return



# DISTRIBUZIONE DEI PROFITTI PERCENTUALI OTTENUTI NEI TEST PER OGNI AGENTE
def plots_distribution_mean_profit_every_agent(cur):
    """
    Funzione utilizzata per recuperare le percentuali dei profitti dei test e generare la distribuzione dei profitti percentuali: frequenza dei test sui profitti percentuali medi.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
       
    # Dizionario agent -> query
    queries = {
        "agent2_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent2_symb_rnd';",
        "agent2_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent2_top_avg_vol';",
        "agent3_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent3_symb_rnd';",
        "agent3_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent3_top_avg_vol';",
        "agent4_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent4_symb_rnd';",
        "agent4_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent4_top_avg_vol';",
        "agent5_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent5_symb_rnd';",
        "agent5_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent5_top_avg_vol';",
        "agent6_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent6_top_avg_vol';",
        "agent7_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent7_symb_rnd';",
        "agent7_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent7_top_avg_vol';",
        "agent8_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent8_symb_rnd';",
        "agent8_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent8_top_avg_vol';"
    }
    
    
    # Definiamo una palette di colori per distinguerli
    colors = [
        "skyblue", "orange", "green", "red", "purple", 
        "brown", "pink", "gray", "olive", "cyan", 
        "magenta", "gold", "teal"
    ]
    
    
    for i, (agent_name, query) in enumerate(queries.items()):
        # Esegui query
        cur.execute(query)
        
        # Estrai i valori in un array numpy
        profits_percs = np.array([row[0] for row in cur.fetchall()])
        
        # Calcola e mostra media e deviazione standard
        mean_val = np.mean(profits_percs)
        std_val = np.std(profits_percs)
        
        # Genera l'istogramma dei risultati
        fig = plt.figure(figsize=(10,6))
        plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_val:.2f}%')
        plt.axvline(mean_val + std_val, color='green', linestyle='--', linewidth=2, label=f'StdDev: {std_val:.2f}%')
        plt.legend()
        
        # Disegna l'istogramma con densità, colore e trasparenza (alpha)
        plt.hist(
            profits_percs, bins=30, density=True, 
            alpha=0.4, color=colors[i], 
            label=agent_name
        )
        
        # Impostazioni del grafico
        plt.xlabel("Profitto Percentuale")
        plt.ylabel("Densità di Probabilità")
        plt.title(f"Distribuzione dei Profitti Percentuali dai Test per {agent_name}")
        plt.grid(True)
        plt.legend()  # Mostra la legenda con i nomi degli agent
        
        plt.savefig(f"{project_root}/data/result/plot/distribution_mean_profit_{agent_name}.png")
        
        plt.show()
        
    return




def one_plot_distribution_mean_profit_every_agent(cur):
    """
    Recupera i profit_perc per vari agent e genera istogrammi sovrapposti in un'unica figura,
    in modo da confrontare la distribuzione dei profitti percentuali.
    """
       
    # Dizionario agent -> query
    queries = {
        "agent2_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent2_symb_rnd';",
        "agent2_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent2_top_avg_vol';",
        "agent3_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent3_symb_rnd';",
        "agent3_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent3_top_avg_vol';",
        "agent4_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent4_symb_rnd';",
        "agent4_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent4_top_avg_vol';",
        "agent5_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent5_symb_rnd';",
        "agent5_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent5_top_avg_vol';",
        "agent6_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent6_top_avg_vol';",
        "agent7_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent7_symb_rnd';",
        "agent7_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent7_top_avg_vol';",
        "agent8_symb_rnd":        "SELECT profit_perc FROM testing_data WHERE agent='agent8_symb_rnd';",
        "agent8_top_avg_vol":     "SELECT profit_perc FROM testing_data WHERE agent='agent8_top_avg_vol';"
    }
    
    
    # Definiamo una palette di colori per distinguerli
    colors = [
        "skyblue", "orange", "green", "red", "purple", 
        "brown", "pink", "gray", "olive", "cyan", 
        "magenta", "gold", "teal"
    ]
    
    for i, (agent_name, query) in enumerate(queries.items()):
        # Esegui query
        cur.execute(query)
        result = cur.fetchall()
        
        # Estrai i valori in un array numpy
        profits_percs = np.array([row[0] for row in result])
        
        # Disegna l'istogramma con densità, colore e trasparenza (alpha)
        plt.hist(
            profits_percs, bins=30, density=True, 
            alpha=0.4, color=colors[i], 
            label=agent_name
        )
    
    # Impostazioni del grafico
    plt.xlabel("Profitto Percentuale")
    plt.ylabel("Densità di Probabilità")
    plt.title("Confronto Distribuzioni di Profitti Percentuali per Agenti")
    plt.grid(True)
    plt.legend()  # Mostra la legenda con i nomi degli agent
    
    plt.savefig(f"{project_root}/data/result/plot/one_distribution_mean_profit_every_agent.png")
    
    plt.show()
    
    return




#FIXME: DA IMPLEMENTARE
def plot_distribution_detention_time(cur):
    query = """
        SELECT avg_sale_time_days, AVG(profit_perc) as avg_profit
        FROM testing_data
        GROUP BY avg_sale_time_days
        ORDER BY avg_sale_time_days;
    """
    cur.execute(query)
    results = cur.fetchall()
    
    # Estrai i tempi medi e i valori medi
    dates = [row[0] for row in results]
    avg_profits = [row[1] for row in results]
    
    plt.hexbin(dates, avg_profits, gridsize=50, cmap='Blues')
    plt.colorbar(label='Contatore punti')
    plt.show()
    
    """
    plt.figure(figsize=(10,6))
    plt.hist2d(dates, avg_profits, bins=[50,50], cmap='Blues')  # bins=[n_bins_x, n_bins_y]
    plt.colorbar(label='Contatore punti')         # Barra con legenda dei conteggi
    plt.xlabel('Tempi in giorni (tra acquisto e vendita)')
    plt.ylabel('Profitto Percentuale')
    plt.title('Distribuzione 2D (hist2d) di Tempi vs Profitto')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()
    """
        
    return




# DISTRIBUZIONE DEI TEMPI DI DETENZIONE OTTENUTI NEI TEST
def plot_distribution_detention_time(cur):
    """
    Funzione utilizzata per recuperare i tempi di detenzione dei test e generare la distribuzione dei risultati.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
    
    # Query to get data results
    query = "SELECT avg_sale_time_days FROM testing_data;"
    
    # Execute query
    cur.execute(query)
    
    # Estrai i valori in un array numpy
    detention_times = np.array([row[0] for row in cur.fetchall()])
    
    print(max(detention_times))
    print(min(detention_times))
    
    # Calcola e mostra media e deviazione standard
    mean_val = np.mean(detention_times)
    std_val = np.std(detention_times)
    
    
    # Genera l'istogramma dei risultati
    fig = plt.figure(figsize=(10,6))
    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_val:.2f}')
    plt.axvline(mean_val + std_val, color='green', linestyle='--', linewidth=2, label=f'StdDev: {std_val:.2f}')
    plt.legend()
    
    plt.hist(detention_times, bins=30, density=True, color='skyblue', alpha=0.7)
    plt.xlabel("Tempo di detenzione misurato in giorni.")
    plt.ylabel("Densità di Probabilità")
    plt.title("Distribuzione dei Tempi di detenzione (misurati in giorni) dai Test")
    
    plt.grid(True)
    
    plt.savefig(f"{project_root}/data/result/plot/distribution_detention_time.png", dpi=fig.dpi)

    plt.show()
    
    return



# DISTRIBUZIONE DEI PROFITTI PERCENTUALI OTTENUTI NEI TEST PER OGNI AGENTE
def plots_distribution_detention_time_every_agent(cur):
    """
    Funzione utilizzata per recuperare i tempi di detenzione dei test e generare la distribuzione dei tempi di detenzione: frequenza dei test sui tempi di detenzione.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
       
    # Dizionario agent -> query
    queries = {
        "agent2_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent2_symb_rnd';",
        "agent2_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent2_top_avg_vol';",
        "agent3_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent3_symb_rnd';",
        "agent3_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent3_top_avg_vol';",
        "agent4_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent4_symb_rnd';",
        "agent4_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent4_top_avg_vol';",
        "agent5_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent5_symb_rnd';",
        "agent5_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent5_top_avg_vol';",
        "agent6_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent6_top_avg_vol';",
        "agent7_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent7_symb_rnd';",
        "agent7_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent7_top_avg_vol';",
        "agent8_symb_rnd":        "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent8_symb_rnd';",
        "agent8_top_avg_vol":     "SELECT avg_sale_time_days FROM testing_data WHERE agent='agent8_top_avg_vol';"
    }
    
    
    # Definiamo una palette di colori per distinguerli
    colors = [
        "skyblue", "orange", "green", "red", "purple", 
        "brown", "pink", "gray", "olive", "cyan", 
        "magenta", "gold", "teal"
    ]
    
    
    for i, (agent_name, query) in enumerate(queries.items()):
        # Esegui query
        cur.execute(query)
        
        # Estrai i valori in un array numpy
        detention_times = np.array([row[0] for row in cur.fetchall()])
        
        # Calcola e mostra media e deviazione standard
        mean_val = np.mean(detention_times)
        std_val = np.std(detention_times)
        
        # Genera l'istogramma dei risultati
        fig = plt.figure(figsize=(10,6))
        plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_val:.2f}')
        plt.axvline(mean_val + std_val, color='green', linestyle='--', linewidth=2, label=f'StdDev: {std_val:.2f}')
        plt.legend()
        
        # Disegna l'istogramma con densità, colore e trasparenza (alpha)
        plt.hist(
            detention_times, bins=30, density=True, 
            alpha=0.4, color=colors[i], 
            label=agent_name
        )
        
        # Impostazioni del grafico
        plt.xlabel("Tempo di detenzione misurato in giorni.")
        plt.ylabel("Densità di Probabilità")
        plt.title(f"Distribuzione dei Tempi di detenzione (misurati in giorni) dai Test per {agent_name}")
        plt.grid(True)
        plt.legend()  # Mostra la legenda con i nomi degli agent
        
        plt.savefig(f"{project_root}/data/result/plot/distribution_detention_time_{agent_name}.png")
        
        plt.show()
        
    return











############################################################################################################
# PROFITTO PERCENTUALE OGNI TEST PER OGNI AGENTE

def plot_profit_by_agent_boxplot(cur):
    """
    Recupera i profit_perc per ogni agente e crea un boxplot 
    con asse X = agente, asse Y = profitto percentuale.
    """

    # Elenco agenti
    agents = [
        "agent2_symb_rnd", "agent2_top_avg_vol",
        "agent3_symb_rnd", "agent3_top_avg_vol",
        "agent4_symb_rnd", "agent4_top_avg_vol",
        "agent5_symb_rnd", "agent5_top_avg_vol",
        "agent6_top_avg_vol",
        "agent7_symb_rnd", "agent7_top_avg_vol",
        "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    # Costruiamo una lista di dizionari, che poi convertiremo in DataFrame
    data_list = []
    
    for ag in agents:
        query = f"SELECT profit_perc FROM testing_data WHERE agent='{ag}';"
        cur.execute(query)
        
        # results è una lista di tuple, estraiamo il profitto in un array
        profits = [row[0] for row in cur.fetchall()]
        
        # Creiamo un dizionario per ogni record
        for p in profits:
            data_list.append({"agent": ag, "profit_perc": p})
    
    # Convertiamo in DataFrame
    df = pd.DataFrame(data_list)
    
    # Boxplot: asse X = agent, asse Y = profit_perc
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="agent", y="profit_perc", data=df)
    
    # Miglioriamo l'etichetta dell'asse X (se i nomi agent sono lunghi)
    plt.xticks(rotation=45, ha='right')
    
    plt.xlabel("Agente")
    plt.ylabel("Profitto Percentuale")
    plt.title("Distribuzione dei Profitti Percentuali per Agente (Boxplot)")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7 )
    
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/profit_every_test_by_agent_boxplot.png")
    plt.show()
    return






############################################################################################################


# PROFITTO PERCENTUALE MEDIO DATE DI INIZIO TEST

def plot_mean_profit_every_date_initial_test(cur):
    """
    Recupera i valori di profitti percentuali medi e li plotta in un grafico dove sull'asse x sono le date di inizio dei test e sull'asse y i valori medi dei profitti percentuali.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """

    # Esegui una query per raggruppare per initial_date e calcolare la media dei profit_perc
    query = """
        SELECT initial_date, AVG(profit_perc) as avg_profit
        FROM testing_data
        GROUP BY initial_date
        ORDER BY initial_date;
    """
    cur.execute(query)
    results = cur.fetchall()
    
    # Estrai le date e i valori medi
    # Assumiamo che initial_date sia in formato datetime o stringa formattata
    dates = [row[0] for row in results]
    avg_profits = [row[1] for row in results]
    
    # Se le date sono stringhe, convertili in oggetti datetime
    if isinstance(dates[0], str):
        dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates]
    
    # Crea il grafico
    plt.figure(figsize=(12,6))
    plt.plot(dates, avg_profits, marker="o", linestyle="-", color='blue')
    plt.xlabel("Data di inizio della simulazione")
    plt.ylabel("Profitto Percentuale Medio")
    plt.title("Media dei Profitti Percentuali per Data di Inizio")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_date_initial_test.png")
    plt.show()
    return 0


    
def plot_mean_profit_every_date_initial_test_every_agent(cur):
    """
    Recupera i valori di profitti percentuali medi e li plotta in un grafico dove sull'asse x sono le date di inizio dei test e sull'asse y i valori medi dei profitti percentuali.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
    
    # Elenco agenti
    agents = [
        "agent2_symb_rnd", "agent2_top_avg_vol",
        "agent3_symb_rnd", "agent3_top_avg_vol",
        "agent4_symb_rnd", "agent4_top_avg_vol",
        "agent5_symb_rnd", "agent5_top_avg_vol",
        "agent6_top_avg_vol",
        "agent7_symb_rnd", "agent7_top_avg_vol",
        "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    for ag in agents:

        # Esegui una query per raggruppare per initial_date e calcolare la media dei profit_perc
        query = f"""
            SELECT initial_date, AVG(profit_perc) as avg_profit
            FROM testing_data
            WHERE agent='{ag}'
            GROUP BY initial_date
            ORDER BY initial_date;
        """
        cur.execute(query)
        results = cur.fetchall()
        
        # Estrai le date e i valori medi
        # Assumiamo che initial_date sia in formato datetime o stringa formattata
        dates = [row[0] for row in results]
        avg_profits = [row[1] for row in results]
        
        # Se le date sono stringhe, convertili in oggetti datetime
        if isinstance(dates[0], str):
            dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates]
        
        # Crea il grafico
        plt.figure(figsize=(14,6))
        plt.plot(dates, avg_profits, marker="o", linestyle="-", color='blue')
        plt.xlabel("Data di inizio della simulazione")
        plt.ylabel("Profitto Percentuale Medio")
        plt.title(f"Media dei Profitti Percentuali per Data di Inizio per {ag}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_date_initial_test_{ag}.png")
        plt.show()
    return 0




def plot_mean_profit_every_date_initial_test_every_market(cur):
    """
    Recupera i valori di profitti percentuali medi e li plotta in un grafico dove sull'asse x sono le date di inizio dei test e sull'asse y i valori medi dei profitti percentuali.
    
    Args:
        cur: oggetto cursor per eseguire query
        
    Returns:
        None
    """
    
    # Elenco mercati:
    markets = ['nasdaq', 'nyse', 'european']
    
    for mark in markets:

        # Esegui una query per raggruppare per initial_date e calcolare la media dei profit_perc
        query = f"""
            SELECT initial_date, AVG(profit_perc) as avg_profit
            FROM testing_data
            WHERE market='{mark}'
            GROUP BY initial_date
            ORDER BY initial_date;
        """
        cur.execute(query)
        results = cur.fetchall()
        
        # Estrai le date e i valori medi
        # Assumiamo che initial_date sia in formato datetime o stringa formattata
        dates = [row[0] for row in results]
        avg_profits = [row[1] for row in results]
        
        # Se le date sono stringhe, convertili in oggetti datetime
        if isinstance(dates[0], str):
            dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates]
        
        # Crea il grafico
        plt.figure(figsize=(14,6))
        plt.plot(dates, avg_profits, marker="o", linestyle="-", color='blue')
        plt.xlabel("Data di inizio della simulazione")
        plt.ylabel("Profitto Percentuale Medio")
        plt.title(f"Media dei Profitti Percentuali per Data di Inizio per {mark}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(f"{project_root}/data/result/plot/mean_profit_every_date_initial_test_{mark}.png")
        plt.show()
    return 0







############################################################################################################

# STATISTICHE NUMERO ACQUISTE E VENDITE


def plot_mean_N_purchases_every_agent(cur):
    """
    Recupera il numero di acquisti per ogni agente, ne calcola la media e crea un barplot:
        - con asse X = agente, 
        - asse Y = media del numero di acquisti.
    
    Args:
        cur: oggetto cursor per eseguire query
    
    Returns:
        None
    """
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    data_list = []
    
    for ag in agents:
        query = f"SELECT n_purchase FROM testing_data WHERE agent='{ag}';"
        cur.execute(query)
        
        numb_purchases = [row[0] for row in cur.fetchall()]
        mean_purchases = np.mean(numb_purchases) if len(numb_purchases) > 0 else 0
        
        data_list.append({"agent": ag, "mean_#_purchase": mean_purchases})
    # end for
    
    df = pd.DataFrame(data_list)
    
    # Ordiniamo i valori per colore più chiaro/scuro
    norm = plt.Normalize(df["mean_#_purchase"].min(), df["mean_#_purchase"].max())
    colors = plt.cm.YlGn(norm(df["mean_#_purchase"]))  # Più alto il valore, più scuro il colore
    
    # Migliorare la visibilità del colore più chiaro rendendolo più scuro
    colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
    
    fig = plt.figure(figsize=(12, 6))
    #sns.barplot(x="agent", y="mean_profit", data=df, palette=colors)
    sns.barplot(x="agent", y="mean_#_purchase", hue="agent", data=df, palette=colors, legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Agente")
    plt.ylabel("Media numero acquisti")
    plt.title("Media numero acquisti per Agente (Barplot)")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
    
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/mean_#_purchase_every_agent.png", dpi=fig.dpi)

    plt.show()
    
    
    return 0





def plot_mean_N_sales_every_agent(cur):
    """
    Recupera il numero di vendite per ogni agente, ne calcola la media e crea un barplot:
        - con asse X = agente, 
        - asse Y = media del numero di acquisti.
    
    Args:
        cur: oggetto cursor per eseguire query
    
    Returns:
        None
    """
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    data_list = []
    
    for ag in agents:
        query = f"SELECT n_sale FROM testing_data WHERE agent='{ag}';"
        cur.execute(query)
        
        numb_sales = [row[0] for row in cur.fetchall()]
        mean_sales = np.mean(numb_sales) if len(numb_sales) > 0 else 0
        
        data_list.append({"agent": ag, "mean_#_sale": mean_sales})
    # end for
    
    df = pd.DataFrame(data_list)
    
    # Ordiniamo i valori per colore più chiaro/scuro
    norm = plt.Normalize(df["mean_#_sale"].min(), df["mean_#_sale"].max())
    colors = plt.cm.Oranges(norm(df["mean_#_sale"]))  # Più alto il valore, più scuro il colore
    
    # Migliorare la visibilità del colore più chiaro rendendolo più scuro
    colors = [(c[0] * 0.85, c[1] * 0.85, c[2] * 0.85, 1) for c in colors]
    
    fig = plt.figure(figsize=(12, 6))
    #sns.barplot(x="agent", y="mean_profit", data=df, palette=colors)
    sns.barplot(x="agent", y="mean_#_sale", hue="agent", data=df, palette=colors, legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Agente")
    plt.ylabel("Media numero vendite")
    plt.title("Media numero vendite per Agente (Barplot)")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7) # alpha indica l'opacità delle linee
    
    plt.tight_layout()
    
    plt.savefig(f"{project_root}/data/result/plot/mean_#_sales_every_agent.png", dpi=fig.dpi)

    plt.show()
    
    
    return 0



############################################################################################################




############################################################################################################




# TABELLA RELATIVA ALLA CORRELAZIONE TRA PROFITTO PERCENTUALE MEDIO E RANGE TEMPO DI DETENZIONE.

def table_correlation_profit_perc_detention_time(cur):
    agents = [ "agent2_symb_rnd", "agent2_top_avg_vol",       "agent3_symb_rnd", "agent3_top_avg_vol",
               "agent4_symb_rnd", "agent4_top_avg_vol",       "agent5_symb_rnd", "agent5_top_avg_vol",
               "agent6_top_avg_vol",
               "agent7_symb_rnd", "agent7_top_avg_vol",      "agent8_symb_rnd", "agent8_top_avg_vol"
    ]
    
    data_list = []
    
    cur.execute("SELECT MAX(avg_sale_time_days) FROM testing_data;")
    max_days = cur.fetchone()[0]
    
    
    range_detention_time = [(0,0), (1, 5), (5,10),(10, 20), (20,30), (30, 50), (50, 80), (80, 120), (120, 170), (170, 230), (230, 300), (300, int(max_days))]
    
    for ag in agents:
        for r in range_detention_time:
            
            if r == (0,0):
                 query = f"""SELECT profit_perc
                        FROM testing_data 
                        WHERE agent='{ag}' AND avg_sale_time_days = {r[0]};
                    """
            else:
                query = f"""SELECT profit_perc
                            FROM testing_data 
                            WHERE agent='{ag}' AND avg_sale_time_days >= {r[0]} AND avg_sale_time_days < {r[1]};
                        """
                    
            cur.execute(query)
            profits = [row[0] for row in cur.fetchall()]
            mean_profit = np.mean(profits) if len(profits) > 0 else 0
            
            print(f"Agent: {ag}, Range: {r}, Mean Profit: {round(mean_profit, 4)}")
            
    return 0
    



"""
Agent: agent2_symb_rnd, Range: (0, 0), Mean Profit: -9.403875
Agent: agent2_symb_rnd, Range: (1, 5), Mean Profit: 252.2637
Agent: agent2_symb_rnd, Range: (5, 10), Mean Profit: 72.8898812080537
Agent: agent2_symb_rnd, Range: (10, 20), Mean Profit: 44.68957463556851
Agent: agent2_symb_rnd, Range: (20, 30), Mean Profit: 33.59465844504022
Agent: agent2_symb_rnd, Range: (30, 50), Mean Profit: 25.97345245683931
Agent: agent2_symb_rnd, Range: (50, 80), Mean Profit: 16.63881546961326
Agent: agent2_symb_rnd, Range: (80, 120), Mean Profit: 15.203452427184466
Agent: agent2_symb_rnd, Range: (120, 170), Mean Profit: 18.09486930835735
Agent: agent2_symb_rnd, Range: (170, 230), Mean Profit: 15.197336477115117
Agent: agent2_symb_rnd, Range: (230, 300), Mean Profit: 9.89630081300813
Agent: agent2_symb_rnd, Range: (300, 365), Mean Profit: 1.2643083333333334


Agent: agent2_top_avg_vol, Range: (0, 0), Mean Profit: -5.4332192307692315
Agent: agent2_top_avg_vol, Range: (1, 5), Mean Profit: 112.66813571428573
Agent: agent2_top_avg_vol, Range: (5, 10), Mean Profit: 55.425618932038844
Agent: agent2_top_avg_vol, Range: (10, 20), Mean Profit: 37.807400297619054
Agent: agent2_top_avg_vol, Range: (20, 30), Mean Profit: 28.835264227642277
Agent: agent2_top_avg_vol, Range: (30, 50), Mean Profit: 23.51070604395604
Agent: agent2_top_avg_vol, Range: (50, 80), Mean Profit: 16.332176168929113
Agent: agent2_top_avg_vol, Range: (80, 120), Mean Profit: 14.702131235955056
Agent: agent2_top_avg_vol, Range: (120, 170), Mean Profit: 18.03639288135593
Agent: agent2_top_avg_vol, Range: (170, 230), Mean Profit: 16.103548701298703
Agent: agent2_top_avg_vol, Range: (230, 300), Mean Profit: 14.054210584958218
Agent: agent2_top_avg_vol, Range: (300, 365), Mean Profit: 5.056059259259259


Agent: agent3_symb_rnd, Range: (0, 0), Mean Profit: -11.51887088607595
Agent: agent3_symb_rnd, Range: (1, 5), Mean Profit: 217.11336666666668
Agent: agent3_symb_rnd, Range: (5, 10), Mean Profit: 99.43365893719808
Agent: agent3_symb_rnd, Range: (10, 20), Mean Profit: 59.132643116883116
Agent: agent3_symb_rnd, Range: (20, 30), Mean Profit: 41.68436564885496
Agent: agent3_symb_rnd, Range: (30, 50), Mean Profit: 28.521766233766236
Agent: agent3_symb_rnd, Range: (50, 80), Mean Profit: 18.87752544117647
Agent: agent3_symb_rnd, Range: (80, 120), Mean Profit: 18.039004472271913
Agent: agent3_symb_rnd, Range: (120, 170), Mean Profit: 20.454313864306783
Agent: agent3_symb_rnd, Range: (170, 230), Mean Profit: 17.695816572504704
Agent: agent3_symb_rnd, Range: (230, 300), Mean Profit: 9.736361607142856
Agent: agent3_symb_rnd, Range: (300, 365), Mean Profit: 0.8490261904761903


Agent: agent3_top_avg_vol, Range: (0, 0), Mean Profit: -5.52432896551724
Agent: agent3_top_avg_vol, Range: (1, 5), Mean Profit: 117.65399655172415
Agent: agent3_top_avg_vol, Range: (5, 10), Mean Profit: 58.27773552631579
Agent: agent3_top_avg_vol, Range: (10, 20), Mean Profit: 38.77028125
Agent: agent3_top_avg_vol, Range: (20, 30), Mean Profit: 28.597419417475727
Agent: agent3_top_avg_vol, Range: (30, 50), Mean Profit: 23.094119204389575
Agent: agent3_top_avg_vol, Range: (50, 80), Mean Profit: 16.04826427480916
Agent: agent3_top_avg_vol, Range: (80, 120), Mean Profit: 17.830974150943394
Agent: agent3_top_avg_vol, Range: (120, 170), Mean Profit: 17.239655636363636
Agent: agent3_top_avg_vol, Range: (170, 230), Mean Profit: 17.515013111888113
Agent: agent3_top_avg_vol, Range: (230, 300), Mean Profit: 17.371524814814816
Agent: agent3_top_avg_vol, Range: (300, 365), Mean Profit: 7.38347840909091


Agent: agent4_symb_rnd, Range: (0, 0), Mean Profit: -9.846256951871657
Agent: agent4_symb_rnd, Range: (1, 5), Mean Profit: 199.06117560975608
Agent: agent4_symb_rnd, Range: (5, 10), Mean Profit: 68.26792920065253
Agent: agent4_symb_rnd, Range: (10, 20), Mean Profit: 42.90813274295036
Agent: agent4_symb_rnd, Range: (20, 30), Mean Profit: 33.162606141007814
Agent: agent4_symb_rnd, Range: (30, 50), Mean Profit: 24.15441597193562
Agent: agent4_symb_rnd, Range: (50, 80), Mean Profit: 16.66142922767408
Agent: agent4_symb_rnd, Range: (80, 120), Mean Profit: 15.67935037065342
Agent: agent4_symb_rnd, Range: (120, 170), Mean Profit: 17.303368220646533
Agent: agent4_symb_rnd, Range: (170, 230), Mean Profit: 15.655010001150218
Agent: agent4_symb_rnd, Range: (230, 300), Mean Profit: 8.945970039118066
Agent: agent4_symb_rnd, Range: (300, 365), Mean Profit: 0.5922391371340524


Agent: agent4_top_avg_vol, Range: (0, 0), Mean Profit: -5.433219230769231
Agent: agent4_top_avg_vol, Range: (1, 5), Mean Profit: 110.0130463878327
Agent: agent4_top_avg_vol, Range: (5, 10), Mean Profit: 55.24775782650143
Agent: agent4_top_avg_vol, Range: (10, 20), Mean Profit: 38.534150884744136
Agent: agent4_top_avg_vol, Range: (20, 30), Mean Profit: 29.38665667808219
Agent: agent4_top_avg_vol, Range: (30, 50), Mean Profit: 23.74515150979851
Agent: agent4_top_avg_vol, Range: (50, 80), Mean Profit: 16.378884867681013
Agent: agent4_top_avg_vol, Range: (80, 120), Mean Profit: 16.52744842778313
Agent: agent4_top_avg_vol, Range: (120, 170), Mean Profit: 18.576843065201267
Agent: agent4_top_avg_vol, Range: (170, 230), Mean Profit: 16.152258646927894
Agent: agent4_top_avg_vol, Range: (230, 300), Mean Profit: 13.513313716012085
Agent: agent4_top_avg_vol, Range: (300, 365), Mean Profit: 5.175996549192364


Agent: agent5_symb_rnd, Range: (0, 0), Mean Profit: -8.171831932773111
Agent: agent5_symb_rnd, Range: (1, 5), Mean Profit: 201.73225217391305
Agent: agent5_symb_rnd, Range: (5, 10), Mean Profit: 73.43006867469879
Agent: agent5_symb_rnd, Range: (10, 20), Mean Profit: 44.70159429920116
Agent: agent5_symb_rnd, Range: (20, 30), Mean Profit: 33.54496957831325
Agent: agent5_symb_rnd, Range: (30, 50), Mean Profit: 24.656743085281526
Agent: agent5_symb_rnd, Range: (50, 80), Mean Profit: 16.57090633310007
Agent: agent5_symb_rnd, Range: (80, 120), Mean Profit: 14.92089034730539
Agent: agent5_symb_rnd, Range: (120, 170), Mean Profit: 16.5372104069975
Agent: agent5_symb_rnd, Range: (170, 230), Mean Profit: 15.038669111034244
Agent: agent5_symb_rnd, Range: (230, 300), Mean Profit: 8.794492200107586
Agent: agent5_symb_rnd, Range: (300, 365), Mean Profit: -0.0643951111111113


Agent: agent5_top_avg_vol, Range: (0, 0), Mean Profit: -5.244595192307693
Agent: agent5_top_avg_vol, Range: (1, 5), Mean Profit: 107.30018965517239
Agent: agent5_top_avg_vol, Range: (5, 10), Mean Profit: 54.649330714707624
Agent: agent5_top_avg_vol, Range: (10, 20), Mean Profit: 37.04221320545924
Agent: agent5_top_avg_vol, Range: (20, 30), Mean Profit: 28.34559250339213
Agent: agent5_top_avg_vol, Range: (30, 50), Mean Profit: 23.405328851492015
Agent: agent5_top_avg_vol, Range: (50, 80), Mean Profit: 15.46712297372834
Agent: agent5_top_avg_vol, Range: (80, 120), Mean Profit: 15.226221606008087
Agent: agent5_top_avg_vol, Range: (120, 170), Mean Profit: 17.35750194092827
Agent: agent5_top_avg_vol, Range: (170, 230), Mean Profit: 15.175299333007972
Agent: agent5_top_avg_vol, Range: (230, 300), Mean Profit: 13.048003377686795
Agent: agent5_top_avg_vol, Range: (300, 365), Mean Profit: 4.274653317535546


Agent: agent6_top_avg_vol, Range: (0, 0), Mean Profit: -6.278932203389831
Agent: agent6_top_avg_vol, Range: (1, 5), Mean Profit: 148.55464893617022
Agent: agent6_top_avg_vol, Range: (5, 10), Mean Profit: 54.81014866995074
Agent: agent6_top_avg_vol, Range: (10, 20), Mean Profit: 37.92396282282283
Agent: agent6_top_avg_vol, Range: (20, 30), Mean Profit: 29.166755655095184
Agent: agent6_top_avg_vol, Range: (30, 50), Mean Profit: 22.51334587942478
Agent: agent6_top_avg_vol, Range: (50, 80), Mean Profit: 15.20717384843982
Agent: agent6_top_avg_vol, Range: (80, 120), Mean Profit: 14.353844221808014
Agent: agent6_top_avg_vol, Range: (120, 170), Mean Profit: 14.539539310806289
Agent: agent6_top_avg_vol, Range: (170, 230), Mean Profit: 14.420355418994415
Agent: agent6_top_avg_vol, Range: (230, 300), Mean Profit: 11.290024817518248
Agent: agent6_top_avg_vol, Range: (300, 365), Mean Profit: 5.756026153846154


Agent: agent7_symb_rnd, Range: (0, 0), Mean Profit: -9.490979999999999
Agent: agent7_symb_rnd, Range: (1, 5), Mean Profit: 242.98575
Agent: agent7_symb_rnd, Range: (5, 10), Mean Profit: 69.782038
Agent: agent7_symb_rnd, Range: (10, 20), Mean Profit: 46.88244528875379
Agent: agent7_symb_rnd, Range: (20, 30), Mean Profit: 32.461735233160624
Agent: agent7_symb_rnd, Range: (30, 50), Mean Profit: 25.09121755319149
Agent: agent7_symb_rnd, Range: (50, 80), Mean Profit: 16.482744225352114
Agent: agent7_symb_rnd, Range: (80, 120), Mean Profit: 16.614327480916028
Agent: agent7_symb_rnd, Range: (120, 170), Mean Profit: 15.648349494949494
Agent: agent7_symb_rnd, Range: (170, 230), Mean Profit: 16.728707438016528
Agent: agent7_symb_rnd, Range: (230, 300), Mean Profit: 7.475312970711297
Agent: agent7_symb_rnd, Range: (300, 365), Mean Profit: -2.46276875


Agent: agent7_top_avg_vol, Range: (0, 0), Mean Profit: -5.433219230769231
Agent: agent7_top_avg_vol, Range: (1, 5), Mean Profit: 112.66813571428574
Agent: agent7_top_avg_vol, Range: (5, 10), Mean Profit: 55.42561893203884
Agent: agent7_top_avg_vol, Range: (10, 20), Mean Profit: 37.80740029761905
Agent: agent7_top_avg_vol, Range: (20, 30), Mean Profit: 28.83526422764228
Agent: agent7_top_avg_vol, Range: (30, 50), Mean Profit: 23.510706043956045
Agent: agent7_top_avg_vol, Range: (50, 80), Mean Profit: 16.33217616892911
Agent: agent7_top_avg_vol, Range: (80, 120), Mean Profit: 14.702131235955056
Agent: agent7_top_avg_vol, Range: (120, 170), Mean Profit: 18.03639288135593
Agent: agent7_top_avg_vol, Range: (170, 230), Mean Profit: 16.103548701298703
Agent: agent7_top_avg_vol, Range: (230, 300), Mean Profit: 14.054210584958218
Agent: agent7_top_avg_vol, Range: (300, 365), Mean Profit: 5.056059259259259


Agent: agent8_symb_rnd, Range: (0, 0), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (1, 5), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (5, 10), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (10, 20), Mean Profit: 133.99093333333334
Agent: agent8_symb_rnd, Range: (20, 30), Mean Profit: 50.115636792452825
Agent: agent8_symb_rnd, Range: (30, 50), Mean Profit: 29.901931710914457
Agent: agent8_symb_rnd, Range: (50, 80), Mean Profit: 19.785065225225225
Agent: agent8_symb_rnd, Range: (80, 120), Mean Profit: 14.16421377517869
Agent: agent8_symb_rnd, Range: (120, 170), Mean Profit: 6.757209176029962
Agent: agent8_symb_rnd, Range: (170, 230), Mean Profit: 0.2909114285714284
Agent: agent8_symb_rnd, Range: (230, 300), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (300, 365), Mean Profit: 0


Agent: agent8_top_avg_vol, Range: (0, 0), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (1, 5), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (5, 10), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (10, 20), Mean Profit: 52.56281111111111
Agent: agent8_top_avg_vol, Range: (20, 30), Mean Profit: 34.8884423076923
Agent: agent8_top_avg_vol, Range: (30, 50), Mean Profit: 24.90940301291248
Agent: agent8_top_avg_vol, Range: (50, 80), Mean Profit: 21.46488833107191
Agent: agent8_top_avg_vol, Range: (80, 120), Mean Profit: 14.749951567711808
Agent: agent8_top_avg_vol, Range: (120, 170), Mean Profit: 6.868904705882353
Agent: agent8_top_avg_vol, Range: (170, 230), Mean Profit: 4.74495352112676
Agent: agent8_top_avg_vol, Range: (230, 300), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (300, 365), Mean Profit: 0









Agent: agent2_symb_rnd, Range: (0, 0), Mean Profit: -9.4039
Agent: agent2_symb_rnd, Range: (1, 5), Mean Profit: 252.2637
Agent: agent2_symb_rnd, Range: (5, 10), Mean Profit: 72.8899
Agent: agent2_symb_rnd, Range: (10, 20), Mean Profit: 44.6896
Agent: agent2_symb_rnd, Range: (20, 30), Mean Profit: 33.5947
Agent: agent2_symb_rnd, Range: (30, 50), Mean Profit: 25.9735
Agent: agent2_symb_rnd, Range: (50, 80), Mean Profit: 16.6388
Agent: agent2_symb_rnd, Range: (80, 120), Mean Profit: 15.2035
Agent: agent2_symb_rnd, Range: (120, 170), Mean Profit: 18.0949
Agent: agent2_symb_rnd, Range: (170, 230), Mean Profit: 15.1973
Agent: agent2_symb_rnd, Range: (230, 300), Mean Profit: 9.8963
Agent: agent2_symb_rnd, Range: (300, 365), Mean Profit: 1.2643


Agent: agent2_top_avg_vol, Range: (0, 0), Mean Profit: -5.4332
Agent: agent2_top_avg_vol, Range: (1, 5), Mean Profit: 112.6681
Agent: agent2_top_avg_vol, Range: (5, 10), Mean Profit: 55.4256
Agent: agent2_top_avg_vol, Range: (10, 20), Mean Profit: 37.8074
Agent: agent2_top_avg_vol, Range: (20, 30), Mean Profit: 28.8353
Agent: agent2_top_avg_vol, Range: (30, 50), Mean Profit: 23.5107
Agent: agent2_top_avg_vol, Range: (50, 80), Mean Profit: 16.3322
Agent: agent2_top_avg_vol, Range: (80, 120), Mean Profit: 14.7021
Agent: agent2_top_avg_vol, Range: (120, 170), Mean Profit: 18.0364
Agent: agent2_top_avg_vol, Range: (170, 230), Mean Profit: 16.1035
Agent: agent2_top_avg_vol, Range: (230, 300), Mean Profit: 14.0542
Agent: agent2_top_avg_vol, Range: (300, 365), Mean Profit: 5.0561


Agent: agent3_symb_rnd, Range: (0, 0), Mean Profit: -11.5189
Agent: agent3_symb_rnd, Range: (1, 5), Mean Profit: 217.1134
Agent: agent3_symb_rnd, Range: (5, 10), Mean Profit: 99.4337
Agent: agent3_symb_rnd, Range: (10, 20), Mean Profit: 59.1326
Agent: agent3_symb_rnd, Range: (20, 30), Mean Profit: 41.6844
Agent: agent3_symb_rnd, Range: (30, 50), Mean Profit: 28.5218
Agent: agent3_symb_rnd, Range: (50, 80), Mean Profit: 18.8775
Agent: agent3_symb_rnd, Range: (80, 120), Mean Profit: 18.039
Agent: agent3_symb_rnd, Range: (120, 170), Mean Profit: 20.4543
Agent: agent3_symb_rnd, Range: (170, 230), Mean Profit: 17.6958
Agent: agent3_symb_rnd, Range: (230, 300), Mean Profit: 9.7364
Agent: agent3_symb_rnd, Range: (300, 365), Mean Profit: 0.849


Agent: agent3_top_avg_vol, Range: (0, 0), Mean Profit: -5.5243
Agent: agent3_top_avg_vol, Range: (1, 5), Mean Profit: 117.654
Agent: agent3_top_avg_vol, Range: (5, 10), Mean Profit: 58.2777
Agent: agent3_top_avg_vol, Range: (10, 20), Mean Profit: 38.7703
Agent: agent3_top_avg_vol, Range: (20, 30), Mean Profit: 28.5974
Agent: agent3_top_avg_vol, Range: (30, 50), Mean Profit: 23.0941
Agent: agent3_top_avg_vol, Range: (50, 80), Mean Profit: 16.0483
Agent: agent3_top_avg_vol, Range: (80, 120), Mean Profit: 17.831
Agent: agent3_top_avg_vol, Range: (120, 170), Mean Profit: 17.2397
Agent: agent3_top_avg_vol, Range: (170, 230), Mean Profit: 17.515
Agent: agent3_top_avg_vol, Range: (230, 300), Mean Profit: 17.3715
Agent: agent3_top_avg_vol, Range: (300, 365), Mean Profit: 7.3835


Agent: agent4_symb_rnd, Range: (0, 0), Mean Profit: -9.8463
Agent: agent4_symb_rnd, Range: (1, 5), Mean Profit: 199.0612
Agent: agent4_symb_rnd, Range: (5, 10), Mean Profit: 68.2679
Agent: agent4_symb_rnd, Range: (10, 20), Mean Profit: 42.9081
Agent: agent4_symb_rnd, Range: (20, 30), Mean Profit: 33.1626
Agent: agent4_symb_rnd, Range: (30, 50), Mean Profit: 24.1544
Agent: agent4_symb_rnd, Range: (50, 80), Mean Profit: 16.6614
Agent: agent4_symb_rnd, Range: (80, 120), Mean Profit: 15.6794
Agent: agent4_symb_rnd, Range: (120, 170), Mean Profit: 17.3034
Agent: agent4_symb_rnd, Range: (170, 230), Mean Profit: 15.655
Agent: agent4_symb_rnd, Range: (230, 300), Mean Profit: 8.946
Agent: agent4_symb_rnd, Range: (300, 365), Mean Profit: 0.5922


Agent: agent4_top_avg_vol, Range: (0, 0), Mean Profit: -5.4332
Agent: agent4_top_avg_vol, Range: (1, 5), Mean Profit: 110.013
Agent: agent4_top_avg_vol, Range: (5, 10), Mean Profit: 55.2478
Agent: agent4_top_avg_vol, Range: (10, 20), Mean Profit: 38.5342
Agent: agent4_top_avg_vol, Range: (20, 30), Mean Profit: 29.3867
Agent: agent4_top_avg_vol, Range: (30, 50), Mean Profit: 23.7452
Agent: agent4_top_avg_vol, Range: (50, 80), Mean Profit: 16.3789
Agent: agent4_top_avg_vol, Range: (80, 120), Mean Profit: 16.5274
Agent: agent4_top_avg_vol, Range: (120, 170), Mean Profit: 18.5768
Agent: agent4_top_avg_vol, Range: (170, 230), Mean Profit: 16.1523
Agent: agent4_top_avg_vol, Range: (230, 300), Mean Profit: 13.5133
Agent: agent4_top_avg_vol, Range: (300, 365), Mean Profit: 5.176


Agent: agent5_symb_rnd, Range: (0, 0), Mean Profit: -8.1718
Agent: agent5_symb_rnd, Range: (1, 5), Mean Profit: 201.7323
Agent: agent5_symb_rnd, Range: (5, 10), Mean Profit: 73.4301
Agent: agent5_symb_rnd, Range: (10, 20), Mean Profit: 44.7016
Agent: agent5_symb_rnd, Range: (20, 30), Mean Profit: 33.545
Agent: agent5_symb_rnd, Range: (30, 50), Mean Profit: 24.6567
Agent: agent5_symb_rnd, Range: (50, 80), Mean Profit: 16.5709
Agent: agent5_symb_rnd, Range: (80, 120), Mean Profit: 14.9209
Agent: agent5_symb_rnd, Range: (120, 170), Mean Profit: 16.5372
Agent: agent5_symb_rnd, Range: (170, 230), Mean Profit: 15.0387
Agent: agent5_symb_rnd, Range: (230, 300), Mean Profit: 8.7945
Agent: agent5_symb_rnd, Range: (300, 365), Mean Profit: -0.0644


Agent: agent5_top_avg_vol, Range: (0, 0), Mean Profit: -5.2446
Agent: agent5_top_avg_vol, Range: (1, 5), Mean Profit: 107.3002
Agent: agent5_top_avg_vol, Range: (5, 10), Mean Profit: 54.6493
Agent: agent5_top_avg_vol, Range: (10, 20), Mean Profit: 37.0422
Agent: agent5_top_avg_vol, Range: (20, 30), Mean Profit: 28.3456
Agent: agent5_top_avg_vol, Range: (30, 50), Mean Profit: 23.4053
Agent: agent5_top_avg_vol, Range: (50, 80), Mean Profit: 15.4671
Agent: agent5_top_avg_vol, Range: (80, 120), Mean Profit: 15.2262
Agent: agent5_top_avg_vol, Range: (120, 170), Mean Profit: 17.3575
Agent: agent5_top_avg_vol, Range: (170, 230), Mean Profit: 15.1753
Agent: agent5_top_avg_vol, Range: (230, 300), Mean Profit: 13.048
Agent: agent5_top_avg_vol, Range: (300, 365), Mean Profit: 4.2747


Agent: agent6_top_avg_vol, Range: (0, 0), Mean Profit: -6.2789
Agent: agent6_top_avg_vol, Range: (1, 5), Mean Profit: 148.5546
Agent: agent6_top_avg_vol, Range: (5, 10), Mean Profit: 54.8101
Agent: agent6_top_avg_vol, Range: (10, 20), Mean Profit: 37.924
Agent: agent6_top_avg_vol, Range: (20, 30), Mean Profit: 29.1668
Agent: agent6_top_avg_vol, Range: (30, 50), Mean Profit: 22.5133
Agent: agent6_top_avg_vol, Range: (50, 80), Mean Profit: 15.2072
Agent: agent6_top_avg_vol, Range: (80, 120), Mean Profit: 14.3538
Agent: agent6_top_avg_vol, Range: (120, 170), Mean Profit: 14.5395
Agent: agent6_top_avg_vol, Range: (170, 230), Mean Profit: 14.4204
Agent: agent6_top_avg_vol, Range: (230, 300), Mean Profit: 11.29
Agent: agent6_top_avg_vol, Range: (300, 365), Mean Profit: 5.756


Agent: agent7_symb_rnd, Range: (0, 0), Mean Profit: -9.491
Agent: agent7_symb_rnd, Range: (1, 5), Mean Profit: 242.9858
Agent: agent7_symb_rnd, Range: (5, 10), Mean Profit: 69.782
Agent: agent7_symb_rnd, Range: (10, 20), Mean Profit: 46.8824
Agent: agent7_symb_rnd, Range: (20, 30), Mean Profit: 32.4617
Agent: agent7_symb_rnd, Range: (30, 50), Mean Profit: 25.0912
Agent: agent7_symb_rnd, Range: (50, 80), Mean Profit: 16.4827
Agent: agent7_symb_rnd, Range: (80, 120), Mean Profit: 16.6143
Agent: agent7_symb_rnd, Range: (120, 170), Mean Profit: 15.6483
Agent: agent7_symb_rnd, Range: (170, 230), Mean Profit: 16.7287
Agent: agent7_symb_rnd, Range: (230, 300), Mean Profit: 7.4753
Agent: agent7_symb_rnd, Range: (300, 365), Mean Profit: -2.4628


Agent: agent7_top_avg_vol, Range: (0, 0), Mean Profit: -5.4332
Agent: agent7_top_avg_vol, Range: (1, 5), Mean Profit: 112.6681
Agent: agent7_top_avg_vol, Range: (5, 10), Mean Profit: 55.4256
Agent: agent7_top_avg_vol, Range: (10, 20), Mean Profit: 37.8074
Agent: agent7_top_avg_vol, Range: (20, 30), Mean Profit: 28.8353
Agent: agent7_top_avg_vol, Range: (30, 50), Mean Profit: 23.5107
Agent: agent7_top_avg_vol, Range: (50, 80), Mean Profit: 16.3322
Agent: agent7_top_avg_vol, Range: (80, 120), Mean Profit: 14.7021
Agent: agent7_top_avg_vol, Range: (120, 170), Mean Profit: 18.0364
Agent: agent7_top_avg_vol, Range: (170, 230), Mean Profit: 16.1035
Agent: agent7_top_avg_vol, Range: (230, 300), Mean Profit: 14.0542
Agent: agent7_top_avg_vol, Range: (300, 365), Mean Profit: 5.0561


Agent: agent8_symb_rnd, Range: (0, 0), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (1, 5), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (5, 10), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (10, 20), Mean Profit: 133.9909
Agent: agent8_symb_rnd, Range: (20, 30), Mean Profit: 50.1156
Agent: agent8_symb_rnd, Range: (30, 50), Mean Profit: 29.9019
Agent: agent8_symb_rnd, Range: (50, 80), Mean Profit: 19.7851
Agent: agent8_symb_rnd, Range: (80, 120), Mean Profit: 14.1642
Agent: agent8_symb_rnd, Range: (120, 170), Mean Profit: 6.7572
Agent: agent8_symb_rnd, Range: (170, 230), Mean Profit: 0.2909
Agent: agent8_symb_rnd, Range: (230, 300), Mean Profit: 0
Agent: agent8_symb_rnd, Range: (300, 365), Mean Profit: 0


Agent: agent8_top_avg_vol, Range: (0, 0), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (1, 5), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (5, 10), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (10, 20), Mean Profit: 52.5628
Agent: agent8_top_avg_vol, Range: (20, 30), Mean Profit: 34.8884
Agent: agent8_top_avg_vol, Range: (30, 50), Mean Profit: 24.9094
Agent: agent8_top_avg_vol, Range: (50, 80), Mean Profit: 21.4649
Agent: agent8_top_avg_vol, Range: (80, 120), Mean Profit: 14.75
Agent: agent8_top_avg_vol, Range: (120, 170), Mean Profit: 6.8689
Agent: agent8_top_avg_vol, Range: (170, 230), Mean Profit: 4.745
Agent: agent8_top_avg_vol, Range: (230, 300), Mean Profit: 0
Agent: agent8_top_avg_vol, Range: (300, 365), Mean Profit: 0
"""
























############################################################################################################







    
############################################################################################################





    


    

        
    


    


        

def plot_number_test_date(cur, conn):

    # Esegui una query per raggruppare per initial_date e calcolare la media dei profit_perc
    query = """
        SELECT initial_date, count(*) as num_test
        FROM testing_data
        GROUP BY initial_date
        ORDER BY initial_date;
    """
    cur.execute(query)
    results = cur.fetchall()
    
    
    # Estrai le date e i valori medi
    # Assumiamo che initial_date sia in formato datetime o stringa formattata
    dates = [row[0] for row in results]
    count_test = [row[1] for row in results]
    
    # Se le date sono stringhe, convertili in oggetti datetime
    if isinstance(dates[0], str):
        dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in dates]
    
    # Crea il grafico
    plt.figure(figsize=(12,6))
    plt.plot(dates, count_test, marker="o", linestyle="-", color='blue')
    plt.xlabel("Data di inizio della simulazione")
    plt.ylabel("Numero di test per la data")
    plt.title("Distribution of number of test for each date")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_number_test_date_distribution(cur, conn):
    """
    Mostra un istogramma che indica quante date hanno X test,
    fornendo così la distribuzione del numero di test per data.
    """
    
    # Query: per ogni data, quanti test ci sono
    query = """
        SELECT initial_date, COUNT(*) as num_test
        FROM testing_data
        GROUP BY initial_date
        ORDER BY initial_date;
    """
    cur.execute(query)
    results = cur.fetchall()
    
    # Estraggo solo la colonna 'num_test'
    count_test = [row[1] for row in results]
    
    # Istogramma: asse X = numero di test in una data,
    # asse Y = quante date hanno quel numero di test
    plt.figure(figsize=(10,6))
    plt.hist(count_test, bins=30, color='skyblue', alpha=0.7)
    
    plt.xlabel("Numero di test in una data")
    plt.ylabel("Frequenza (quante date hanno quel numero di test)")
    plt.title("Distribuzione del numero di test per data")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()



def plot_profit_perc_in_avg_time_sale(cur, conn):
     # Esegui una query per raggruppare per tempo medio che intercorre tra l'acquisto e la vendita e calcolare la media dei profit_perc
    query = """
        SELECT avg_sale_time_days, AVG(profit_perc) as avg_profit
        FROM testing_data
        GROUP BY avg_sale_time_days
        ORDER BY avg_sale_time_days;
    """
    cur.execute(query)
    results = cur.fetchall()
    
    # Estrai i tempi medi e i valori medi
    dates = [row[0] for row in results]
    avg_profits = [row[1] for row in results]
    
  
    # Crea il grafico
    plt.figure(figsize=(12,6))
    plt.plot(dates, avg_profits, marker="o", linestyle="-", color='blue')
    plt.xlabel("Tempi in giorni che intercorrono tra l'acquisto e la vendita")
    plt.ylabel("Profitto Percentuale Medio")
    plt.title("Media dei Profitti Percentuali per Tempi che intercorrono tra l'acquisto e la vendita")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    return
    
    
    
    
    
    
if __name__ == '__main__':
    # Crea la cartella solo se non esiste
    os.makedirs(f"{project_root}/data/result/plot", exist_ok=True)
    
    # Connect to database
    cur, conn = connectDB.connect_data_backtesting()
    
    """
    plot_mean_profit_every_agent(cur)
    plot_dev_std_every_agent(cur)
    plot_mean_profit_every_agent_market(cur)
    
    plot_distribution_mean_profit(cur)
    plots_distribution_mean_profit_every_agent(cur)
    one_plot_distribution_mean_profit_every_agent(cur)
    
    plot_profit_by_agent_boxplot(cur)
    plot_mean_profit_every_date_initial_test(cur)
    plot_mean_profit_every_date_initial_test_every_agent(cur)
    plot_mean_profit_every_date_initial_test_every_market(cur)
    
    
    plot_mean_N_purchases_every_agent(cur)
    plot_mean_N_sales_every_agent(cur)
    """
    
    #plot_distribution_detention_time(cur)
    #plots_distribution_detention_time_every_agent(cur)
     
    #plot_distribution_detention_time(cur)
    #plot_mean_profit_every_take_profit(cur)
    
    
    #table_correlation_profit_perc_detention_time(cur)
    
    x = [1,2,3,4,5,6,7,8,9,10]
    y = [1,1,2,3,5,2,8,7,9,10]
    plt.plot(x, y, color = 'brown')
    
    # Impostare i ticks manualmente
    plt.yticks(range(0, 11))  # Da 0 a 10
    
    plt.show()
    
    # Close connection
    conn.close()