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


def weekly_counts(weeks: int = 26) -> list[dict]:
    """直近 `weeks` 週分（月曜始まり）の記録件数を古い順に返す。

    習慣的な記録を想定していないため、日単位ではなく週単位で集計する。
    週の区切りは ISO 週（月曜始まり）。
    """
    from datetime import date, timedelta

    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    start_monday = this_monday - timedelta(weeks=weeks - 1)

    counts: dict[date, int] = {}
    monday = start_monday
    while monday <= this_monday:
        counts[monday] = 0
        monday += timedelta(weeks=1)

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT date, COUNT(*) AS cnt FROM entries WHERE date >= ? GROUP BY date",
            (start_monday.isoformat(),),
        ).fetchall()

    for row in rows:
        d = date.fromisoformat(row["date"])
        monday = d - timedelta(days=d.weekday())
        if monday in counts:
            counts[monday] += row["cnt"]

    result = []
    for monday, count in sorted(counts.items()):
        week_end = monday + timedelta(days=6)
        if count == 0:
            tier = "t0"
        elif count == 1:
            tier = "t1"
        elif count == 2:
            tier = "t2"
        else:
            tier = "t3"
        result.append(
            {
                "week_start": monday.isoformat(),
                "label": f"{monday.month}/{monday.day}",
                "range": f"{monday.month}/{monday.day}〜{week_end.month}/{week_end.day}",
                "count": count,
                "tier": tier,
            }
        )
    return result
