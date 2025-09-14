@echo off
echo === WHOAMI api-A (8000) ===
curl.exe -i -H "Connection: close" "http://127.0.0.1:8000/whoami"
echo.
echo === WHOAMI api-B (8001) ===
curl.exe -i -H "Connection: close" "http://127.0.0.1:8001/whoami"
echo.
pause
