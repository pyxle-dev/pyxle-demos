"""Pulse — data layer, on the pyxle-db plugin.

The plugin (configured in ``pyxle.config.json``) opens ``data/pulse.db`` at
startup and applies ``migrations/``. This is the only module that talks to it:
pages import these async functions and never write SQL themselves. The whole
demo is seeded with realistic status-page data on first boot.

Every function is async — ``await`` them from ``@server`` loaders, ``@action``
handlers, and the WebSocket room.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from pyxle_db import get_database

# ── status vocabulary ────────────────────────────────────────────
# Ordered worst→best so we can compute an overall rollup.
STATUS_RANK = {
    "major": 4,
    "partial": 3,
    "degraded": 2,
    "maintenance": 1,
    "operational": 0,
}
STATUS_LABEL = {
    "operational": "Operational",
    "degraded": "Degraded performance",
    "partial": "Partial outage",
    "major": "Major outage",
    "maintenance": "Under maintenance",
}

_seed_lock = asyncio.Lock()


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def _d(row) -> dict:
    """pyxle-db Row → plain JSON-serializable dict (loaders return JSON)."""
    return dict(row)


# ── seed ─────────────────────────────────────────────────────────

_SERVICES = [
    ("api", "API Gateway", "us-east-1", "operational", 0),
    ("dashboard", "Dashboard", "us-east-1", "operational", 1),
    ("realtime", "Realtime · WebSockets", "eu-west-1", "degraded", 2),
    ("auth", "Authentication", "us-east-1", "operational", 3),
    ("edge", "Edge CDN", "global", "operational", 4),
    ("db", "Postgres", "us-east-1", "operational", 5),
]

# Which (service_slug, days_ago) had a rough day — everything else is 100%.
_ROUGH_DAYS = {
    ("realtime", 0): ("degraded", 99.2),
    ("realtime", 14): ("partial", 98.1),
    ("dashboard", 8): ("degraded", 99.6),
    ("db", 3): ("maintenance", 99.9),
    ("edge", 41): ("degraded", 99.4),
}


async def ensure_seeded() -> None:
    """Idempotently seed the demo. Cheap no-op once data exists."""
    db = get_database()
    existing = await db.fetchone("SELECT COUNT(*) AS n FROM services")
    if existing and existing["n"]:
        return
    async with _seed_lock:
        existing = await db.fetchone("SELECT COUNT(*) AS n FROM services")
        if existing and existing["n"]:
            return
        await _seed(db)


async def _seed(db) -> None:
    now = _now()
    # One transaction for the whole seed. Use the `tx` handle for every write —
    # db.execute / db.executemany manage their OWN transaction, so calling them
    # inside an open one would deadlock on the write lock.
    async with db.transaction() as tx:
        # services
        await tx.executemany(
            "INSERT INTO services (slug, name, region, status, sort) VALUES (?, ?, ?, ?, ?)",
            _SERVICES,
        )
        ids = {
            r["slug"]: r["id"]
            for r in await tx.fetchall("SELECT id, slug FROM services")
        }

        # 90 days of daily status per service
        daily: list[tuple] = []
        for slug, sid in ids.items():
            for ago in range(89, -1, -1):
                day = (now - timedelta(days=ago)).strftime("%Y-%m-%d")
                status, uptime = _ROUGH_DAYS.get((slug, ago), ("operational", 100.0))
                daily.append((sid, day, status, uptime))
        await tx.executemany(
            "INSERT INTO daily_status (service_id, day, status, uptime) VALUES (?, ?, ?, ?)",
            daily,
        )

        # active incident — the demo's centerpiece
        await tx.execute(
            """INSERT INTO incidents (slug, title, severity, status, service_id, summary, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "elevated-ws-reconnects",
                "Elevated WebSocket reconnects in eu-west-1",
                "major",
                "monitoring",
                ids["realtime"],
                "A subset of realtime connections in eu-west-1 are reconnecting more often than usual. Messages are delivered, but with added latency.",
                _iso(now - timedelta(hours=2, minutes=6)),
            ),
        )
        active_id = (await tx.fetchone("SELECT id FROM incidents WHERE slug = ?", ("elevated-ws-reconnects",)))["id"]
        await tx.executemany(
            "INSERT INTO incident_updates (incident_id, status, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
            [
                (active_id, "investigating", "We're investigating elevated reconnect rates on the realtime edge in eu-west-1. Connections recover automatically; you may see brief gaps in live updates.", "Priya · On-call", _iso(now - timedelta(hours=2, minutes=6))),
                (active_id, "identified", "Root cause identified: one broker node in eu-west-1 hit its connection-pool ceiling after a traffic spike. We're draining it and shifting subscribers to healthy nodes.", "Priya · On-call", _iso(now - timedelta(hours=1, minutes=18))),
                (active_id, "monitoring", "Mitigation is in place and reconnect rates are trending back to baseline. We're monitoring before calling it resolved.", "Marcus · SRE", _iso(now - timedelta(minutes=37))),
            ],
        )

        # resolved history
        await tx.execute(
            """INSERT INTO incidents (slug, title, severity, status, service_id, summary, created_at, resolved_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "postgres-failover",
                "Scheduled Postgres failover",
                "maintenance",
                "resolved",
                ids["db"],
                "Planned primary failover to apply security patches. Brief read-only window.",
                _iso(now - timedelta(days=3, hours=4)),
                _iso(now - timedelta(days=3, hours=3, minutes=12)),
            ),
        )
        pg_id = (await tx.fetchone("SELECT id FROM incidents WHERE slug = ?", ("postgres-failover",)))["id"]
        await tx.executemany(
            "INSERT INTO incident_updates (incident_id, status, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
            [
                (pg_id, "maintenance", "Beginning the scheduled failover. Writes will pause briefly while the replica is promoted.", "Pulse", _iso(now - timedelta(days=3, hours=4))),
                (pg_id, "resolved", "Failover complete; the new primary is healthy and writes have resumed. Total write-pause: 48 seconds.", "Pulse", _iso(now - timedelta(days=3, hours=3, minutes=12))),
            ],
        )

        await tx.execute(
            """INSERT INTO incidents (slug, title, severity, status, service_id, summary, created_at, resolved_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "dashboard-500s",
                "Dashboard 500s during a bad deploy",
                "minor",
                "resolved",
                ids["dashboard"],
                "A deploy shipped a regression that 500'd ~3% of dashboard loads. Rolled back.",
                _iso(now - timedelta(days=8, hours=6)),
                _iso(now - timedelta(days=8, hours=5, minutes=41)),
            ),
        )
        dash_id = (await tx.fetchone("SELECT id FROM incidents WHERE slug = ?", ("dashboard-500s",)))["id"]
        await tx.executemany(
            "INSERT INTO incident_updates (incident_id, status, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
            [
                (dash_id, "investigating", "We're seeing a spike in 500s on the dashboard following a deploy. Investigating now.", "Marcus · SRE", _iso(now - timedelta(days=8, hours=6))),
                (dash_id, "resolved", "Rolled back the offending deploy; error rate is back to zero. A guard has been added to the deploy check.", "Marcus · SRE", _iso(now - timedelta(days=8, hours=5, minutes=41))),
            ],
        )


