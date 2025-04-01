# Backetesting-Trading-strategies
**Sviluppo e validazione di trading agents**, ovvero agenti software progettati per operare autonomamente all'interno del mercato azionario.
Il loro compito è **analizzare constantemente i dati di mercato** ed **eseguire operazioni di acquisto e di vendita** secondo _regole_ e _strategie_ ben definite.

Ogni agente segue una strategia di trading precisa.

Per valutare l'efficacia di queste strategie, ho implementato un **sistema di simulazione basato su dati di mercato storici**. Ciò mi ha permesso di testare il comportamento degli agenti in scenari di mercato concreti. 

L'obiettivo principale è **trovare la strategia ottimale a seconda delle esigenze di un potenziale trader**. Questa può puntare alla massimizzazione del profitto, oppure alla stabilità, minimizzando i rischi.
L’idea è che, se una strategia ha prodotto buoni risultati su dati passati, possa mantenere performance interessanti anche in contesti di mercato attuali e futuri.

Nel dominio di questa applicazione, si lavora titoli azionari quotati sui mercati _Nasdaq_, _NYSE_ e su alcuni _simboli di rilevanti società europee a grande capitalizzazione_.

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

---

## Struttura del Repository
Ecco una panoramica delle cartelle principali:
- `test/`: include file come test_main.py (per l’esecuzione degli agenti e i test su diverse strategie), generate_plot.py (per la generazione dei plot in base ai risultati ottenuti dagli esperimenti)
- `work_historical/`: 
	- `agents/`: contiene i file agenti.py, che implementano le strategie di trading;
	- `utils/`: funzioni di utilità (per esempio, gestione date randomiche);
	- `database/`: script e file di connessione al DB (connectDB.py).
	- `symbols/`: file come manage_symbol.py per gestire l’individuazione dei titoli a maggior capitalizzazione.
- `scripts/`: script di controllo e manutenzione (ad esempio checkErrorData.py).
- `logs/`: cartella in cui vengono salvati i file di log delle simulazioni e degli errori.
- `data/`: contiene i file dei dati scaricati (dati di mercato storici) o generati (risultati o anomalie)

***



## Motivazioni e Soluzioni
Per chi non avesse familiarità con il tema, il **trading azionario** si traduce nell’acquisto e nella vendita di titoli azionari con l’obiettivo di trarre un profitto dalle variazioni di prezzo positive.
Molti trader inesperti subiscono perdite significative poiché operare nel mercato azionario non è facile: si tratta di un ambiente dinamico influenzato da fattori economici, politici e psicologici.

Come si possono **minimizzare i rischi e ottimizzare i risultati nel trading?**
Il primo passo fondamentale è studiare e definire una strategia efficace: comprare azioni in modo completamente casuale è praticamente inutile.
Successivamente è molto importante simulare le strategie sui dati di mercato del passato e quindi in scenari reali poich´e anche conoscendo molto bene un mercato, non vi è una garanzia che una strategia ”ben pensata sulla carta” possa produrre risultati positivi nella realtà.

Viene garantita l'**automazione**, vantaggiosa perché consente un intervento istantaneo laddove si presenti un’opportunità di guadagno, riducendo al minimo il fattore psicologico.


## Descrizione sullo sviluppo dei trading Agents
Il nucleo dell'applicazione si basa su:
- **implementazione dei diversi agenti**, ciascuno associato a una strategia di trading specifica.
- **esecuzione dgli esperimenti** su numerose combinazioni di condizioni: strategia di selezione titoli, parametri specifici, uno dei tre mercati e una delle 76 date casuali estratte dal periodo 1999–2025.
- **valutazione dei risultati** di ogni agente tramite simulazioni, salvando criteri fondamentali, fra cui:
	- profitto percentuale : ((capitale finale - capitale iniziale)/capitale iniziale) * 100.
	- variazione.
	- deviazione standard.
	- tempo medio che intercorre tra un acquisto e una vendita.

Ogni agente, e quindi ogni strategia, include una serie di **parametri configurabili**: questi consentono di testare la stessa strategia variando tali parametri, osservando così quali combinazioni producano, nel tempo, i risultati migliori.

Per ogni spiegazione dell'agente verranno specificati questi parametri.

### Agente 1: scaricamento dataset.
Prima di progettare gli agenti di trading, è stato necessario costruire una solida base di dati su cui testare le strategie. Questo compito è stato affidato all’**Agente 1**, un agente particolare che non implementa una vera e propria strategia operativa di trading, ma si occupa di:
- **scaricare i dati di mercato** (prezzi di apertura, chiusura, massimi e minimi, ecc.) dai mercati di riferimento.
- **inserire questi dati all’interno di un database** PostgreSQL per costituire lo storico necessario a tutti gli altri agenti.

