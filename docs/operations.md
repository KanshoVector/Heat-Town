# 運用・技術（発起人用）

学生向け: [START.md](../START.md) + 各フォルダ README。

---

## 技術スタック（実装）

| レイヤ | 技術 |
|--------|------|
| 分析 | Python 3.11+, pandas, numpy |
| 前処理 | pandas + haversine（DuckDB 未使用） |
| 地図 | Leaflet 1.9 |
| フロント | HTML + 素の JS |
| ホスト | **GitHub Pages**（本番）+ Vercel（代替） |

---

## デプロイ

### GitHub Pages（本番）

- Workflow: `.github/workflows/deploy-pages.yml`
- `main` push → `pipeline --sample` → `mvp/public` 公開
- URL: https://kanshovector.github.io/Heat-Town/?demo=1

### Vercel（代替）

ルート `vercel.json` — ビルド時に `pipeline --sample`、出力 `mvp/public/`。

---

## 再現性

| パス | Git |
|------|-----|
| `data/samples/`, `processed/`, `raw/` | .gitignore |
| `mvp/public/data/` | .gitignore |

各自 `python -m heat_town.cli pipeline --sample` 必須 → [ADR-003](adr/003-generated-data-not-in-git.md)

---

## CI（任意・手動）

| ファイル | 内容 |
|----------|------|
| `python.yml` | ruff + pytest（34 tests） |
| `docs.yml` | Markdown lint |
| `ci.yml` | workflow_dispatch のみ |

Branch Protection に Status Check は設定しない。

---

## コスト

API キー不要。GitHub Pages + Vercel Hobby = $0。