# ── reads ────────────────────────────────────────────────────────

async def list_services() -> list[dict]:
    """Services with their current status and 90-day uptime average."""
    db = get_database()
    services = [_d(r) for r in await db.fetchall(
        "SELECT * FROM services ORDER BY sort ASC"
    )]
    bars = await db.fetchall(
        "SELECT service_id, day, status, uptime FROM daily_status ORDER BY day ASC"
    )
    by_service: dict[int, list[dict]] = {}
    for b in bars:
        by_service.setdefault(b["service_id"], []).append(_d(b))
    for svc in services:
        days = by_service.get(svc["id"], [])
        svc["days"] = days
        svc["uptime90"] = round(sum(d["uptime"] for d in days) / len(days), 3) if days else 100.0
        svc["status_label"] = STATUS_LABEL.get(svc["status"], svc["status"])
    return services


async def overall_status() -> dict:
    """The worst current service status, as the headline rollup."""
    db = get_database()
    rows = await db.fetchall("SELECT status FROM services")
    worst = "operational"
    for r in rows:
        if STATUS_RANK.get(r["status"], 0) > STATUS_RANK.get(worst, 0):
            worst = r["status"]
    active = await db.fetchone(
        "SELECT COUNT(*) AS n FROM incidents WHERE status != 'resolved'"
    )
    return {
        "status": worst,
        "label": "All systems operational" if worst == "operational" else STATUS_LABEL.get(worst, worst),
        "active_incidents": active["n"] if active else 0,
    }


