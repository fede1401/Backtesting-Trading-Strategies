# Backetesting-Trading-agent
> [!IMPORTANT]
> Sviluppo di **trading agent** per l'analisi e la valutazione delle prestazioni di determinate strategie di trading attraverso simulazioni applicate a dati storici del mondo reale.

L'obiettivo è trovare la strategia che rende maggiormente in termini di profitti.

Il fine è quello di applicare la stessa strategia dal vivo sperando che i buoni risultati in passato vengano garantiti anche nelle condizioni attuali e future del mercato.

Nel dominio della mia applicazione si effettuano simulazioni di trading con i simboli azionari quotati sulla borsa del Nasdaq, Nyse e di alcuni simboli azionari europei delle aziende più importanti (titoli a maggior capitalizzazione in europa).

***

## Descrizione sullo sviluppo dei trading agents.
Lo sviluppo sostanziale dell'applicazione si basa:
- sull'implementazioe dei diversi agenti, la quale ognuno di questi, implementa una strategia e 
- sulla valutazione di questi, che effettuate delle simulazioni salvando criteri importanti per la valutazione:
	- profitto percentuale calcolato come : ((capitale finale - capitale iniziale)/capitale iniziale) * 100.
	- variazione.
	- deviazione standard.
	- tempo medio che intercorre tra un acquisto e una vendita.

Per ogni agente, quindi per ogni strategia di trading, ci sono dei parametri che permettono di valutare la stessa strategia differenziando questi parametri. 

Per ogni spiegazione dell'agente verranno specificati questi parametri.

#### Agente 1: scaricamento dataset.
L'agente 1 è un agente particolare poiché non implementa una stratega, ma si occupa del raccoglimento e dello scaricamento dei dati di mercato relativi ai diversi mercati analizzati e dell'inserimento di questi all'interno del database postgreSQL.
I dati di mercato memorizzati nel database sono i seguenti:
- titolo azionario;
- time frame: considera l'intervallo di tempo con cui sono presi i dati.
- data di analisi: periodo di tempo per cui sono validi i dati.
- prezzo iniziale: prezzo di apertura del titolo azionario all'inizio del periodo.
- prezzo più alto: prezzo massimo raggiunto dal titolo azionario durante il periodo
- prezzo più basso: prezzo minimo raggiunto dall'azione durante il periodo
- prezzo di chisura: prezzo di chiusura dell'azione alla fine del periodo

Inizialmente i dati erano stati presi con un time frame di 15 minuti, ma questo non garantiva una velocità sufficientemente alta per le simulazioni.
Per lo scaricamento dei dati è stata utilizzata l'API yfinance, questa garantisce uno scaricamento di i dati di mercato relativi alle date più remote e quelle attuale in maniera precisa, tutto su cadenza giornaliera.

L'obiettivo di questo agente è quello di creare uno storico dove gli altre agenti possono valutare le diverse strategie.

È stato utilizzato il database postgreSQL per la memorizzazione dei dati.

La spiegazione dei prossimi agenti è relativa alle varie strategie di trading implementate.
#### Informazioni default per le seguenti strategie.
Ogni strategia di trading corrisponderà ad azioni di acquisto e vendita di titoli azionari. 
L'obiettivo del trading è sfruttare le variazioni di prezzo dei titoli: quindi il top sarebbe comprare e rivendere lo stesso titolo una volta che il prezzo del titolo è salito.
Si mira a guadagni di breve termine. 
- Per ogni acquisto si spende un importo fisso di 10 USD, questo permette di calcolare di conseguenza il volume. Ad esempio se vogliamo acquistare un'azione per il titolo AAPL, di cui il prezzo di acquisto è: 250, il volume corrisponderà a 10/250 = 0.04.
- Per effettuare un acquisto si utilizza il prezzo di apertura del titolo del timestamp di cui si acquista, per la vendita si utilizza il prezzo massimo del titolo del timestamp di cui si acquista: questo permette di implementare nelle strategie la vendita possibile nella stessa giornata.
- Si utilizza la strategia dell'investitore prudente che ad ogni vendita, il 10% del profitto lo utilizza per il reinvestimento e il 90% lo utilizza per il mantenimento.
- Si lavora con gli x titoli a maggior capitalizzazione del mercato di cui si lavora: per selezionare i titoli corrispondenti viene implementato uno script. 

#### Valutazione delle strategie.
Per la valutazione delle strategie, ci sono da chiarire alcuni aspetti importanti:
Le date per cui si valutano le strategie partono dal 1999 alla data attuale del 2025.
Come si è detto, ogni strategia ha dei parametri sulla quale valutare la strategia.
Quindi in base a questi parametri sono effettuati dei test di trading ben precisi:
- vengono selezionate 75 della date random tra quelle presenti nel dataset relativo ai dati di mercato dei titoli azionari.
Per ognuna di queste date (attraverso un semplice ciclo) viene valutata la strategia per 1 anno intero con il parametro considerati --> indichiamo con test
AL termine della valutazione vengono memorizzate nel database delle informazioni importanti:
- data di inizio e fine test;
- profitto in percentuale;
- profitto in dollari;
- numero acquisti;
- numero vendite;
- tempio medio che intercorre tra la vendita e gli acquisti;
- titolo che dà maggior profitti;
- titolo che dà minor profitto;

