# Architecture Decision Records — 索引（誠実版）

heat-town の**実装済み**設計判断の入口。詳細は [adr/](adr/) 配下の各 ADR を参照。

> **注意**: 本プロジェクトは PoC です。ナイキスト・シャノン采样定理や PCA による重み自動決定など、**未実装の理論を主張しません**。

## 採用済み ADR

| ID | タイトル | 要点 |
|----|----------|------|
| [001](adr/001-linear-decision-model.md) | 線形多目的モデル Jᵢ | 説明可能性 First。重みはペルソナ事前設定 |
| [002](adr/002-static-geojson-poc.md) | 静的 GeoJSON + Leaflet | サーバーレス配信 |
| [003](adr/003-generated-data-not-in-git.md) | 生成データは Git 外 | Vercel ビルド時に pipeline 実行 |
| [004](adr/004-open-data-fetch-strategy.md) | Open-Meteo / OSM 方針 | PBL は `--sample` |
| [005](adr/005-client-side-ji-recompute.md) | クライアント側 Jᵢ 再計算 | 重み変更を即時反映 |
| [006](adr/006-pandas-preprocess-over-duckdb.md) | pandas 前処理 | PoC スコープ優先 |
| [007](adr/007-rest-first-ux.md) | Rest-first UX | Primary=涼み場 Top3、Secondary=分析 |
| [008](adr/008-future-extensions.md) | **将来拡張（未実装）** | メッシュ導出・重み推定 |

## 格子 400 点について（ADR-001 補足）

2km 四方を **100m 間隔で探索的に離散化**した PoC 用サンプル（\(N \approx 400\)）。

- **主張しないこと**: ナイキスト・シャノン定理に基づく「最小十分統計量」
- **主張すること**: 計算量 \(O(N)\) とブラウザ即時 UX の **Pareto 妥協点**（400 点なら JS 再計算 < 1ms）
- 本番拡張時は [ADR-008](adr/008-future-extensions.md) の variogram ベース間隔設計を検討

## 重み \(w_1, w_2, w_3\) について

- **現状**: `config/weights.yaml` のペルソナ別事前設定（専門家仮定 + 感度分析 notebook）
- **主張しないこと**: PCA による自動重み決定（PCA は分散最大化であり、規範的意思決定と目的が異なる）
- **将来**: AHP / 逆最適化 — [ADR-008](adr/008-future-extensions.md)

## 更新ルール

判断を変えたら新 ADR を追加。旧 ADR は superseded として残す。
