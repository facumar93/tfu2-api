# ============================================
# TFU2 — Demo de Tácticas (FastAPI)
#
# TÁCTICAS QUE SE DEMUESTRAN:
# - Disponibilidad: Replicación  → /whoami (dos procesos/puertos)
# - Disponibilidad: Reintentos   → /users (integrado) y /retry (harness)
# - Seguridad: Resistir ataques  → Validación global “GET con body ⇒ 400”
# ============================================

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Literal
from fastapi import HTTPException
import os, socket
import random, time  # (random no se usa en esta versión; se dejó por si sirve para variantes)

app = FastAPI()

# -------------------------
# MIDDLEWARE: Rate limiting (sin proxy)
# -------------------------
# Limita por IP (request.client.host): máx. N requests por ventana T → 429.
RATE_LIMIT_MAX_REQUESTS = 10       # límite de requests por ventana
RATE_LIMIT_WINDOW_SECONDS = 10     # duración de la ventana (segundos)

_rate_counters = {}  # dict[ip] = {"count": int, "window_start": float}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host or "unknown"
    now = time.time()
    bucket = _rate_counters.get(client_ip)

    # Crear o resetear ventana
    if not bucket or (now - bucket["window_start"]) >= RATE_LIMIT_WINDOW_SECONDS:
        _rate_counters[client_ip] = {"count": 1, "window_start": now}
        return await call_next(request)

    # Ventana vigente: verificar límite
    if bucket["count"] >= RATE_LIMIT_MAX_REQUESTS:
        retry_after = int(RATE_LIMIT_WINDOW_SECONDS - (now - bucket["window_start"]))
        headers = {
            "Retry-After": str(max(retry_after, 1)),
            "X-RateLimit-Limit": str(RATE_LIMIT_MAX_REQUESTS),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Window": str(RATE_LIMIT_WINDOW_SECONDS),
        }
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429, headers=headers)

    # Aún hay crédito
    bucket["count"] += 1
    return await call_next(request)


# -------------------------
# MIDDLEWARE (control global)
# -------------------------
@app.middleware("http")
async def reject_get_with_body(request: Request, call_next):
    """
    Seguridad (resistir ataques) — Validación global:
    Si llega un GET con body, lo rechazamos con 400.
    Esto evita usos indebidos/ataques que abusen de GET con payload.
    """
    if request.method == "GET":
        cl = request.headers.get("content-length")
        te = request.headers.get("transfer-encoding", "").lower()
        if (cl and cl != "0") or ("chunked" in te):
            return JSONResponse({"detail": "GET must not have a body"}, status_code=400)
    return await call_next(request)

# -------------------------
# Endpoint simple de salud
# -------------------------
@app.get("/health")
def health():
    """Ping básico para ver que la API responde."""
    return {"ok": True}

# --------------------------------------
# /users — Funcionalidad con reintentos
# --------------------------------------
@app.get("/users")
def list_users(
    role: Literal["admin", "user"] | None = None,
    attempts: bool = False,          # True => demo: simula 3 fallos y aplica retry; False => sin retry
    max_attempts: int = 4,           # política de reintentos (cuántos intentos como máximo)
    backoff_ms: int = 100,           # espera entre intentos (ms)
):
    """
    Disponibilidad (reintentos) integrada en una funcionalidad real:
    - Si attempts=True: simulamos 3 fallos seguidos y aplicamos la política de retry.
    - Si attempts=False: ejecuta directo, sin reintentos.
    Además, mantiene validación de negocio por 'role'.
    """

    def op(attempt: int):
        # Simulación de fallo determinista SOLO en modo demo (attempts=True)
        if attempts and attempt <= 3:
            raise HTTPException(status_code=500, detail=f"simulated failure at attempt {attempt}")

        # "Consulta de datos" (mock)
        data = [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob",   "role": "user"},
            {"id": 3, "name": "Eve",   "role": "admin"},
        ]
        if role is not None:
            data = [u for u in data if u["role"] == role]
        return {"count": len(data), "items": data}

    if attempts:
        # Aplica política de reintentos (stop-on-first-success, solo 5xx)
        result, tries = run_with_retry(op, max_attempts=max_attempts, backoff_ms=backoff_ms)
        # Devolvemos evidencia de cuántos intentos se necesitaron (solo en modo demo)
        return result | {"meta": {"attempts": tries}}
    else:
        # Modo normal: sin reintentos
        return op(1)