In dettaglio, i dati memorizzati includono:
- **titolo azionario**;
- **time frame**: intervallo di tempo in cui viene campionato il prezzo (inizialmente 15 minuti, poi passato a cadenza giornaliera per migliorare la velocità delle simulazioni).
- **data di analisi** (il periodo di tempo a cui i dati si riferiscono).
- **prezzo iniziale**: prezzo di apertura del titolo azionario all'inizio del periodo.
- **prezzo più alto**: prezzo massimo raggiunto dal titolo azionario durante il periodo
- **prezzo più basso**: prezzo minimo raggiunto dall'azione durante il periodo
- **prezzo di chisura**: prezzo di chiusura dell'azione alla fine del periodo

Per ottenere dati affidabili ho utilizzato l’API yfinance, che mi ha permesso di recuperare dati storici su un ampio orizzonte temporale, dal 1999
ad oggi, escludendo le giornate in cui i mercati erano chiusi, come i weekend e le festività.

Per garantire un’analisi pi`u ampia e rappresentativa, sono stati considerati tre mercati principali:
- **NASDAQ**, caratterizzato da titoli tecnologici.
- **NYSE**, con titoli di aziende più consolidate.
- **Titoli europei a grande capitalizzazione**, per una maggiore diversificazione.

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
4. **Selezione dei titoli**: si considera un insieme di titoli a maggiore volume scambiato (Nasdaq/NYSE/Europa). Questa selezione varia in base alle singole strategie, ma di norma si usa uno script che filtra i titoli per volume scambiato e ne sceglie i primi X.


### Test e Simulazioni
Per valutare le diverse strategie di trading implementate sull'ambiente di simulazione ogni Agente viene **testato su numerose combinazioni di condizioni**: 
- metodologia di selezione di simboli su cui lavorare;
- parametri specifici dell'agente;
-  uno dei tre mercati considerati;
- una delle 76 date casuali estratte dal periodo 1999–2025.
Ogni test simula un anno di attività di trading.

**_Esempio pratico_**: Consideriamo l’agente 2. Questo agente viene testato iterando
su vari valori di take profit, ad esempio :
_1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100%_
Per ognuno di questi valori, l’agente:
1. Seleziona uno dei tre mercati (Nasdaq, NYSE, Europa).
2. Adotta una delle due strategie di scelta dei titoli (random vs top average volume).
3. Esegue 76 test, ciascuno relativo a una data casuale (compresa tra il 1999 e il
2025).
   
Per esempio, un singolo test potrebbe essere “Agente 2 con take profit= 1%, su Nasdaq, con selezione random, a partire dal 17 dicembre 1999 no al 17 dicembre 2000”. 
Ripetendo questa procedura per tutte le combinazioni, si ottengono:
2 x 20 x 76 x 3 = 9120 test
dove:
- 2 varianti operative relative alla selezione dei simboli;
- 20: i valori di take profit;
- 76: le date causali estratte;
- 3: mercati considerati per il lavoro di tesi;
solamente per l'Agente 2.


### Metodologia di valutazione delle strategie.
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
- **Top average volume:** I simboli vengono selezionati ordinando in modo decrescente il volume scambiato del titolo di riferimento **nella data in cui si effettua la simulazione**. La selezione è calcolata per ogni data di test; ad esempio, se il test per la strategia è relativo al 2002, la selezione dei simboli avverrà in base al volume scambiato per quei titoli nel 2002.
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

## Risultati ottenuti.
Analizzando la documentazione si possono osservare i dettagli dei risultati ottenuti.
Le conclusioni generali includono:

#### Andamento generale dei risultati
L’analisi della distribuzione dei profitti nelle simulazioni permette di comprendere l’andamento generale delle strategie testate.
La maggior parte dei test registra profitti compresi tra 0% e 30%, con una media complessiva del +22% annuo. Tuttavia, la deviazione standard del 28% indica che alcuni risultati dei test possono variare discostandosi dalla media.
Osservando il grafico, notiamo che la distribuzione presenta sia casi di profitto negativo (sulla sinistra) sia alcuni episodi di guadagni estremamente elevati (sulla destra), seppur meno frequenti.
Questa analisi mostra dei buoni risultati, al variare di alcune condizioni i risultati cambiano come vedremo nei seguenti paragrafi.
![distribution_mean_profit](https://github.com/user-attachments/assets/0147f895-e6bf-4a4b-95e6-235cc715778d)
![profit_every_test_by_agent_boxplot](https://github.com/user-attachments/assets/f9017a70-e6fa-4be5-911f-59847f269be7)

---

#### Importanza del contesto storico.
I risultati variano significativamente a seconda del contesto storico in cui si effettua il test. Anche la migliore strategia può subire pesanti perdite se applicata in un periodo sfavorevole. 
![mean_profit_every_date_initial_test](https://github.com/user-attachments/assets/4b8d0e87-b67f-469e-bbc6-b17b2d6cc710)

---

#### Selezione dei titoli e volatilità.
- Le strategie che effettuano la scelta dei titoli su cui lavorare in modo casuale (symb_rnd) spesso ottengono profitti medi più elevati, perché possono includere titoli a bassa capitalizzazione, che presentano oscillazioni di prezzo più marcate. Tra tutte, l’Agente 3 (con selezione casuale) si è rivelato quello con il miglior profitto percentuale medio, ma con più esposizione al rischio.
- Allo stesso tempo, queste scelte casuali mostrano maggiore instabilità, con oscillazioni di profitti percentuali molto ampie (deviazione standard più elevata). Questo significa che gli alti profitti sono compensati da un rischio maggiore.
- Le strategie basate su aziende grandi e più consolidate (top_avg_vol), invece, presentano profitti medi leggermente inferiori, ma offrono risultati più stabili.
- Grazie all’analisi dei titoli che registrano maggior e minor pro tti è stato confermato il trend.
	- I titoli a bassa capitalizzazione, per loro natura molto volatili, hanno garantito guadagni alti: compaiono fra i migliori, ma in alcuni casi anche tra i peggiori, poiché la volatilità ampli ca sia i rialzi sia i ribassi.
 	- Le grandi aziende, pur più stabili, presentano movimenti di prezzo meno accentuati e dunque un potenziale di guadagno inferiore in strategie di breve periodo.

#### Instabilità vs Stabilità.
- L'Agente 3 risulta il più profittevole, ma anche molto instabile.
- L’Agente 8, basato sul trailing stop loss, si distingue invece come il più stabile: presenta uttuazioni moderate e una distribuzione dei profitti meno soggetta a valori estremi. Per chi preferisce una strategia di guadagno più equilibrata, la stabilità di questo Agente può essere un vantaggio.

![mean_profit_every_agent](https://github.com/user-attachments/assets/164070ff-6011-49c9-933d-0a3dddceffaf)
![dev_std_every_agent](https://github.com/user-attachments/assets/c57c30c4-e48b-44a6-8309-ccc416caa29a)

---

#### Tempo di detenzione e Take Profit.
- Spesso un **Take Profit basso** (vendita rapida quando si raggiunge un piccolo guadagno) permette di chiudere operazioni in tempi molto brevi, ottenendo profitti medi più elevati ma con maggiore variabilità.
- Al crescere del tempo di detenzione, i pro tti tendono a calare.
Questo è legato sia a **Take Profit più alti** (che ritardano la vendita), sia al fatto che titoli meno volatili richiedono più tempo per generare movimenti di prezzo significativi.

#### Correlazione fra tempi di detenzione e rendimenti.
Il tempo di detenzione rappresenta l’intervallo, espresso in giorni, tra l’acquisto e la vendita di un titolo e varia in modo significativo in base alla strategia adottata. I guadagni più alti si concentrano spesso nei primi giorni (1–5). Con il passare del tempo, il profitto medio tende a diminuire, a conferma che puntare a rapidi aumenti di prezzo (Take Profit basso) è più redditizio, ma meno stabile.

![avg_profit_by_time_detenction](https://github.com/user-attachments/assets/584955de-7241-44c9-8c04-04011b7cace2)
![mean_profit_every_agent_take_profit_agent2_top_avg_vol](https://github.com/user-attachments/assets/4787af27-bed5-46f7-889c-4c55da47289b)
![mean_profit_every_agent_take_profit_agent2_symb_rnd](https://github.com/user-attachments/assets/21f1d47e-0773-4465-95af-f3c4b3e3b8e2)

---

#### Influenza sul numero di operazioni e tempi di detenzione.
- Gli agenti che adottano la selezione casuale (symb_rnd) spesso chiudono le posizioni più in fretta, grazie alle oscillazioni di prezzo elevate. Di conseguenza, registrano mediamente tempi di detenzione inferiori rispetto a chi sceglie titoli più stabili ma anche più lenti nei movimenti.
- Le strategie che operano su un numero maggiore di titoli o su orizzonti temporali più lunghi generano molte più transazioni, aumentando sì le occasioni di guadagno ma anche l’esposizione al rischio.
![mean_#_sales_every_agent](https://github.com/user-attachments/assets/4707e9d4-d095-41a8-bac4-b21483c939fd)
![mean_#_purchase_every_agent](https://github.com/user-attachments/assets/30180658-15a2-4eb6-b301-14dd70912c27)


---
### Sviluppi futuri.
Sono presentati i seguenti suggerimenti per i sviluppi futuri:
- **Migliorare la selezione dei titoli basata sul valore di capitalizzazione di mercato** in un determinato periodo storico.
- Introdurre **vincoli di mercato più realistici** come limiti di acquisto e di vendita oppure costi di transazione.
- Eseguire un **maggior numero di test** su periodi specifici .
- Grazie all’approccio modulare adottato nel progetto, sarà possibile per altri sviluppatori e ricercatori **definire nuove strategie di trading e testarle con maggiore fessibilità**.



---

## Licenza.


--- 

## Contatti.
Per informazioni, segnalazioni di bug o richieste di funzionalità:
- Apri una Issue su GitHub;
- Oppure contattami direttamente;

---

**Buon Trading e Buon Backtesting!**

