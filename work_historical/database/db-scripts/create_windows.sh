@echo off
REM Imposta il percorso della cartella bin di PostgreSQL
#set PG_BIN="C:\Program Files\PostgreSQL\13\bin"

REM Esegue i file SQL nell'ordine desiderato
%PG_BIN%\psql.exe -U postgres -f create-db-user.sql
%PG_BIN%\psql.exe -U postgres -f schema.sql
%PG_BIN%\psql.exe -U postgres -f parameters.sql
%PG_BIN%\psql.exe -U postgres -f grant.sql

pause
