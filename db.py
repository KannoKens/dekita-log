# -*- coding: utf-8 -*-
"""できたことログの永続化層（SQLite）。

最小構成のため標準ライブラリの sqlite3 を直接使う。
日本語を扱うため、文字列は全て UTF-8 前提で扱う（sqlite3 は Python3 では
str をそのまま Unicode として保存するので明示のエンコード指定は不要だが、
外部ファイル入出力を足すときは encoding='utf-8' を必ず付けること）。
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "dekita.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """テーブルがなければ作る。起動時に呼ぶ。"""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT    NOT NULL,
                category   TEXT,
                created_at TEXT    NOT NULL,  -- ISO8601（並び替え用）
                date       TEXT    NOT NULL   -- YYYY-MM-DD（日単位の集計用）
            )
            """
        )


def add_entry(content: str, category: str | None = None) -> None:
    now = datetime.now()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO entries (content, category, created_at, date) VALUES (?, ?, ?, ?)",
            (content.strip(), (category or "").strip() or None,
             now.isoformat(timespec="seconds"), now.strftime("%Y-%m-%d")),
        )


def list_entries_by_date(date: str) -> list[sqlite3.Row]:
    """指定日（YYYY-MM-DD）のできたことを新しい順に返す。"""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM entries WHERE date = ? ORDER BY created_at DESC",
            (date,),
        ).fetchall()


def list_all_entries() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM entries ORDER BY created_at DESC"
        ).fetchall()
