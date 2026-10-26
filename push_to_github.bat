@echo off
setlocal enabledelayedexpansion
title Push Project to GitHub

echo ======================================================================
echo   Push ETL ARM DWH Consolidation Project to GitHub
echo   Faculty Guide: Ms. G. Hema Sri
echo ======================================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not found in PATH!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Once installed, open a new command prompt and run this script again.
    echo.
    pause
    exit /b 1
)

echo [1/4] Initializing Git repository...
if not exist ".git" (
    git init
    git branch -M main
)

echo [2/4] Staging files...
git add .

echo [3/4] Creating commit...
git commit -m "Initial commit: ETL/ELT Pipeline Optimization via ARM DWH Consolidation"

echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/etl-arm-dwh.git): "

if "%REPO_URL%"=="" (
    echo [WARNING] No repository URL provided. Commit created locally.
    pause
    exit /b 0
)

echo [4/4] Setting remote and pushing to main branch...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ======================================================================
echo   SUCCESS! Project pushed to GitHub.
echo   Next Step: Go to https://share.streamlit.io/ to deploy!
echo ======================================================================
pause
