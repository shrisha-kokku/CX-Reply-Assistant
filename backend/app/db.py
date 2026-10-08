# One tiny helper for all SQL. Every query in the project goes through run().
import psycopg2
from psycopg2.extras import RealDictCursor

from app import config


def run(sql, params=(), fetch="all"):
    """Run one SQL statement.
    fetch="all"  -> list of rows (dicts)
    fetch="one"  -> one row (dict) or None
    fetch=None   -> nothing returned (insert/update/delete)
    Always use %s placeholders for params, never string formatting (prevents SQL injection).
    """
    conn = psycopg2.connect(config.DATABASE_URL)
    try:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:  # "with conn" commits
            cur.execute(sql, params)
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
    finally:
        conn.close()
