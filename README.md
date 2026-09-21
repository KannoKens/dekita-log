# できたことログ

一日の「できたこと」を気軽に記録し、AIがポジティブに受け止め、積み上がりを可視化する Web アプリ。

## なぜ作ったか

一日の終わりに「できたこと」をノートに書き出す習慣を試したが、
**書くのを忘れる・書いても手応えがない**という理由で続かなかった。
「なぜ続かないのか」を先に考え、次の3点で解決することを目指している。

1. **入力を軽く** — 一行でさっと記録できる
2. **すぐ手応え** — AI が短くポジティブに受け止める
3. **積み上がりの可視化** — できた日をカレンダーで見える化する

## 技術構成

| 層 | 使用技術 |
|---|---|
| バックエンド | Python / FastAPI |
| DB | SQLite |
| フロント | Jinja2 テンプレート + 素の HTML/CSS |
| AI | Claude API（claude-opus-4-8 / できたことのポジティブ評価・週次サマリ） |

## 開発状況

- [x] できたことを入力して保存・当日分を一覧表示（MVP）
- [x] JSON API（`GET /api/entries`）
- [x] カレンダーヒートマップによる可視化（週2回以上を基準にした週単位の色分け、`GET /calendar`）
- [x] AI によるポジティブなフィードバック（記録時に Claude が短く受け止め、一覧に表示）
- [x] 週次サマリ（`GET /summary`、週単位でキャッシュ・`?regenerate=1` で作り直し）

## 動かし方

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" jinja2 anthropic
export ANTHROPIC_API_KEY=sk-ant-...   # AI 機能に必要（無くても記録・閲覧は動く）
uvicorn main:app --reload
```

ブラウザで http://127.0.0.1:8000 を開く。

AI フィードバックは記録の保存時に同期生成されるため、保存に数秒かかることがある。
`ANTHROPIC_API_KEY` が未設定・API エラーの場合はフィードバック無しで保存だけ行われる。
