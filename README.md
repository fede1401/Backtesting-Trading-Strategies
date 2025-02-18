# Backetesting-Trading-strategies.
> **Sviluppo di trading agent** per l'analisi e la valutazione delle prestazioni di determinate strategie di trading attraverso simulazioni applicate a dati storici del mondo reale.


L'obiettivo principale è **trovare la strategia che genera il maggior profitto**. L’idea è che, se una strategia ha prodotto buoni risultati su dati passati, possa (con i dovuti caveat) mantenere performance interessanti anche in contesti di mercato attuali e futuri.

Nel dominio di questa applicazione, si effettuano simulazioni di trading su titoli azionari quotati sui mercati Nasdaq, NYSE e su alcuni simboli di rilevanti società europee a grande capitalizzazione.

---
## Sommario.
- [Caratteristiche Principali.](#caratteristiche-principali)
- [Quick Start.](#quick-start)
- [Struttura del Repository](#struttura-del-repository)
- [Descrizione sullo Sviluppo dei Trading Agent](#descrizione-sullo-sviluppo-dei-trading-agents)
  - [Agente 1: Scaricamento Dataset](#agente-1-scaricamento-dataset)
  - [Informazioni di Base per le Strategie](#informazioni-di-base-per-le-strategie)
  - [Metodologia di Valutazione delle Strategie](#metodologia-di-valutazione-delle-strategie)
- [Descrizione degli Agenti di Trading](#descrizione-degli-agenti-di-trading)
  - [Note sulle Varianti di Selezione dei Simboli](#note-sulle-variante-di-selezione-dei-simboli)
  - [Agente 2: Strategia Semplice con Take Profit](#agente-2-strategia-semplice-con-take-profit)
  - [Agente 3](#agente-3)
  - [Agente 4](#agente-4)
  - [Agente 5](#agente-5)
  - [Agente 6](#agente-6)
  - [Agente 7](#agente-7)
  - [Agente 8](#agente-8)
  - [Utilizzo di Sistemi e File Comuni](#utilizzo-di-sistemi-e-file-comuni)
- [Requisiti](#requisiti)
- [Preparazione dell’Ambiente ed Esecuzione dei Test](#preparazione-dellambiente-ed-esecuzione-dei-test)
  - [Sistema di Logging](#sistema-di-logging)
  - [Controllo degli Errori](#controllo-degli-errori)
  - [Struttura dei Percorsi](#struttura-dei-percorsi)
  - [Spiegazione dei Test](#spiegazione-dei-test)
- [Database PostgreSQL](#database-postgresql)
  - [Installazione e Creazione del Database](#installazione-e-creazione-del-database)
  - [Collegamento al DB](#collegamento-al-db)
  - [Eliminazione di Database e Utenti](#eliminazione-di-database-e-utenti)
- [Esempio di Report / Output](#esempio-di-report--output)
- [Licenza](#licenza)
- [Contatti](#contatti)

---

## Caratteristiche Principali
- **Simulazione su dati reali** provenienti da diverse Borse (Nasdaq, NYSE, Europa).
- **Modularità**: più agenti, ognuno con una strategia di trading specifica.
- **Database PostgreSQL** per la memorizzazione dei dati e l’analisi delle performance.
- **Logging e Monitoraggio** dei risultati e degli eventuali errori durante le simulazioni.
- **Ampio orizzonte temporale** (dal 1999 al 2025) e test randomizzati su 75 date diverse.

## Quick Start
1. **Clona il repository**:
   ```bash
   git clone https://github.com/fede1401/Backtesting-Trading-Strategies.git
   cd Backtesting-Trading-Strategies
   ```

2. **Installa le dipendenze** (quando il setup.py sarà disponibile, potrai usare un comando simile):
	```bash 
	python3 setup.py install
	```

3. **Configura il Database PostgreSQL** seguendo le istruzioni in [Installazione e Creazione del Database](#installazione-e-creazione-del-database) e in db-scripts.

4. **Esegui l’agente 1** se vuoi solo scaricare i dati e popolare il database:
	```bash
	python3 agent1.py
	```

5. **Esegui i test** completi con gli altri agenti:
	```bash
	python3 test_main.py
	```
	Nota: i test potrebbero richiedere tempi lunghi, a seconda della quantità di dati e della frequenza delle simulazioni.

--

## Struttura del Repository.
Ecco una panoramica delle cartelle principali:
- `test/`: include file come test_main.py che permettono l’esecuzione degli agenti e i test su diverse strategie.
- `work_historical/`: 
	- `agent/`: contiene i file agenti.py, che implementano le strategie di trading;
	- `utils/`: funzioni di utilità (per esempio, gestione date randomiche);
	- `database/`: script e file di connessione al DB (connectDB.py).
	- `symbols/`: file come manage_symbol.py per gestire l’individuazione dei titoli a maggior capitalizzazione.
- `scripts/`: script di controllo e manutenzione (ad esempio checkErrorData.py).
- `logs/`: cartella in cui vengono salvati i file di log delle simulazioni e degli errori.
- `data/`: contiene i file dei dati scaricati (dati di mercato storici) o generati (risultati o anomalie)

***

## Descrizione sullo sviluppo dei trading agents.
Il nucleo dell'applicazione si basa su:
- **implementazione dei diversi agenti**, ciascuno associato a una strategia di trading specifica.
- **valutazione dei risultati** di ogni agente tramite simulazioni, salvando criteri fondamentali, fra cui:
	- profitto percentuale : ((capitale finale - capitale iniziale)/capitale iniziale) * 100.
	- variazione.
	- deviazione standard.
	- tempo medio che intercorre tra un acquisto e una vendita.

Ogni agente, e quindi ogni strategia, include una serie di parametri configurabili: questi consentono di testare la stessa strategia variando tali parametri, osservando così quali combinazioni producano, nel tempo, i risultati migliori.

Per ogni spiegazione dell'agente verranno specificati questi parametri.

#### Agente 1: scaricamento dataset.
L'agente 1 è un **agente particolare** poiché non implementa una vera e propria strategia operativa di trading. Il suo compito è:
- **scaricare i dati di mercato** (prezzi di apertura, chiusura, massimi e minimi, ecc.) dai mercati di riferimento (Nasdaq, NYSE ed Europa).
- **inserire questi dati all’interno di un database** PostgreSQL per costituire lo storico necessario a tutti gli altri agenti.

In dettaglio, i dati memorizzati includono:
- **titolo azionario**;
- **time frame**: intervallo di tempo in cui viene campionato il prezzo (inizialmente 15 minuti, poi passato a cadenza giornaliera per migliorare la velocità delle simulazioni).
- **data di analisi** (il periodo di tempo a cui i dati si riferiscono).
- **prezzo iniziale**: prezzo di apertura del titolo azionario all'inizio del periodo.
- **prezzo più alto**: prezzo massimo raggiunto dal titolo azionario durante il periodo
- **prezzo più basso**: prezzo minimo raggiunto dall'azione durante il periodo
- **prezzo di chisura**: prezzo di chiusura dell'azione alla fine del periodo

Questa raccolta avviene tramite l’API yfinance, che permette di recuperare dati storici fino a date molto remote, fino ai giorni odierni, a intervalli giornalieri.

Il database PostgreSQL è scelto per la sua stabilità e per la possibilità di gestire grandi volumi di dati in modo affidabile.

L’Agente 1, in sintesi, fornisce la **base dati** su cui tutte le altre strategie opereranno.

***

#### Informazioni di base per le strategie.
Le strategie dei vari agenti (dal 2 all’8) si concentrano sull’acquisto e sulla vendita di titoli azionari.
L'obiettivo del trading è sfruttare le variazioni di prezzo dei titoli per ottenere profitti nel breve termine: l'obiettivo è acquistare e rivendere il titolo una volta che questo ha subito un'aumento del prezzo.
A seguire, alcuni aspetti comuni a tutte le strategie:
1. **Importo fisso di acquisto**: si spendono sempre 10 USD per ogni acquisto, e da qui si calcola il volume di azioni comprate.
Esempio: se il prezzo di acquisto di AAPL è 250 USD, allora il volume sarà 10/250=0,04 azioni.
2. **Prezzi di acquisto e vendita**:
- L’acquisto avviene sempre al prezzo di apertura del titolo relativo al timestamp considerato.
- La vendita avviene sempre al prezzo massimo relativo al timestamp considerato, questo permette anche una “vendita intra-day”.
3. **Strategia dell’investitore prudente**: di ogni profitto derivante da una vendita, il 10% viene reinvestito, mentre il restante 90% viene conservato (non più rimesso sul mercato). L’obiettivo è proteggere la maggior parte del guadagno, reinvestendo una quota limitata per “accelerare” la crescita.
4. **Selezione dei titoli**: si considera un insieme di titoli a maggiore capitalizzazione nel mercato analizzato (Nasdaq/NYSE/Europa). Questa selezione varia in base alle singole strategie, ma di norma si usa uno script che filtra i titoli per capitalizzazione di mercato e ne sceglie i primi X.

#### Metodologia di valutazione delle strategie.
Per misurare l’efficacia di ogni strategia e dei suoi parametri, si procede come segue:
1. **Finestra temporale di valutazione**: dal 1999 al 2025.
2. **Selezione di date casuali**: vengono scelte 75 date random (fra tutte quelle presenti nel dataset). Per ciascuna data selezionata, si valuta la strategia in un arco di 1 anno intero. Questo “singolo test” viene ripetuto per tutti i parametri della strategia.
3. **Memorizzazione dei risultati**: dopo ogni test si salvano su database:
- Data di inizio e data di fine test.
- Profitto in percentuale.
- Profitto in dollari.
- Numero di acquisti e vendite.
- Tempo medio fra acquisto e vendita.
- Titolo che ha generato il profitto maggiore.
- Titolo che ha generato il profitto minore.
4. **Media dei 75 test** (simulazione): al termine dei 75 test (per un singolo set di parametri), si calcola la media dei risultati e si salvano ulteriori indicatori:
- Percentuale media di profitti.
- Profitto medio in dollari.
- Varianza.
- Deviazione standard.
- Numero medio di acquisti.
- Numero medio di vendite.
- Titolo con maggior profitto medio.
- Titolo con minor profitto medio.

L’obiettivo di queste statistiche aggregate è fornire un quadro chiaro delle **prestazioni di ogni strategia** in contesti di mercato e parametri differenti, così da compiere una scelta informata su quale agente/strategia risulti globalmente più vantaggiosa.
***

## Descrizione degli Agenti di Trading.

### Note sulle Varianti di Selezione dei Simboli.
**Nota:** Per ogni agente (ad eccezione dell'agente 6) esistono due varianti operative:
- **Top MktCap:** I simboli vengono selezionati ordinando in modo decrescente la capitalizzazione dal mercato di riferimento **nella data in cui si effettua la simulazione**. La selezione è calcolata per ogni data di test; ad esempio, se il test per la strategia è relativo al 2002, la selezione dei simboli avverrà in base alla capitalizzazione decrescente dei simboli nel 2002.
Questo è stato fatto tramite le funzioni presenti nel file al percorso `work_historical/symbols/manage_symbol.py`.
- **Random:** I simboli vengono scelti in maniera casuale (ad esempio, 100 simboli) dal medesimo mercato.

Questa suddivisione permette un ulteriore confronto delle strategie dei test, poiché le simulazioni vengono effettuate con entrambe le varianti, consentendo di valutare l'impatto della modalità di selezione dei simboli sui risultati finali.


Le note di inserimento nel database sono create in modo conciso permettendo di comprendere quale valutazione è in atto.

---

#### Agente 2: strategia semplice con take profit.
L'agente 2 simula una strategia molto semplice: viene utilizzato come **strategia di riferimento** per gli altri agenti.
Questo utilizza un approccio iterativo per testare i seguenti **parametri** di take profit: 1,2,3,4,5,6,7,8,9,10,15,20,30,40,50,60,70,80,90,100 (in percentuale).
Grazie ai parametri si può valutare quale tra questi è quello che reagisce migliormente e dà più profitti.

##### Logica generale:
- Si parte con un budget iniziale di 1000 USD.
- Si acquistano i titoli a maggior capitalizzazione (nello specifico, 100 titoli fra i più capitalizzati) fino a esaurire il budget disponibile.
- Il parametro di take profit definisce la soglia percentuale di guadagno a cui il titolo viene venduto.
- Quando un titolo raggiunge questa soglia di profitto, si esegue la vendita, realizzando il guadagno e incrementando così il budget disponibile.
- Con il budget aggiornato si procede in un ciclo continuo di acquisti e vendite, finché la simulazione non termina.

Grazie a questa strategia base, si ottiene un primo benchmark sulle possibili prestazioni. Tutti gli altri agenti si appoggeranno al meccanismo dell’Agente 2, modificando o aggiungendo condizioni.

***

#### Agente 3.
L’Agente 3 estende la logica dell’Agente 2 introducendo una **condizione di acquisto basata sul prezzo medio del titolo**. In particolare:

1. Si calcola (pre-analisi) il prezzo medio storico del titolo nei 50 giorni precedenti.
2. Prima di acquistare un titolo, l’agente verifica che il prezzo attuale sia inferiore alla sua media calcolata.
3. Se il prezzo è realmente minore, si procede all’acquisto, ipotizzando che il titolo possa “tornare” verso il prezzo medio, guadagnandoci.
4. Si mantiene lo stesso schema di parametri di take profit dell’Agente 2.

L’aspettativa è che, comprando solo quando un titolo è “sottovalutato” rispetto alla media, si possano **ottenere rendimenti complessivi maggiori**, riducendo al contempo il rischio di acquistare a prezzi troppo alti.

***

#### Agente 4.
L'agente 4 riprende la base dell’Agente 2, ma differisce poiché una volta venduto un titolo azionario si va a **riacquistare lo stesso titolo** dopo un delay definito. 
La modifica principale è:
1. Una volta venduto un titolo, non lo si riacquista immediatamente, ma si attende un numero di giorni definito dal parametro “delay”.
2. I parametri da testare includono non solo il take profit, ma anche tutti i possibili valori di delay fra 1 e 15 giorni.
3. Questi parametri vengono combinati nelle simulazioni, in modo da individuare la coppia (take profit, delay) più redditizia.

L’idea alla base: lasciare “decantare” il titolo dopo la vendita, per vedere se un ritracciamento del prezzo consenta un nuovo ingresso più conveniente.

***

#### Agente 5.
L’Agente 5 introduce **variazioni nel numero di titoli su cui operare e nel budget iniziale**, pur mantenendo la stessa logica di base dell’Agente 2. In particolare, si valutano diverse coppie:
- **100 titoli** azionari a maggiore capitalizzazione e **1000 USD** di budget iniziale;
- **200 titoli** azionari a maggiore capitalizzazione e **2000 USD** di budget iniziale;
- **300 titoli** azionari a maggiore capitalizzazione e **3000 USD** di budget iniziale;  
...
- **800 titoli** azionari a maggiore capitalizzazione e **8000 USD** di budget iniziale; 

Per ogni combinazione (numero di titoli – budget), si eseguono i test e si misurano i parametri di valutazione. In questo modo, si capisce come il capitalizzare un maggior numero di titoli (quindi diversificando) e disporre di un budget più elevato possa influire sui risultati e se esiste un “punto di equilibrio” fra l’aumento dei titoli/budget e la redditività complessiva.

#### Agente 6.
L’Agente 6 si basa sulla stessa strategia dell’Agente 2 ma **seleziona i titoli in modo diverso**: invece di prendere i titoli a maggior capitalizzazione senza distinzione, li filtra per settore e ne preleva una certa percentuale tra i top di quel settore. I parametri testati sono:
- 10% dei titoli a maggior capitalizzazione di ogni settore.
- 20% dei titoli a maggior capitalizzazione di ogni settore.
- 30%, 40%, 50%... e così via.

L’aspettativa è capire se diversificare la scelta dei titoli per settore (anziché considerare il mercato globale) comporti un guadagno maggiore o una riduzione del rischio.

***

#### Agente 7.
L’Agente 7 mantiene la struttura e i parametri dell’Agente 2, ma **estende la finestra temporale per il singolo test da 1 anno a 2 anni**. 
Questa differenza consente di studiare l’impatto di una visione più lungo-termine sul funzionamento del take profit e di capire se una strategia originariamente pensata per il breve termine possa diventare più (o meno) profittevole su un orizzonte doppio.

#### Agente 8.
L'agente 8 sfrutta la strategia del **TSL: trailing stop loss**.
Questa strategia si basa sulla vendita di un titolo azionario quando il suo prezzo scende sotto una certa soglia.
L'obiettivo è ottenere un profitto, tenendo salva una percentuale di profitto che il titolo ha già guadagnato.
La strategia si basa su due parametri fondamentali:
- α (alpha): indica la soglia per cui attivare la strategia del TSL. Se il profitto del titolo azionario supera alpha, allora si attiva la strategia del TSL.
- β (beta): indica la percentuale per cui il prezzo del titolo azionario deve scendere rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.

L’idea è **garantire un profitto minimo** nel momento in cui il titolo abbia superato la soglia α, fissando un prezzo sotto il quale si esce dalla posizione per **preservare parte dei guadagni**

***

#### Utilizzo di sistemi e file comuni.
Per mantenere modularità e ordine nel codice, le funzioni e i calcoli comuni a più agenti sono posizionati in file condivisi. Ad esempio:
- manage_symbol.py (in /work_historical/symbols): individua i titoli azionari a maggior capitalizzazione in un periodo specifico.
- Funzioni per date randomiche (in /work_historical/utils): generano e gestiscono le date casuali per i test.
***

## Requisiti 
- Python 3.*+
- scaricamento librerie fondamentali per la creazione dell'environmente: (yfinance, ...)
Il file setup.py (ancora da completare) si occuperà di gestire l’installazione automatica di tutte le dipendenze necessarie.

***
## Preparazione dell’ambiente ed esecuzione dei test.
Per l'esecuzione delle simulazioni è prima fondamentale creare l'ambiente, poiché è su questo che verranno valutate le diverse strategie.
1. **Data setup**. 
- Per la preparazione dell'ambiente c'è l'**agente 1**: questo scarica e memorizza i dati di mercato storici e di capitalizzazione di mercato storici nel database (scaricati mediante un'algoritmo preciso).
Questi dati serviranno per tutte le simulazioni degli altri agenti.

2. **Esecuzione del main**.
- Nella cartella test è presente il file test_main.py, che include le procedure per il setup dell’ambiente e l’esecuzione di tutti gli agenti relativi alle strategie di trading elaborate e spiegate precedentemente. (2, 3, 4, 5, 6, 7, 8).

Per avviare il processo completo, basta eseguire: 
``` bash
python3 test_main.py
```

**Avviso**: L'esecuzione di questo programma include tempi di attesa per i risultati molto lunghi.

Se si desidera solo scaricare i dati, si può lanciare un apposito main (legato all’Agente 1) e commentare l’esecuzione degli altri agenti.

### Sistema di logging.
Per monitorare l’andamento dei test (es. risultati, errori e tempistiche) si utilizzano i file di log nella cartella /logs grazie a **sistema di logging Python** configurato per salvare:
- Eventuali errori logici o di runtime.
- Informazioni sui tempi di esecuzione.
- Dettagli sulle operazioni svolte da ciascun agente.
Parte dei risultati viene inoltre memorizzata nel database per analisi successive più approfondite.

### Controllo degli errori.
Dato che il dataset è stato generato internamente dall’Agente 1, è presente uno **script di controllo per evidenziare possibili anomalie nei dati di mercato scaricati**. Il suo funzionamento si basa sul confronto tra:
- Prezzo di apertura e prezzo massimo nello stesso giorno.
- Prezzo di apertura e prezzo massimo nel giorno successivo (per verificare incongruenze non realistiche).

Questo script, checkErrorData.py, si trova nella cartella /scripts e serve a **evidenziare differenze anomale** che potrebbero inficiare le simulazioni (visto che acquisto e vendita, in queste strategie, utilizzano proprio prezzo di apertura e prezzo massimo come valori di riferimento).

### Struttura dei percorsi.
Per gestire i percorsi dei file e delle cartelle in modo dinamico, è presente un algoritmo nel file manage_module.py. In sintesi:
1. Un ciclo individua la root del progetto.
2. Vengono definiti i percorsi fondamentali (cartelle log, cartelle script, ecc.).
3. Una funzione aggiunge la root al sys.path (se non già presente) per consentire import di file da posizioni diverse senza conflitti.

In tutti gli altri file, quindi, si può importare facilmente sia la root sia i vari moduli, usufruendo dei percorsi definiti in manage_module.py.

***

### Spiegazione dei test.
I test verranno eseguiti su un dataset molto ampio. L'elevato numero di test e simulazioni può comportare tempi di esecuzione significativi.
Si può pensare che le tabelle del database relative ai dati di mercato raggiungono milioni di record. Per questo effettuare delle query può risultare abbastanza inefficiente.
Per questo per ottimizzare:
- prima di far partire le strategie, si **recuperano i dati dal database o da alcuni file di appoggio, memorizzandoli in specifiche strutture dati**: dizionari, in memoria.
- l’indicizzazione nei dizionari è molto più rapida, riducendo drasticamente i tempi di accesso ai dati.

***

## Database postgreSQL.
In una sistema come questo, la gestione e la memorizzazione dei dati è fondamentale per la comprensione e la valutazione delle strategie di trading.

#### Installazione e creazione del database.
1. Seguire la guida ufficiale su: https://www.postgresql.org/download/linux/ubuntu/ per installare postgreSQL.
2. All’interno della cartella db-scripts sono presenti:
- **Definizione nome DB e utente;**
- **Creazione utente postgreSQL;**
- **Creazione schema con varie tabelle;**
- **Definizione privilegi;**
- **Script .sh per automatizzare i passaggi precedenti;**

Per creare il database, basta posizionarsi in db-scripts ed eseguire lo script .sh appropriato per il proprio sistema operativo.

#### Collegamento al DB.
Per il collegamento al database da terminale si utilizza il comando:
``` psql -U nome_utente -h localhost -d nome_db```, in questo caso si utilizza ``` psql -U reporting_user -h localhost -d data_backtesting -p 5433```
Verrà richiesta la password, presente nel file create-db-user.sql.

Nel codice, il file /work_historical/database/connectDB.py semplifica l’accesso al database e le query.
Una volta connessi si possono effettuare diverse query oppure inserimenti ed eliminazioni.

Esempi di comandi basilari in SQL:

##### Eliminare tutte le righe di una tabella:
``` 
DELETE FROM nome_tabella; 
```

##### Eliminare una tabella:
``` 
DROP TABLE nome_tabella; 
```

##### Cercare qualcosa in ordine decrescente:
``` 
SELECT nome_colonna FROM nome_tabella ORDER BY nome_colonna DESC
```

##### Tornare il risultato della query con un limite di righe:
``` 
SELECT nome_colonna FROM nome_tabella WHERE condizioni LIMIT 1
```
In questo caso con l'1 dopo il LIMIT torna solo una riga,...

***

##### Eliminare il database: o l'utente
Per effettuare l'eliminazione del database si complica poiché dobbiamo accedere come utente postgres. 
Ecco i seguenti passaggi:
1. ```sudo -i -u postgres ```
2. ``` psql ```
3. ```DROP DATABASE nome_database; ``` OR ```DROP USER nome_utente; ```

---

## Esempio di report / output.


---

## Licenza.


--- 

## Contatti.
Per informazioni, segnalazioni di bug o richieste di funzionalità:
- Apri una Issue su GitHub;
- Oppure contattami direttamente;

---

**Buon Trading e Buon Backtesting!**

