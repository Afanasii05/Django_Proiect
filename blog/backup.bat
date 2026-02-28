@echo off
echo Creare backup date...

SET PG_PATH="C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

%PG_PATH% -U fanel_django -d proiect_django_db -t aplicatie_exemplu_jucarie -t aplicatie_exemplu_categorie > backup_tabele.sql
if %ERRORLEVEL% neq 0 (
    echo EROARE: Backup-ul a esuat! Verifica parola sau calea.
) else (
    echo Backup finalizat cu succes in backup_tabele.sql!
)
pause