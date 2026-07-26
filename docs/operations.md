# 運用・技術（発起人用）

学生向け手順は各フォルダ README + [START.md](../START.md)。本ファイルは発起人・教員向け。

---

## 設計思想（7 First）

| 思想 | 実装 |
|------|------|
| Open Data First | Open-Meteo, OSM |
| OSS First | MIT, GitHub |
| AI Assisted Development | ツール使用を PR / レポートで開示 |
| Serverless First | DuckDB ファイル、静的 PoC |
| MVP First | PoC のみ |
| Explainability First | 線形 \(J_i\) + 寄与 UI |
| Reproducibility First | Parquet, seed 42 |

## 技術スタック

| レイヤ | 技術 |
|--------|------|
| 分析 | Python 3.11+, Pandas, DuckDB |
| 気象 | Open-Meteo REST |
| 地図 | Leaflet |
| フロント | Next.js **または** HTML+JS |
| ホスト | Vercel（GitHub 連携） |

---

## 再現性

```bash
git clone https://github.com/KanshoVector/Heat-Town.git
cd Heat-Town
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

| パス | Git |
|------|-----|
| `data/samples/` | **.gitignore**（各自 `pipeline --sample`） |
| `data/raw/` | .gitignore |
| `data/processed/` | .gitignore |
| `mvp/public/data/` | .gitignore |

詳細: [adr/003-generated-data-not-in-git.md](adr/003-generated-data-not-in-git.md)

---

## デプロイ（Vercel）

| 項目 | 値 |
|------|-----|
| Root | `mvp/` |
| 方式 | GitHub 連携（main → 自動） |
| 環境変数 | 不要（静的 GeoJSON） |

```bash
cd mvp && npm install && npm run dev   # Next.js 採用時
cd mvp/public && python -m http.server 8080  # HTML+JS
```

**CD は Actions から行わない**。Vercel ダッシュボードでリポジトリ連携。

---

## CI（任意・手動のみ）

**学生は pytest / ruff / CI を気にしない。** 動けば正義。

| ファイル | 内容 |
|----------|------|
| `ci.yml` | `workflow_dispatch` のみ。PR を止めない |
| `docs.yml` | Markdown Lint |
| `python.yml` | ruff + pytest |

GitHub Actions タブから手動実行。Branch Protection に Status Check は **設定しない**（PR が止まるため）。

---

## セキュリティ・コスト

API キー不要。Vercel Hobby + GitHub Free で $0。個人情報データ禁止。

詳細: [CONTRIBUTING.md](../CONTRIBUTING.md) · [data/README.md](../data/README.md)
