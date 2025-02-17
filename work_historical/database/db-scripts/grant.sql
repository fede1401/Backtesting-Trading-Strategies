
-- connettersi al database dbname

\c :dbname postgres

-- user already exists
GRANT ALL PRIVILEGES ON DATABASE :dbname to :username ;


ALTER TABLE data_market_nasdaq_symbols OWNER TO :username ;
ALTER TABLE data_market_nyse_symbols OWNER TO :username ;
ALTER TABLE data_market_larg_comp_eu_symbols OWNER TO :username
ALTER TABLE purchase OWNER TO :username;
ALTER TABLE sale OWNER TO :username;
ALTER TABLE testing_data OWNER TO :username;
ALTER TABLE simulation_data OWNER TO :username;

GRANT ALL ON SCHEMA public TO :username ;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO :username ;