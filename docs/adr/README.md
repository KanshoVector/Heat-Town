# Architecture Decision Records (ADR)

heat-town の**実装済み**判断と、残リスクの一覧。学生向け入口は [START.md](../../START.md)。詳細 spec は [docs/data.md](../data.md) 等。

## 索引

| ID | タイトル | 状態 |
|----|----------|------|
| [000](000-risks-register.md) | リスク登録簿（横断） | 採用 |
| [001](001-linear-decision-model.md) | 線形多目的モデル Jᵢ | 採用 |
| [002](002-static-geojson-poc.md) | 静的 GeoJSON + Leaflet PoC | 採用 |
| [003](003-generated-data-not-in-git.md) | 生成データを Git 管理外にする | 採用 |
| [004](004-open-data-fetch-strategy.md) | Open-Meteo / OSM 取得方針（2026-07） | 採用 |
| [005](005-client-side-ji-recompute.md) | クライアント側 Jᵢ 再計算 | 採用 |
| [006](006-pandas-preprocess-over-duckdb.md) | PoC 前処理は pandas 優先 | 採用 |

## 更新ルール

- 判断を変えたら新 ADR を追加（番号インクリメント）。旧 ADR は「 superseded by NNN 」と残す。
- PBL スコープ外の拡張（リアルタイム API、Next.js 本番化など）は [rejected-approaches.md](../rejected-approaches.md) 参照。
