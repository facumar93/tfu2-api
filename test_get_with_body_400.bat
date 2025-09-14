@echo off
echo === Probar politica GET con body -> 400 ===
curl.exe -i -X GET -H "Content-Type: application/json" --data "{\"ping\":\"pong\"}" "http://127.0.0.1:8000/health"
echo.
pause
