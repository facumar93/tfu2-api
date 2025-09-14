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

## Arranque rápido
1) Levantar:
   docker compose up -d

2) Probar instancias:
   curl -i http://127.0.0.1:8000/whoami  
   curl -i http://127.0.0.1:8001/whoami  

Útil:
- Ver logs:        docker compose logs -f api-a api-b  
- Reiniciar limpio:docker compose down && docker compose up -d  
- Rebuild forzado: docker compose build --no-cache && docker compose up -d --force-recreate  
- Apagar:          docker compose down

