# TFU2 - Demo de Tácticas de Arquitectura

Este proyecto contiene una demo API en FastAPI para demostrar tácticas de arquitectura de software.

## Tácticas implementadas
Replicación: endpoint /whoami muestra qué instancia responde (api-A o api-B).  
Reintentos: endpoint /retry intenta varias veces hasta que /unstable devuelve éxito.  
Rate limiting: máximo 10 requests cada 10 segundos, luego responde HTTP 429 Too Many Requests.  
Validación de entrada: GET con body devuelve 400.

## Scripts de prueba
test_whoami.bat  prueba replicación.  
test_retry.bat  prueba reintentos.  
test_ratelimit.bat  prueba rate limiting.  
test_get_with_body_400.bat  prueba validación de GET con body.  
run_all.bat  corre todos los anteriores en orden para la demo.

## Arranque rápido (tener Docker Desktop con WSL funcionando)

# Parate en la carpeta donde está docker-compose.yaml
docker compose up -d

## Pruebas rápidas

### Windows (PowerShell)

# Replicación
curl.exe -i http://127.0.0.1:8000/whoami
curl.exe -i http://127.0.0.1:8001/whoami

# Reintentos
curl.exe -i http://127.0.0.1:8000/retry

# GET con body -> 400
curl.exe -i -X GET -H "Content-Type: application/json" --data "{\"ping\":\"pong\"}" http://127.0.0.1:8000/health

# Rate limiting (usando uno de los script)
.\test_ratelimit.bat

### Windows (CMD)

REM Replicación
curl -i http://127.0.0.1:8000/whoami
curl -i http://127.0.0.1:8001/whoami

REM Reintentos
curl -i http://127.0.0.1:8000/retry

REM GET con body -> 400
curl -i -X GET -H "Content-Type: application/json" --data "{\"ping\":\"pong\"}" http://127.0.0.1:8000/health

REM Rate limiting (incluye loop de 12 requests)
test_ratelimit.bat

### Linux / macOS (bash/zsh)
# Replicación
curl -i http://127.0.0.1:8000/whoami
curl -i http://127.0.0.1:8001/whoami

# Reintentos
curl -i http://127.0.0.1:8000/retry

# GET con body -> 400
curl -i -X GET -H "Content-Type: application/json" --data '{"ping":"pong"}' http://127.0.0.1:8000/health

# Rate limiting (12 requests)
for i in {1..12}; do curl -i http://127.0.0.1:8000/users?role=user; done

## Scripts de prueba (solo para Windows)

# PowerShell
.\test_whoami.bat
.\test_retry.bat
.\test_get_with_body_400.bat
.\test_ratelimit.bat
# Todo junto:
.\run_all.bat

REM CMD
test_whoami.bat
test_retry.bat
test_get_with_body_400.bat
test_ratelimit.bat
REM Todo junto:
run_all.bat

## Útil (windows,macOS,linux)
# Logs en vivo
docker compose logs -f api-a api-b

# Reinicio limpio
docker compose down && docker compose up -d

# Rebuild forzado
docker compose build --no-cache && docker compose up -d --force-recreate

# Apagar
docker compose down

