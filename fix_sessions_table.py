"""
One-off fix for the user_sessions table.

A bad alembic merge migration (c3f9a7e1d824) previously rewrote user_sessions
to a schema (device_label/revoked/string PK) meant for an unfinished, unused
session design. This drops the table and recreates it with the schema the
app actually uses (device_info/is_active/integer PK) - the same schema
a7d3f1c9b204 originally created.

Run once from the project root (same folder as backend\\), with your venv
active:

    python fix_sessions_table.py

Uses the project's own DATABASE_URL, so no psql/PATH setup needed.
"""

from sqlalchemy import text
from backend.database import engine


SQL = """
DROP TABLE IF EXISTS user_sessions;

CREATE TABLE user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    device_info VARCHAR(255),
    ip_address VARCHAR(45),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    last_active_at TIMESTAMP DEFAULT now()
);

CREATE INDEX ix_user_sessions_session_id ON user_sessions (session_id);
CREATE INDEX ix_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX ix_user_sessions_is_active ON user_sessions (is_active);
"""

if __name__ == "__main__":
    with engine.begin() as conn:
        for statement in SQL.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    print("user_sessions table fixed.")
