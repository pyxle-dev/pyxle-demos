"""Flux demo — SQLite data layer.

Auto-seeds with realistic SaaS metrics on first run.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

_DB_PATH: Path = Path(__file__).resolve().parent / "data" / "flux.db"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def _connect(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = db_path or _DB_PATH
    _ensure_dir(path)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Schema ──────────────────────────────────────────────────────

def _init_tables() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT NOT NULL,
                email        TEXT NOT NULL UNIQUE COLLATE NOCASE,
                company      TEXT NOT NULL,
                plan         TEXT NOT NULL DEFAULT 'free',
                mrr          INTEGER NOT NULL DEFAULT 0,
                status       TEXT NOT NULL DEFAULT 'trial',
                avatar_color TEXT NOT NULL DEFAULT '#6366f1',
                joined_at    TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monthly_metrics (
                month       TEXT PRIMARY KEY,
                mrr         INTEGER NOT NULL,
                customers   INTEGER NOT NULL,
                new_signups INTEGER NOT NULL,
                churned     INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                event_type  TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)


# ── Seed Data ───────────────────────────────────────────────────

_SEED_CUSTOMERS = [
    # (name, email, company, plan, mrr_cents, status, color, joined_at)
    ("Sarah Chen", "sarah@acmecorp.com", "Acme Corp", "enterprise", 499900, "active", "#6366f1", "2025-06-12"),
    ("James Wilson", "james@techstart.io", "TechStart Inc", "pro", 7900, "active", "#22c55e", "2025-07-03"),
    ("Maria Garcia", "maria@designhub.co", "DesignHub", "business", 19900, "active", "#f59e0b", "2025-05-21"),
    ("David Kim", "david@cloudnine.dev", "CloudNine", "enterprise", 249900, "active", "#ef4444", "2025-08-15"),
    ("Aisha Patel", "aisha@dataflow.ai", "DataFlow AI", "enterprise", 499900, "active", "#8b5cf6", "2025-06-01"),
    ("Michael O'Brien", "michael@pixelperfect.design", "PixelPerfect", "business", 29900, "active", "#06b6d4", "2025-09-10"),
    ("Yuki Tanaka", "yuki@codecraft.jp", "CodeCraft", "pro", 7900, "active", "#ec4899", "2025-10-22"),
    ("Carlos Rodriguez", "carlos@nebula.systems", "Nebula Systems", "enterprise", 799900, "active", "#14b8a6", "2025-05-08"),
    ("Emma Thompson", "emma@brightpath.co", "BrightPath", "business", 19900, "active", "#f97316", "2025-11-14"),
    ("Raj Mehta", "raj@quantumlabs.in", "Quantum Labs", "enterprise", 349900, "active", "#a855f7", "2025-07-29"),
    ("Sofia Andersson", "sofia@swiftserve.se", "SwiftServe", "business", 29900, "active", "#0ea5e9", "2025-08-06"),
    ("Marcus Johnson", "marcus@metawave.io", "MetaWave", "pro", 7900, "active", "#84cc16", "2025-12-01"),
    ("Lisa Wang", "lisa@alphapoint.com", "AlphaPoint", "enterprise", 499900, "active", "#e11d48", "2025-09-18"),
    ("Omar Hassan", "omar@novatech.ae", "NovaTech", "business", 19900, "active", "#7c3aed", "2025-10-05"),
    ("Priya Sharma", "priya@skybridge.in", "SkyBridge", "pro", 7900, "active", "#059669", "2025-11-20"),
    ("Alex Novak", "alex@corelogic.cz", "CoreLogic", "business", 29900, "active", "#dc2626", "2025-12-15"),
    ("Isabella Costa", "isabella@freshstack.br", "FreshStack", "pro", 7900, "active", "#2563eb", "2026-01-08"),
    ("Thomas Fischer", "thomas@blueshift.de", "BlueShift", "enterprise", 249900, "active", "#ca8a04", "2025-06-25"),
    ("Mei Lin", "mei@prismio.cn", "PrismIO", "business", 19900, "active", "#9333ea", "2026-01-22"),
    ("Benjamin Okafor", "benjamin@zenithai.ng", "ZenithAI", "enterprise", 799900, "active", "#0d9488", "2025-07-14"),
    ("Anna Kowalski", "anna@elevate.co", "Elevate Co", "pro", 7900, "active", "#e879f9", "2026-02-05"),
    ("Ryan Chang", "ryan@peakops.dev", "PeakOps", "business", 29900, "active", "#f43f5e", "2025-08-30"),
    ("Fatima Al-Rashid", "fatima@nexusdigital.sa", "Nexus Digital", "enterprise", 349900, "active", "#4f46e5", "2025-09-12"),
    ("Jack Murphy", "jack@arclight.ie", "ArcLight", "pro", 7900, "active", "#16a34a", "2026-02-18"),
    ("Leila Nazari", "leila@velocity.ir", "VeloCity", "business", 19900, "active", "#db2777", "2026-03-01"),
    ("Daniel Park", "daniel@ironclad.kr", "IronClad", "pro", 7900, "active", "#2dd4bf", "2026-03-10"),
    ("Camille Dubois", "camille@sunforge.fr", "SunForge", "business", 29900, "active", "#fb923c", "2025-10-28"),
    ("Nathan Brooks", "nathan@waveform.au", "WaveForm", "enterprise", 249900, "active", "#818cf8", "2026-03-22"),
    # Churned customers
    ("Zara Ahmed", "zara@clearview.pk", "ClearView", "pro", 0, "churned", "#94a3b8", "2025-06-15"),
    ("Vincent Moreau", "vincent@pulsetech.fr", "PulseTech", "business", 0, "churned", "#94a3b8", "2025-08-01"),
    ("Hannah Lee", "hannah@edgecraft.nz", "EdgeCraft", "pro", 0, "churned", "#94a3b8", "2025-09-20"),
    ("Stefan Mueller", "stefan@embersys.de", "Ember Systems", "enterprise", 0, "churned", "#94a3b8", "2025-07-10"),
    # Trial customers
    ("Nadia Volkov", "nadia@oceanbyte.ru", "OceanByte", "free", 0, "trial", "#a78bfa", "2026-04-02"),
    ("Lucas Santos", "lucas@stratocloud.br", "StratoCloud", "free", 0, "trial", "#34d399", "2026-04-05"),
    ("Emily Foster", "emily@mindbridge.us", "MindBridge", "free", 0, "trial", "#fbbf24", "2026-04-08"),
    ("Wei Zhang", "wei@crestline.cn", "CrestLine", "free", 0, "trial", "#f87171", "2026-04-10"),
]

_SEED_METRICS = [
    # (month, mrr_cents, customers, new_signups, churned)
    ("2025-05", 2180000, 112, 15, 3),
    ("2025-06", 2520000, 119, 12, 5),
    ("2025-07", 2810000, 125, 11, 5),
    ("2025-08", 3050000, 131, 14, 8),
    ("2025-09", 3290000, 136, 10, 5),
    ("2025-10", 3510000, 143, 13, 6),
    ("2025-11", 3740000, 148, 12, 7),
    ("2025-12", 3920000, 152, 9, 5),
    ("2026-01", 4180000, 159, 14, 7),
    ("2026-02", 4390000, 165, 12, 6),
    ("2026-03", 4610000, 176, 18, 7),
    ("2026-04", 4875000, 184, 16, 8),
]

_SEED_ACTIVITY = [
    # (customer_name_ref, event_type, description, created_at)
    ("Nadia Volkov", "signup", "Started free trial", "2026-04-02T10:30:00"),
    ("Lucas Santos", "signup", "Started free trial", "2026-04-05T14:15:00"),
    ("Nathan Brooks", "signup", "Signed up for Enterprise plan", "2026-03-22T09:00:00"),
    ("Daniel Park", "signup", "Signed up for Pro plan", "2026-03-10T11:45:00"),
    ("Emily Foster", "signup", "Started free trial", "2026-04-08T16:20:00"),
    ("Wei Zhang", "signup", "Started free trial", "2026-04-10T08:30:00"),
    ("Leila Nazari", "upgrade", "Upgraded from Pro to Business", "2026-03-15T13:00:00"),
    ("Anna Kowalski", "payment", "Monthly payment received ($79)", "2026-04-01T00:00:00"),
    ("Carlos Rodriguez", "payment", "Monthly payment received ($7,999)", "2026-04-01T00:00:00"),
    ("Sarah Chen", "payment", "Monthly payment received ($4,999)", "2026-04-01T00:00:00"),
    ("Vincent Moreau", "churn", "Cancelled Business plan", "2026-03-28T17:00:00"),
    ("Jack Murphy", "upgrade", "Upgraded from Free to Pro", "2026-02-18T10:00:00"),
    ("Aisha Patel", "payment", "Annual renewal ($59,988)", "2026-03-01T00:00:00"),
    ("Sofia Andersson", "upgrade", "Upgraded from Pro to Business", "2026-02-20T14:30:00"),
    ("Ryan Chang", "payment", "Monthly payment received ($299)", "2026-04-01T00:00:00"),
]


def _seed_data() -> None:
    with _connect() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if existing > 0:
            return

        for name, email, company, plan, mrr, status, color, joined in _SEED_CUSTOMERS:
            conn.execute(
                "INSERT INTO customers (name, email, company, plan, mrr, status, avatar_color, joined_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, email, company, plan, mrr, status, color, joined),
            )

        for month, mrr, customers, signups, churned in _SEED_METRICS:
            conn.execute(
                "INSERT INTO monthly_metrics (month, mrr, customers, new_signups, churned) "
                "VALUES (?, ?, ?, ?, ?)",
                (month, mrr, customers, signups, churned),
            )

        # Resolve customer IDs for activity
        name_to_id = {}
        for row in conn.execute("SELECT id, name FROM customers"):
            name_to_id[row["name"]] = row["id"]

        for cust_name, event_type, desc, created in _SEED_ACTIVITY:
            cust_id = name_to_id.get(cust_name)
            conn.execute(
                "INSERT INTO activity (customer_id, event_type, description, created_at) "
                "VALUES (?, ?, ?, ?)",
                (cust_id, event_type, desc, created),
            )

        # Default settings
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('company_name', 'Flux Inc')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('notify_signups', 'true')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('notify_churn', 'true')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('notify_payments', 'false')")


# ── Public API ──────────────────────────────────────────────────


def get_dashboard_metrics() -> dict:
    """Aggregate KPIs from customer and metrics data."""
    with _connect() as conn:
        current = conn.execute(
            "SELECT * FROM monthly_metrics ORDER BY month DESC LIMIT 1"
        ).fetchone()
        previous = conn.execute(
            "SELECT * FROM monthly_metrics ORDER BY month DESC LIMIT 1 OFFSET 1"
        ).fetchone()

    if not current:
        return {"mrr": 0, "customers": 0, "new_signups": 0, "churn_rate": 0,
                "mrr_change": 0, "customers_change": 0, "signups_change": 0, "churn_change": 0}

    churn_rate = round((current["churned"] / current["customers"]) * 100, 1) if current["customers"] else 0
    prev_churn = round((previous["churned"] / previous["customers"]) * 100, 1) if previous and previous["customers"] else 0

    mrr_change = round(((current["mrr"] - previous["mrr"]) / previous["mrr"]) * 100, 1) if previous and previous["mrr"] else 0
    cust_change = current["customers"] - previous["customers"] if previous else 0

    return {
        "mrr": current["mrr"],
        "customers": current["customers"],
        "new_signups": current["new_signups"],
        "churn_rate": churn_rate,
        "mrr_change": mrr_change,
        "customers_change": cust_change,
        "signups_change": current["new_signups"] - previous["new_signups"] if previous else 0,
        "churn_change": round(churn_rate - prev_churn, 1),
    }


def get_monthly_mrr() -> list[dict]:
    """Return last 12 months of MRR data for charting."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT month, mrr, customers, new_signups, churned "
            "FROM monthly_metrics ORDER BY month ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_recent_activity(*, limit: int = 10) -> list[dict]:
    """Return recent activity with customer names."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT a.id, a.event_type, a.description, a.created_at, "
            "c.name AS customer_name, c.avatar_color "
            "FROM activity a LEFT JOIN customers c ON a.customer_id = c.id "
            "ORDER BY a.created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_customers(*, search: str = "", status: str = "") -> list[dict]:
    """Return customers, optionally filtered."""
    query = "SELECT * FROM customers WHERE 1=1"
    params: list = []
    if search:
        query += " AND (name LIKE ? OR email LIKE ? OR company LIKE ?)"
        pat = f"%{search}%"
        params.extend([pat, pat, pat])
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY mrr DESC, name ASC"

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_customer(customer_id: int) -> dict | None:
    """Return a single customer by ID."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    return dict(row) if row else None


def get_customer_activity(customer_id: int) -> list[dict]:
    """Return activity for a specific customer."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM activity WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def update_customer_plan(customer_id: int, plan: str, mrr: int) -> bool:
    """Update a customer's plan and MRR."""
    with _connect() as conn:
        conn.execute(
            "UPDATE customers SET plan = ?, mrr = ?, status = 'active' WHERE id = ?",
            (plan, mrr, customer_id),
        )
        # Log activity
        conn.execute(
            "INSERT INTO activity (customer_id, event_type, description, created_at) "
            "VALUES (?, 'upgrade', ?, ?)",
            (customer_id, f"Changed to {plan.title()} plan",
             datetime.now(tz=timezone.utc).isoformat()),
        )
    return True


def get_settings() -> dict[str, str]:
    """Return all settings as a dict."""
    with _connect() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


def update_setting(key: str, value: str) -> None:
    """Upsert a setting."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


def get_company_name() -> str:
    """Helper to get company name setting."""
    settings = get_settings()
    return settings.get("company_name", "Flux Inc")

# Initialize on import
_init_tables()
_seed_data()
