@echo off
title Dis Ticaret Karar Destek Sistemi
color 0B

echo =============================================
echo   DIS TICARET KARAR DESTEK SISTEMI
echo   Lineer Cebir Donem Projesi
echo =============================================
echo.

where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [HATA] Python bulunamadi!
    pause
    exit /b 1
)

echo [1/3] Kutuphaneler yukleniyor...
py -m pip install flask pandas numpy matplotlib -q
echo [TAMAM]

echo [2/3] Uygulama baslatiliyor...
echo.
echo =============================================
echo   Sayfalar:
echo   - Ana Sayfa  : http://localhost:5001/
echo   - Veri Analizi : http://localhost:5001/analiz
echo   - Karar Destek : http://localhost:5001/karar
echo   - Sonuclar   : http://localhost:5001/sonuc
echo =============================================
echo.
start http://localhost:5001

py app.py

pause
