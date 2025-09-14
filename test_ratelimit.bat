@echo off
echo === Enviando 12 requests a /users?role=user para gatillar 429 ===
FOR /L %%I IN (1,1,12) DO (
  echo ---- Request %%I ----
  curl.exe -i -H "Connection: close" "http://127.0.0.1:8000/users?role=user"
  echo.
)
echo.
echo === Revisar cabeceras retry-after y x-ratelimit-* en la primera 429 ===
pause
