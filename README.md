# TFU2 - Demo de Tácticas de Arquitectura

Este proyecto contiene una demo API en FastAPI para demostrar tácticas de arquitectura de software.

## Tácticas implementadas
- **Replicación**: endpoint `/whoami` muestra qué instancia responde (api-A o api-B).  
- **Reintentos**: endpoint `/retry` (o `/users?attempts=true`) simula fallos y aplica reintentos hasta devolver éxito.  
- **Rate limiting**: máximo 10 requests cada 10 segundos, luego responde HTTP 429 Too Many Requests.  
- **Validación de entrada**: un GET con body devuelve 400.

## Arranque rápido
(Tener Docker Desktop con WSL funcionando)

Parate en la carpeta donde está `docker-compose.yaml` y ejecutá:

```bash
docker compose up -d
```

## Pruebas rápidas

### Windows (PowerShell)

```powershell
# Replicación
curl.exe -i http://127.0.0.1:8000/whoami
curl.exe -i http://127.0.0.1:8001/whoami

# Reintentos
curl.exe -i http://127.0.0.1:8000/retry

# GET con body -> 400
curl.exe -i -X GET -H "Content-Type: application/json" --data '{"ping":"pong"}' "http://127.0.0.1:8000/health"

# Rate limiting
# Ejecutá este GET varias veces seguidas (más de 10 en menos de 10 s) y recibirás 429 Too Many Requests
curl.exe -i http://127.0.0.1:8000/users?role=user
```

### Windows (CMD)

```cmd
:: Replicación
curl -i http://127.0.0.1:8000/whoami
curl -i http://127.0.0.1:8001/whoami

:: Reintentos
curl -i http://127.0.0.1:8000/retry

:: GET con body -> 400
curl -i -X GET -H "Content-Type: application/json" --data "{\"ping\":\"pong\"}" http://127.0.0.1:8000/health

:: Rate limiting
:: Ejecutá este GET varias veces seguidas (más de 10 en menos de 10 s) y recibirás 429 Too Many Requests
curl -i http://127.0.0.1:8000/users?role=user
```

### Linux / macOS (bash/zsh)

```bash
# Replicación
curl -i http://127.0.0.1:8000/whoami
curl -i http://127.0.0.1:8001/whoami

# Reintentos
curl -i http://127.0.0.1:8000/retry

# GET con body -> 400
curl -i -X GET -H "Content-Type: application/json" --data '{"ping":"pong"}' http://127.0.0.1:8000/health

# Rate limiting
# Ejecutá este GET varias veces (más de 10 en menos de 10 s) para gatillar 429 Too Many Requests
curl -i http://127.0.0.1:8000/users?role=user
```

## Scripts de prueba (solo Windows)

### PowerShell

```powershell
.	est_whoami.bat
.	est_retry.bat
.	est_get_with_body_400.bat
.	est_ratelimit.bat
# Todo junto:
.
un_all.bat
```

### CMD

```cmd
test_whoami.bat
test_retry.bat
test_get_with_body_400.bat
test_ratelimit.bat
:: Todo junto:
run_all.bat
```

## Comandos útiles (Windows / macOS / Linux)

```bash
# Logs en vivo
docker compose logs -f api-a api-b

# Reinicio limpio
docker compose down && docker compose up -d

# Rebuild forzado
docker compose build --no-cache && docker compose up -d --force-recreate

# Apagar
docker compose down
```
