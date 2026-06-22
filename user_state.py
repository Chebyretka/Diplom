import sqlite3
import json
import logging
from datetime import datetime

DB_PATH = "bot_data.db"
log = logging.getLogger(__name__)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id     INTEGER PRIMARY KEY,
                state_json  TEXT    NOT NULL DEFAULT '{}',
                updated_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                first_name  TEXT,
                created_at  TEXT    NOT NULL,
                last_seen   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS search_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                destination  TEXT,
                days         TEXT,
                budget       TEXT,
                stars        TEXT,
                children     TEXT,
                results_count INTEGER,
                searched_at  TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
    log.info("База данных инициализирована: %s", DB_PATH)


class UserStateManager:
    """
    Хранит состояние диалога каждого пользователя в SQLite.
    Таблицы создаются автоматически при первом запуске.
    """

    #  Состояние диалога 

    def get(self, user_id: int) -> dict | None:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT state_json FROM user_states WHERE user_id = ?",
                (user_id,)
            ).fetchone()
        if row is None:
            return None
        state = json.loads(row["state_json"])
        return state if state else None

    def set(self, user_id: int, state: dict):
        now = datetime.utcnow().isoformat()
        with _get_conn() as conn:
            conn.execute("""
                INSERT INTO user_states (user_id, state_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
            """, (user_id, json.dumps(state, ensure_ascii=False), now))

    def reset(self, user_id: int):
        with _get_conn() as conn:
            conn.execute(
                "DELETE FROM user_states WHERE user_id = ?",
                (user_id,)
            )

    #  Пользователи 

    def upsert_user(self, user_id: int, first_name: str):
        """Сохраняет/обновляет имя пользователя и время последнего визита."""
        now = datetime.utcnow().isoformat()
        with _get_conn() as conn:
            conn.execute("""
                INSERT INTO users (user_id, first_name, created_at, last_seen)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name = excluded.first_name,
                    last_seen  = excluded.last_seen
            """, (user_id, first_name, now, now))

    def get_user_name(self, user_id: int) -> str | None:
        """Возвращает имя из БД (кэш, чтобы не дёргать VK API лишний раз)."""
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT first_name FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
        return row["first_name"] if row else None

    #  История поисков 

    def save_search(self, user_id: int, params: dict, results_count: int):
        """Записывает параметры подбора тура и количество найденных вариантов."""
        now = datetime.utcnow().isoformat()
        with _get_conn() as conn:
            conn.execute("""
                INSERT INTO search_history
                    (user_id, destination, days, budget, stars, children, results_count, searched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                params.get("destination"),
                params.get("days"),
                params.get("budget"),
                params.get("stars"),
                params.get("children"),
                results_count,
                now,
            ))
        log.info("Поиск сохранён: user=%s dest=%s results=%d",
                 user_id, params.get("destination"), results_count)
