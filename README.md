# heat-town — 近くの涼み場を探す

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

猛暑の外勤中に **「どこへ逃げればいいか」** を3タップで答える PoC です。  
Python でデータを作り、ブラウザ地図で **近くの涼み場 Top 3** と **Google Maps 徒歩ナビ** を表示します。

```
┌─────────────┐     pipeline      ┌──────────────┐     fetch      ┌─────────────┐
│ Open Data   │ ───────────────► │ GeoJSON      │ ─────────────► │ 地図アプリ   │
│ (気象・POI) │   Python CLI     │ scores/rest  │   Leaflet JS   │ Top3 + ナビ │
└─────────────┘                   └──────────────┘                └─────────────┘
```

## 公開 URL（そのまま開くだけ）

**https://kanshovector.github.io/Heat-Town/?demo=1**

発表・デモ用。有明キャンパス固定・エリア外でも壊れません。

---

## 10 秒でローカル試す（任意）

```bash
git clone https://github.com/KanshoVector/Heat-Town.git && cd Heat-Town
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e ".[dev]"
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
```

→ **http://localhost:8080** を開く（発表デモ: **http://localhost:8080/?demo=1**）

| 操作 | 説明 |
|------|------|
| 📍 ボタン | GPS で近くの涼み場 Top 3 |
| 🕹️ クリックモード | 地図タップで仮想現在地を変更 |
| 🔄 有明に戻す | デモ初期位置へリセット |
| 📊 分析モード | 400 点格子・重みスライダー（折りたたみ） |

> **初回必須**: `data/` と `mvp/public/data/*.geojson` は Git 管理外です。上記 `pipeline --sample` を必ず実行してください。

## 何をしているか（30 秒）

各候補地点の「暑さリスク」を次の式で評価し、**近さ** と **快適度** から涼み場を選びます。

```text
Jᵢ = w₁·d + w₂·(100−C)/100 + w₃·WBGT/40   ← 各項 [0,1]、小さいほど良い
涼み場スコア = 0.6×(徒歩距離/800m) + 0.4×Jᵢ
```

- **Primary UX**: 現場向け — 涼み場 3 件 + Maps ナビ
- **Secondary UX**: 発表向け — 格子ヒートマップ + 重み変更デモ

## 開発者向け

```bash
pytest                    # 34 tests
ruff check src tests
python -m heat_town.cli pipeline --sample   # データ再生成
```

| パス | 役割 |
|------|------|
| `src/heat_town/rest_finder.py` | 涼み場 Top-k・エリア外ガード |
| `src/heat_town/export.py` | GeoJSON 出力 |
| `mvp/public/js/app.js` | 地図 UI・Playground |
| `vercel.json` | デプロイ時に pipeline 自動実行 |

## デプロイ

**本番（GitHub Pages）**: https://kanshovector.github.io/Heat-Town/?demo=1  
`main` へ push すると [deploy-pages.yml](.github/workflows/deploy-pages.yml) が自動ビルド・公開。

Vercel も [vercel.json](vercel.json) で対応可（GitHub 連携または `vercel` CLI）。

## ドキュメント

| ファイル | 内容 |
|---------|------|
| [docs/PROJECT.md](docs/PROJECT.md) | プロジェクト正本 |
| [docs/ADR.md](docs/ADR.md) | 設計判断・トレードオフ |
| [docs/SLIDE_DECK_MATERIALS.md](docs/SLIDE_DECK_MATERIALS.md) | 5 分発表・原稿・Q&A |
| [docs/CRITICAL_REVIEW.md](docs/CRITICAL_REVIEW.md) | PoC の限界 |

## License

[MIT License](LICENSE)
