"""GET /api/healthz — a plain Starlette API route (pages/api/*.py).

Reports liveness plus a couple of live counts read through the pyxle-db plugin,
so it doubles as a tiny example of an API endpoint that talks to the database.
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def endpoint(request: Request) -> JSONResponse:
    payload = {"status": "ok", "service": "pulse"}
    try:
        from db import get_database

        db = get_database()
        svc = await db.fetchone("SELECT COUNT(*) AS n FROM services")
        inc = await db.fetchone("SELECT COUNT(*) AS n FROM incidents WHERE status != 'resolved'")
        payload["services"] = svc["n"] if svc else 0
        payload["active_incidents"] = inc["n"] if inc else 0
    except Exception:  # noqa: BLE001 - health must answer even if the DB is cold
        payload["db"] = "unavailable"
    return JSONResponse(payload)
