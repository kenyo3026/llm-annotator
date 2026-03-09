"""
Integration test: fetch feedbacks from PostgreSQL, annotate via API, write tags back.

This test hits a real database and a real LLM. It is intentionally an integration
test, not a unit test -- use pytest -m integration to run selectively.

Usage:
    # Run this test only
    pytest src/annotator/tests/test_annotation_pipeline.py -v -s

    # Or with direct execution
    python -m src.annotator.tests.test_annotation_pipeline
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import psycopg2
    _psycopg2_available = True
except ImportError:
    _psycopg2_available = False

from fastapi.testclient import TestClient
from annotator.app import create_app

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test_db"
DB_HOST = None
DB_PASS = None

MAX_RUN_CASES = 10

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_connection_params() -> dict[str, Any]:
    params: dict[str, Any] = {
        "host": os.environ.get("DB_HOST", DB_HOST),
        "port": int(os.environ.get("DB_PORT", DB_PORT)),
        "dbname": os.environ.get("DB_NAME", DB_NAME),
    }
    if os.environ.get("DB_USER"):
        params["user"] = os.environ[DB_HOST]
        params["password"] = os.environ.get("DB_PASSWORD", DB_PASS)
    return params


def _try_connect():
    """Return a psycopg2 connection, or None if unavailable."""
    if not _psycopg2_available:
        return None
    try:
        return psycopg2.connect(**_get_connection_params())
    except Exception:
        return None


def _is_db_ready(conn) -> bool:
    """Check if feedbacks table exists and is queryable."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM feedbacks LIMIT 1")
        return True
    except Exception:
        return False


def _fetch_feedbacks(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, feedback_text FROM feedbacks ORDER BY id LIMIT %s;",
            (MAX_RUN_CASES,),
        )
        return [{"id": row[0], "feedback_text": row[1]} for row in cur.fetchall()]


def _save_tags(conn, feedback_id: int, tags: list[str], model_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tags (feedback_id, tags, model_name) VALUES (%s, %s, %s);",
            (feedback_id, tags, model_name),
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db_conn():
    """Module-scoped DB connection; skip all tests if DB is unreachable or schema not ready."""
    conn = _try_connect()
    if conn is None:
        pytest.skip("PostgreSQL not available -- set DB_NAME / DB_HOST env vars")
    if not _is_db_ready(conn):
        conn.close()
        pytest.skip("DB schema not ready -- run make init-schema and make seed")
    conn.autocommit = False
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture(scope="module")
def api_client():
    """Module-scoped TestClient backed by the real FastAPI app."""
    return TestClient(create_app())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestAnnotationPipeline:
    """Integration tests: annotate feedbacks from DB and write tags back."""

    def test_api_health(self, api_client):
        """Verify the annotator API is reachable before running the pipeline."""
        response = api_client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_annotate_single_feedback(self, api_client, db_conn):
        """Smoke test: annotate the first feedback and check the response shape."""
        feedbacks = _fetch_feedbacks(db_conn)
        assert len(feedbacks) > 0, "No feedbacks found in DB"

        first = feedbacks[0]
        response = api_client.post(
            "/annotate",
            json={"context": first["feedback_text"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_run_full_pipeline(self, api_client, db_conn):
        """
        Full pipeline: annotate all feedbacks and write tags to DB.
        Rolls back after the test (db_conn fixture handles rollback).
        """
        feedbacks = _fetch_feedbacks(db_conn)
        assert len(feedbacks) > 0, "No feedbacks found in DB"

        total = len(feedbacks)
        success, failed = 0, 0
        for i, fb in enumerate(feedbacks, start=1):
            response = api_client.post(
                "/annotate",
                json={"context": fb["feedback_text"]},
            )

            if response.status_code != 200:
                logger.warning("[%d/%d] feedback_id=%d FAIL HTTP %d: %s", i, total, fb["id"], response.status_code, response.text)
                failed += 1
                continue

            tags = response.json().get("tags", [])
            _save_tags(db_conn, fb["id"], tags, model_name="default")
            logger.info("[%d/%d] feedback_id=%d OK tags=%s", i, total, fb["id"], tags)
            success += 1

        logger.info("Annotated: %d OK, %d failed out of %d feedbacks", success, failed, len(feedbacks))
        assert success > 0, "No feedbacks were successfully annotated"

    def test_persist_pipeline(self, api_client):
        """
        Persistent version: same pipeline but commits to DB.
        Run this when you want the tags to actually be saved.
        """
        conn = _try_connect()
        if conn is None:
            pytest.skip("PostgreSQL not available")
        if not _is_db_ready(conn):
            conn.close()
            pytest.skip("DB schema not ready -- run make init-schema and make seed")

        conn.autocommit = False
        try:
            feedbacks = _fetch_feedbacks(conn)
            total = len(feedbacks)
            success, failed = 0, 0

            for i, fb in enumerate(feedbacks, start=1):
                response = api_client.post(
                    "/annotate",
                    json={"context": fb["feedback_text"]},
                )

                if response.status_code != 200:
                    logger.warning("[%d/%d] feedback_id=%d FAIL HTTP %d: %s", i, total, fb["id"], response.status_code, response.text)
                    failed += 1
                    continue

                tags = response.json().get("tags", [])
                _save_tags(conn, fb["id"], tags, model_name="default")
                logger.info("[%d/%d] feedback_id=%d OK tags=%s", i, total, fb["id"], tags)
                success += 1

            conn.commit()
            logger.info("Persisted: %d OK, %d failed", success, failed)
            assert success > 0

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


if __name__ == "__main__":
    from annotator.tests.base import run_tests_with_report
    sys.exit(run_tests_with_report(__file__, "annotation_pipeline"))