# --------------------------------------
# /whoami — Evidencia de replicación
# --------------------------------------
@app.get("/whoami")
def whoami(request: Request):
    """
    Disponibilidad (replicación):
    Muestra qué instancia (proceso) te atendió.
    En la demo se levantan dos procesos (p.ej., puertos 8000 y 8001),
    y este endpoint devuelve distinto instance_id/hostname/pid en cada uno.
    """
    return {
        "instance_id": os.getenv("INSTANCE_ID") or f"{socket.gethostname()}:{os.getpid()}",
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "client_ip": request.client.host,  # IP del cliente tal como Uvicorn la ve
    }

# ----------------------------------------------------------
# /retry — Harness (táctica aislada para mostrar reintentos)
# ----------------------------------------------------------
# Falla siempre en los primeros N intentos del MISMO request
FAIL_FIRST_N = 3  # ⇒ éxito recién en el intento 4

def _op(attempt: int):
    """Operación de ejemplo para el harness: falla determinísticamente las primeras N veces."""
    if attempt <= FAIL_FIRST_N:
        raise HTTPException(status_code=500, detail=f"simulated failure at attempt {attempt}")
    return {"ok": True, "attempt": attempt}

@app.get("/retry")
def retry(max_attempts: int = 4, backoff_ms: int = 100):
    """
    Disponibilidad (reintentos) en aislado:
    - Intenta ejecutar _op(attempt) y reintenta hasta max_attempts si hay 5xx.
    - Stop-on-first-success: si funciona, corta y devuelve 200.
    - Si agota intentos, responde 503 (Service Unavailable).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = _op(attempt)
            return {"attempts": attempt, "result": result}
        except HTTPException as e:
            if attempt == max_attempts:
                # Agotó reintentos → devolvemos 503 con detalle
                raise HTTPException(status_code=503, detail={"attempts": attempt, "last_error": e.detail})
            time.sleep(backoff_ms / 1000.0)

# -------------------------------------------------
# Función interna reutilizable — política de retry
# -------------------------------------------------
def run_with_retry(op, max_attempts: int = 4, backoff_ms: int = 100):
    """
    Política de reintentos (reutilizable por /users, /retry u otros):
    - Ejecuta op(attempt) reintentando SOLO errores 5xx (errores del servidor/transitorios).
    - Stop-on-first-success.
    - Si agota intentos o no es 5xx, responde 503 con detalle.
    Devuelve (resultado, intentos_realizados).
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            return op(attempts), attempts
        except HTTPException as e:
            if e.status_code < 500 or attempts >= max_attempts:
                raise HTTPException(status_code=503, detail={"attempts": attempts, "last_error": str(e.detail)})
            time.sleep(backoff_ms / 1000.0)

# ---------------------------------
# NOTAS DE USO (para la demo rápida)
# ---------------------------------
# 1) Replicación (dos procesos):
#    [SIN DOCKER]
#      uvicorn main:app --host 127.0.0.1 --port 8000
#      uvicorn main:app --host 127.0.0.1 --port 8001
#      curl.exe -i "http://127.0.0.1:8000/whoami"
#      curl.exe -i "http://127.0.0.1:8001/whoami"
#
#    [CON DOCKER - docker run]
#      docker run --rm -p 8000:8000 -e INSTANCE_ID=api-A tfu2-api:demo
#      docker run --rm -p 8001:8000 -e INSTANCE_ID=api-B tfu2-api:demo
#      curl.exe -i "http://127.0.0.1:8000/whoami"
#      curl.exe -i "http://127.0.0.1:8001/whoami"
#
#    [CON DOCKER - docker compose]
#      docker compose up -d --build
#      curl.exe -i "http://127.0.0.1:8000/whoami"
#      curl.exe -i "http://127.0.0.1:8001/whoami"
#      docker compose down
#
# 2) Reintentos integrados (en /users):
#    Normal:   curl.exe -i "http://127.0.0.1:8000/users?role=user"
#    Con demo: curl.exe -i "http://127.0.0.1:8000/users?role=user&attempts=true"
#              → meta.attempts: 4 (falló 3 y levantó en el 4º)
#    Forzar fallo tras reintentos:
#              curl.exe -i "http://127.0.0.1:8000/users?role=user&attempts=true&max_attempts=3"
#              → 503 (no llegó al intento 4)
#
# 3) Reintentos aislados (harness):
#    curl.exe -i "http://127.0.0.1:8000/retry"
#    curl.exe -i "http://127.0.0.1:8000/retry?max_attempts=3"  → 503
#
# 4) Seguridad (validación global GET con body):
#    curl.exe -i -X GET -H "Content-Type: application/json" --data "{}" "http://127.0.0.1:8000/health"
#    → 400