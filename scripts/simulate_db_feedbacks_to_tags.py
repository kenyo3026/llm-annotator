#!/usr/bin/env python3
"""
Annotation pipeline simulation: fetch feedbacks from DB, annotate via API, push tags.

Uses TestClient to call the FastAPI app in-process — no live server needed.
Requires a reachable PostgreSQL instance with the feedbacks table populated.

Usage:
    # Dry-run (default, no DB writes):
    uv run python scripts/run_annotation_pipeline.py

    # Persist tags to DB:
    DB_NAME=test_db uv run python scripts/run_annotation_pipeline.py --persist

    # Custom options:
    uv run python scripts/run_annotation_pipeline.py --limit 5 --annotator open-tagging --model gemini-flash

Makefile target:
    make annotate               # dry-run against DB_NAME
    make annotate PERSIST=1     # persist mode
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Allow direct execution without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import psycopg2
    _psycopg2_available = True
except ImportError:
    _psycopg2_available = False

from fastapi.testclient import TestClient
from annotator.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

_DB_DEFAULTS: dict[str, Any] = {
    "host": "localhost",
    "port": 5432,
    "dbname": "test_db",
}


def _build_db_params() -> dict[str, Any]:
    params: dict[str, Any] = {
        "host": os.environ.get("DB_HOST", _DB_DEFAULTS["host"]),
        "port": int(os.environ.get("DB_PORT", _DB_DEFAULTS["port"])),
        "dbname": os.environ.get("DB_NAME", _DB_DEFAULTS["dbname"]),
    }
    if os.environ.get("DB_USER"):
        params["user"] = os.environ["DB_USER"]
        params["password"] = os.environ.get("DB_PASSWORD", "")
    return params


def _connect():
    """Return a psycopg2 connection, or raise SystemExit if DB is unreachable."""
    if not _psycopg2_available:
        logger.error("psycopg2 is not installed. Run: pip install psycopg2-binary")
        raise SystemExit(1)
    try:
        return psycopg2.connect(**_build_db_params())
    except Exception as exc:
        params = _build_db_params()
        logger.error(
            "Cannot connect to DB (host=%s port=%s dbname=%s): %s",
            params["host"], params["port"], params["dbname"], exc,
        )
        raise SystemExit(1)


def _fetch_feedbacks(conn, limit: int) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, feedback_text FROM feedbacks ORDER BY id LIMIT %s;",
            (limit,),
        )
        return [{"id": row[0], "feedback_text": row[1]} for row in cur.fetchall()]


def _save_tags(conn, feedback_id: int, tags: list[str], model_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tags (feedback_id, tags, model_name) VALUES (%s, %s, %s);",
            (feedback_id, tags, model_name),
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    client: TestClient,
    feedbacks: list[dict],
    conn=None,
    persist: bool = False,
    annotator: str | None = None,
    model: str | None = None,
) -> dict[str, int]:
    """
    Annotate each feedback via the in-process API and optionally persist tags.

    Returns a summary dict with keys: total, success, failed.
    """
    total = len(feedbacks)
    success, failed = 0, 0

    for i, fb in enumerate(feedbacks, start=1):
        payload: dict[str, Any] = {"context": fb["feedback_text"]}
        if annotator:
            payload["annotator"] = annotator
        if model:
            payload["model"] = model

        response = client.post("/annotate", json=payload)

        if response.status_code != 200:
            logger.warning(
                "[%d/%d] id=%s  FAIL  HTTP %d: %s",
                i, total, fb["id"], response.status_code, response.text,
            )
            failed += 1
            continue

        tags = response.json().get("tags", [])
        logger.info("[%d/%d] id=%s  OK    tags=%s", i, total, fb["id"], tags)

        if persist and conn is not None:
            _save_tags(conn, fb["id"], tags, model_name=model or "default")

        success += 1

    return {"total": total, "success": success, "failed": failed}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Annotation pipeline: fetch feedbacks → annotate via API → push tags.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--limit", type=int, default=10,
        help="Max number of feedbacks to process (default: 10)",
    )
    parser.add_argument(
        "--persist", action="store_true",
        help="Write tags to DB and commit. Default is dry-run (no writes).",
    )
    parser.add_argument("--annotator", default=None, help="Annotator name (default: first in config)")
    parser.add_argument("--model", default=None, help="Model name (default: first in config)")
    args = parser.parse_args()

    # --- Boot API in-process via TestClient ---
    logger.info("Booting annotator API (in-process)...")
    client = TestClient(create_app())

    health = client.get("/")
    if health.status_code != 200 or health.json().get("status") != "healthy":
        logger.error("API health check failed: %s", health.text)
        return 1
    logger.info("API healthy  version=%s", health.json().get("version"))

    # --- Connect to DB ---
    conn = _connect()
    conn.autocommit = False
    feedbacks = _fetch_feedbacks(conn, args.limit)
    logger.info("DB (%s) — %d feedback(s) to process", _build_db_params()["dbname"], len(feedbacks))

    # --- Run pipeline ---
    mode = "PERSIST" if args.persist else "DRY-RUN"
    logger.info(
        "Mode: %s | annotator=%s | model=%s",
        mode, args.annotator or "default", args.model or "default",
    )

    try:
        stats = run_pipeline(
            client=client,
            feedbacks=feedbacks,
            conn=conn,
            persist=args.persist,
            annotator=args.annotator,
            model=args.model,
        )
        if args.persist and conn:
            conn.commit()
            logger.info("Tags committed to DB.")
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Pipeline failed; rolled back.")
        return 1
    finally:
        if conn:
            conn.close()

    logger.info(
        "Done — %d/%d succeeded, %d failed.",
        stats["success"], stats["total"], stats["failed"],
    )
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