async def list_incidents(*, limit: int = 20, active_only: bool = False) -> list[dict]:
    db = get_database()
    where = "WHERE i.status != 'resolved'" if active_only else ""
    rows = await db.fetchall(
        f"""SELECT i.*, s.name AS service_name, s.slug AS service_slug
            FROM incidents i LEFT JOIN services s ON s.id = i.service_id
            {where}
            ORDER BY i.created_at DESC LIMIT ?""",
        (limit,),
    )
    return [_d(r) for r in rows]


async def get_incident(slug: str) -> dict | None:
    db = get_database()
    inc = await db.fetchone(
        """SELECT i.*, s.name AS service_name, s.slug AS service_slug
           FROM incidents i LEFT JOIN services s ON s.id = i.service_id
           WHERE i.slug = ?""",
        (slug,),
    )
    if inc is None:
        return None
    inc = _d(inc)
    inc["updates"] = [_d(r) for r in await db.fetchall(
        "SELECT * FROM incident_updates WHERE incident_id = ? ORDER BY created_at DESC",
        (inc["id"],),
    )]
    return inc


# ── writes ───────────────────────────────────────────────────────

async def create_incident(title: str, severity: str, service: str, summary: str) -> str:
    """Open a new incident (from the report form) and return its slug."""
    import re

    db = get_database()
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] or "incident"
    slug = base
    n = 1
    while await db.fetchone("SELECT 1 FROM incidents WHERE slug = ?", (slug,)):
        n += 1
        slug = f"{base}-{n}"
    svc = await db.fetchone(
        "SELECT id FROM services WHERE name = ? OR slug = ?", (service, service)
    )
    service_id = svc["id"] if svc else None
    now = _now()
    async with db.transaction() as tx:
        await tx.execute(
            """INSERT INTO incidents (slug, title, severity, status, service_id, summary, created_at)
               VALUES (?, ?, ?, 'investigating', ?, ?, ?)""",
            (slug, title, severity, service_id, summary, _iso(now)),
        )
        inc = await tx.fetchone("SELECT id FROM incidents WHERE slug = ?", (slug,))
        await tx.execute(
            "INSERT INTO incident_updates (incident_id, status, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
            (inc["id"], "investigating", summary, "Pulse", _iso(now)),
        )
    return slug


async def service_names() -> list[str]:
    db = get_database()
    return [r["name"] for r in await db.fetchall("SELECT name FROM services ORDER BY sort")]


async def add_subscriber(email: str) -> bool:
    """Record a status-update subscriber. Returns True if newly added, False if
    the email was already subscribed (idempotent — no duplicate row)."""
    db = get_database()
    email = email.strip().lower()
    existing = await db.fetchone("SELECT 1 FROM subscribers WHERE email = ?", (email,))
    if existing:
        return False
    try:
        await db.execute(
            "INSERT INTO subscribers (email, created_at) VALUES (?, ?)",
            (email, _iso(_now())),
        )
    except Exception:  # noqa: BLE001 - a race on the UNIQUE index is a no-op
        return False
    return True


async def count_subscribers() -> int:
    db = get_database()
    row = await db.fetchone("SELECT COUNT(*) AS n FROM subscribers")
    return row["n"] if row else 0


async def add_update(incident_id: int, status: str, body: str, author: str) -> dict:
    """Append an update and move the incident to ``status``. Returns the row."""
    db = get_database()
    created = _now()
    async with db.transaction() as tx:
        await tx.execute(
            "INSERT INTO incident_updates (incident_id, status, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
            (incident_id, status, body, author, _iso(created)),
        )
        resolved_at = _iso(created) if status == "resolved" else None
        await tx.execute(
            "UPDATE incidents SET status = ?, resolved_at = COALESCE(?, resolved_at) WHERE id = ?",
            (status, resolved_at, incident_id),
        )
        new = await tx.fetchone(
            "SELECT * FROM incident_updates WHERE incident_id = ? ORDER BY id DESC LIMIT 1",
            (incident_id,),
        )
    return _d(new)