Una volta effettuati i 75 test per ognuna delle dati per il parametro considerato effettuiamo una media dellle informazioni già ottenute e salviamo nel database questi dati che rappresentano la valutazione della strategia per quel parametro specifico, con il salvataggio delle seguenti informazioni:
- percentuale media di profitti;
- profitti medi in dollari;
- varianza;
- deviazione standard;
- numero medio di acquisti;
- numero medio di vendite;
- titolo che dà maggior profitti (calcolando una media);
- titolo che dà minor profitto (calcolando una media);

Grazie a queste informazioni è possibile calcolare una stima relativa alle prestazioni della strategia di trading.



#### Agente 2: strategia semplice con take profit.
L'agente 2 simula una strategia molto semplice: viene utilizzato come reference per le altre strategie.
Questo utilizza un approccio iterativo per testare i seguenti parametri di take profit: 1,2,3,4,5,6,7,8,9,10,15,20,30,40,50,60,70,80,90,100 %.
Grazie ai parametri si può valutare quale tra questi è il parametro che reagisce migliormente e dà più profitti.

Ogni test sfrutta questa metodologia:
- partendo con un budget iniziale di 1000 dollari, si acquistano inizialmente titoli (100 titoli a maggior capitalizzazione) fino ad esaurimento del budget. A questo punto, dato il parametro con cui si sta valutando la strategia si prosegue, quando è possibile, alle vendite del titolo quando si raggiunge un profitto dato dal parametro valutato. 
Le vendite permettono di incrementare il budget per l'investimento e questo permette un ciclo continui di acquisti e vendite.

Questo agente è utilizzato come base per la creazione delle altre strategie.

#### Agente 3.
L'agente 3 utilizza come base l'agente 2, aggiunge una condizione tale per cui, prima di acquistare, controlla se il prezzo attuale del titolo è minore del prezzo medio di quel titolo (precalcolato).
Se il controllo va a buon fine si acquista il titolo poiché si aspetta una risalita del prezzo al prezzo medio.
Viene mantenuto lo stesso schema di parametri da valutare dell'agente 2.

#### Agente 4.
L'agente utilizza come base l'agente 2, ma differisce poiché una volta venduto un titolo azionario si va a riacquistare lo stesso titolo dopo un delay definito.
In questo caso, per i parametri di questo agente si utilizzano le metriche di take profit e anche i valori di delay per valutare quale sia il delay migliore tra 1 e 15 giorni.
Questi parametri vengono combinati tra loro.


#### Agente 5.
Anche l'agente 5 si basa sulla strategia dell'agente 2. 
In questo caso per ogni test e valutazione ci sono delle variazioni sul numero di titoli da considerare e sul budget iniziale. Questi sono strettamente collegati tra di loro, ad esempio: 
- **100 titoli** azionari a maggiore capitalizzazione e **1000 USD** di budget iniziale;
- **200 titoli** azionari a maggiore capitalizzazione e **2000 USD** di budget iniziale;
- **300 titoli** azionari a maggiore capitalizzazione e **3000 USD** di budget iniziale;  
...
- **800 titoli** azionari a maggiore capitalizzazione e **8000 USD** di budget iniziale; 

#### Agente 6.
L'agente 6 permette di effettuare trading sulla base dell'agente 2, ma selezionando una percentuale specifica dei titoli a maggior capitalizzazione 

#### Agente 7.

#### Agente 8.



***

## Database postgreSQL.
Importante creare il DB postgreSQL per il salvataggio, la comprensione e l'apprendimento dei dati.

Recarsi su :  https://www.postgresql.org/download/linux/ubuntu/ per installare postgreSQL.

Utilizzare la cartella "db-scripts" per:
- **Definizione nome DB e utente;**
- **Creazione utente postgreSQL;**
- **Creazione schema con varie tabelle;**
- **Definizione privilegi;**
- **Script per l'esecuzione dei compiti precedenti;**

Per creare il database, ci posizioniamo nella cartella db-scripts nel path della cartella relativa al progetto ed eseguire da Linux:
``` sh create.sh```

##### Collegamento da terminale al DB.
Per il collegamento al database da terminale si utilizza il comando
``` psql -U nome_utente -h localhost -d nome_db```, in questo caso si utilizza ``` psql -U federico -h localhost -d nasdaq```

verrà chiesta una password che si trova nel file "create-db-user.sql".

Una volta entrati possiamo effettuare diverse query oppure inserimenti ed eliminazioni.

Ad esempio se volessimo:
##### Eliminare tutte le righe di una tabella:
``` DELETE FROM nome_tabella; ```

##### Eliminare una tabella:
``` DROP TABLE nome_tabella; ```

##### Cercare qualcosa in ordine decrescente:
```  SELECT nome_colonna FROM nome_tabella ORDER BY nome_colonna DESC```

##### Tornare il risultato della query con un limite di righe:
``` SELECT nome_colonna FROM nome_tabella WHERE condizioni LIMIT 1```
In questo caso con l'1 dopo il LIMIT torna solo una riga,...

***

##### Eliminare il database: o l'utente
Per effettuare l'eliminazione del database si complica poiché dobbiamo accedere come utente postgres. 
Ecco i seguenti passaggi:
1. ```sudo -i -u postgres ```
2. ``` psql ```
3. ```DROP DATABASE nome_database; ``` OR ```DROP USER nome_utente; ```

****

