
-- database already exists

\c :dbname 


-- ==========================================
-- 1. Tabelle dati di mercato
-- ==========================================

CREATE TABLE IF NOT EXISTS data_market_nasdaq_symbols (
    symbol          VARCHAR(50)         NOT NULL,
    time_frame      VARCHAR(10)         NOT NULL,
    time_value      TIMESTAMP           NOT NULL,  -- es: 'YYYY-MM-DD hh:mm:ss'
    open_price      DOUBLE PRECISION,
    high_price      DOUBLE PRECISION,
    low_price       DOUBLE PRECISION,
    close_price     DOUBLE PRECISION,
    PRIMARY KEY (symbol, time_value, time_frame)
);

CREATE TABLE IF NOT EXISTS data_market_nyse_symbols (
    symbol          VARCHAR(50)         NOT NULL,
    time_frame      VARCHAR(10)         NOT NULL,
    time_value      TIMESTAMP           NOT NULL,
    open_price      DOUBLE PRECISION,
    high_price      DOUBLE PRECISION,
    low_price       DOUBLE PRECISION,
    close_price     DOUBLE PRECISION,
    PRIMARY KEY (symbol, time_value, time_frame)
);

CREATE TABLE IF NOT EXISTS data_market_larg_comp_eu_symbols (
    symbol          VARCHAR(50)         NOT NULL,
    time_frame      VARCHAR(10)         NOT NULL,
    time_value      TIMESTAMP           NOT NULL,
    open_price      DOUBLE PRECISION,
    high_price      DOUBLE PRECISION,
    low_price       DOUBLE PRECISION,
    close_price     DOUBLE PRECISION,
    PRIMARY KEY (symbol, time_value, time_frame)
);


-- ==========================================
-- 2. Tabelle per acquisti e vendite
-- ==========================================

CREATE TABLE IF NOT EXISTS purchase (
    purchase_date   TIMESTAMP           NOT NULL,
    created_at      TIMESTAMP           NOT NULL,
    ticket          VARCHAR(100)        NOT NULL,
    symbol          VARCHAR(10)         NOT NULL,
    volume          DOUBLE PRECISION    NOT NULL,
    price           DOUBLE PRECISION    NOT NULL,
    PRIMARY KEY (purchase_date, created_at, symbol)
);

CREATE TABLE IF NOT EXISTS sale (
    sale_date       TIMESTAMP           NOT NULL,
    purchase_date   TIMESTAMP           NOT NULL,
    created_at      TIMESTAMP           NOT NULL,
    ticket_purchase VARCHAR(100)        NOT NULL,
    ticket_sale     VARCHAR(100)        NOT NULL,
    symbol          VARCHAR(10)         NOT NULL,
    price_sale      DOUBLE PRECISION    NOT NULL,
    price_purchase  DOUBLE PRECISION    NOT NULL,
    volume          DOUBLE PRECISION    NOT NULL,
    profit_usd      DOUBLE PRECISION    NOT NULL,
    profit_perc     DOUBLE PRECISION    NOT NULL,
    PRIMARY KEY (sale_date, created_at, symbol)
);

-- (Opzionale) Se c'è una relazione diretta con purchase, si può aggiungere una foreign key. Esempio:
-- ALTER TABLE sale
--     ADD CONSTRAINT fk_purchase
--     FOREIGN KEY (purchase_date, symbol)
--     REFERENCES purchase (purchase_date, symbol);


-- ==========================================
-- 3. Tipi enumerati
-- ==========================================

CREATE TYPE state_agent AS ENUM (
    'INITIAL',
    'PURCHASE',
    'SALE',
    'WAIT',
    'SALE_IMMEDIATE'
);

-- ==========================================
-- 4. Tabelle di testing / simulazione
-- ==========================================

CREATE TABLE IF NOT EXISTS testing_data (
    id                      INTEGER           NOT NULL,
    agent                   VARCHAR(50)       NOT NULL,
    number_test             INTEGER,
    market                  VARCHAR(30)       NOT NULL,
    initial_date            TIMESTAMP         NOT NULL,
    end_date                TIMESTAMP         NOT NULL,
    initial_budget_usd      DOUBLE PRECISION  NOT NULL,
    budget_with_profit_usd  DOUBLE PRECISION,
    profit_perc             DOUBLE PRECISION,
    n_purchase              INTEGER           NOT NULL,
    n_sale                  INTEGER           NOT NULL,
    avg_sale_time_seconds   DOUBLE PRECISION  NOT NULL,
    avg_sale_time_days      DOUBLE PRECISION  NOT NULL,
    best_profit_symbol      VARCHAR(20)       NOT NULL,
    worst_profit_symbol     VARCHAR(20)       NOT NULL,
    notes                   VARCHAR(1000),
    PRIMARY KEY (id, agent, number_test)
);

CREATE TABLE IF NOT EXISTS simulation_data (
    test_id                         INTEGER           NOT NULL,
    agent                           VARCHAR(50)       NOT NULL,
    mean_perc_profit                DOUBLE PRECISION  NOT NULL,
    std_dev                         DOUBLE PRECISION  NOT NULL,
    variance                        DOUBLE PRECISION  NOT NULL,
    initial_budget                  DOUBLE PRECISION  NOT NULL,
    mean_budget_with_profit_usd     DOUBLE PRECISION  NOT NULL,
    avg_sale                        DOUBLE PRECISION  NOT NULL,
    avg_purchase                    DOUBLE PRECISION  NOT NULL,
    avg_time_sale                   DOUBLE PRECISION  NOT NULL,
    best_symbol                     VARCHAR(20)       NOT NULL,
    worst_symbol                    VARCHAR(20)       NOT NULL,
    timestamp_in                    TIMESTAMP         NOT NULL,
    timestamp_fin                   TIMESTAMP         NOT NULL,
    notes                           VARCHAR(1000),
    -- Esempio di foreign key se vuoi legare simulation_data a testing:
    -- FOREIGN KEY (test_id) REFERENCES testing (id)
    PRIMARY KEY (test_id, timestamp_in)
);