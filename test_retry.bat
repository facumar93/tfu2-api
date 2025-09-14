@echo off
echo === /retry (debe reintentar internamente contra /unstable) ===
curl.exe -i -H "Connection: close" "http://127.0.0.1:8000/retry"
echo.
pause
