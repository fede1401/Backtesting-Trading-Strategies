#!/bin/bash
# Imposta il PATH per includere la directory di PostgreSQL, se necessario
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"

chmod +x create_macOS.sh

# Esegue i file SQL nell'ordine desiderato
psql -U postgres -f parameters.sql -p 5433 -v dbname='data_backtesting' -v password='fede'
psql -U postgres -f create-db-user.sql -p 5433 -v dbname='data_backtesting' -v username='reporting_user' -v password='fede'
psql -U reporting_user -d data_backtesting -f schema.sql -p 5433 -v dbname='data_backtesting' -v password='1234'
psql -U reporting_user -d data_backtesting -f grant.sql -p 5433 -v dbname='data_backtesting' -v password='1234' -v username='reporting_user'


# specificare porta se non è la classica 5432.

# avvio dello script con `./create_db.sh``