@echo off
chcp 65001 >nul
title UADB Study Hub - Test local
color 0A

echo ============================================
echo    UADB Study Hub - Lancement en local
echo ============================================
echo.

REM --- Verifie que Python est installe ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas reconnu.
    echo Telecharge-le sur https://www.python.org/downloads/
    echo Important : coche "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte.
echo.

REM --- Se place dans le dossier ou se trouve ce fichier .bat ---
cd /d "%~dp0"

REM --- Cree un environnement virtuel s'il n'existe pas deja ---
if not exist "venv\" (
    echo Premiere installation : creation de l'environnement...
    python -m venv venv
)

REM --- Active l'environnement virtuel ---
call venv\Scripts\activate.bat

REM --- Installe/met a jour les dependances ---
echo Installation des dependances (peut prendre 1-2 minutes la 1ere fois)...
pip install -r requirements.txt --quiet
echo.

REM --- Variable de connexion a la base Supabase ---
REM Remplace la ligne ci-dessous par TA vraie adresse Supabase (Session pooler),
REM la meme que celle configuree sur Render.
if not defined DATABASE_URL (
    set DATABASE_URL=REMPLACE_PAR_TON_LIEN_SUPABASE_SESSION_POOLER
)

if "%DATABASE_URL%"=="REMPLACE_PAR_TON_LIEN_SUPABASE_SESSION_POOLER" (
    echo [ATTENTION] Tu dois d'abord modifier ce fichier .bat :
    echo Ouvre-le avec le Bloc-notes, remplace REMPLACE_PAR_TON_LIEN_SUPABASE_SESSION_POOLER
    echo par ta vraie adresse Supabase ^(Session pooler^), la meme que sur Render.
    echo.
    pause
    exit /b 1
)

echo ============================================
echo Le site va demarrer.
echo Ouvre ton navigateur sur : http://localhost:5000
echo.
echo ATTENTION : ce test utilise la MEME base de donnees que le site en
echo ligne ^(Supabase^). Les ajouts/suppressions que tu fais ici sont reels.
echo.
echo Pour arreter le site : ferme cette fenetre ou fais Ctrl+C
echo ============================================
echo.

python app.py

pause
