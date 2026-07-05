# -*- coding: utf-8 -*-
"""できたことログ — FastAPI アプリ本体（MVP）。

今の機能:
  - GET  /            今日のできたこと入力フォーム＋一覧
  - POST /entries     できたことを1件保存 → / にリダイレクト
  - GET  /api/entries 全件を JSON で返す（API を持つことの証明用）

まだ入れていない（次の段階）: LLM によるポジティブ評価、可視化（ヒートマップ等）。
"""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import db

app = FastAPI(title="できたことログ")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.get("/")
def index(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    entries = db.list_entries_by_date(today)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"today": today, "entries": entries},
    )


@app.post("/entries")
def create_entry(content: str = Form(...), category: str = Form("")):
    if content.strip():
        db.add_entry(content, category)
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/entries")
def api_entries():
    return [dict(row) for row in db.list_all_entries()]


@app.get("/calendar")
def calendar(request: Request):
    weeks = db.weekly_counts()
    return templates.TemplateResponse(
        request=request,
        name="calendar.html",
        context={"weeks": weeks},
    )
