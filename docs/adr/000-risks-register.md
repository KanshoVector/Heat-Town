# ADR-000: リスク登録簿

**日付**: 2026-07-26  
**状態**: 採用（living document）

## 目的

セキュリティ・運用・計算量・オープンデータ・エッジケースを横断で追跡する。

## リスク一覧

| ID | 領域 | リスク | 影響 | 現状の緩和 | 残課題 |
|----|------|--------|------|------------|--------|
| R-01 | モデル | WBGT は推定値で絶対値不可 | 誤った政策判断 | README Q&A・GLOSSARY で相対比較限定 | 観測所データ連携はスコープ外 |
| R-02 | モデル | 線形仮定・因果非主張 | 過度な解釈 | decision-model 限界節 | — |
| R-03 | データ | OSM POI 欠損・偏り | d/C の歪み | 欠損時 cap（1500m）、notebook 01 | `--full` 取得未実装 |
| R-04 | データ | Open-Meteo 解像度 | 地点差の過小評価 | 考察で明記 | 有料 tier / ERA5 は将来 |
| R-05 | オープンデータ | Overpass 公共 API 不安定（2026） | fetch 失敗・IP 制限 | サンプル代替、ADR-004 | User-Agent・mirror・`.pbf` ローカル化 |
| R-06 | オープンデータ | Open-Meteo 非商用 1 万 calls/日 | CI/再取得でブロック | PBL は `--sample` 中心 | 商用は有料プラン必須 |
| R-07 | セキュリティ | Leaflet CDN 改ざん | XSS/供給網 | SRI 付与（index.html） | 完全オフライン bundle は未 |
| R-08 | セキュリティ | popup HTML 注入 | XSS | `escapeHtml`（app.js） | 外部 GeoJSON 取込時も同関数必須 |
| R-09 | 運用 | scores.geojson 未生成で Vercel 空地図 | デモ失敗 | README + status UI + pipeline 必須 | デプロイ前チェックリスト |
| R-10 | 運用 | docs と実装の乖離 | 学生混乱 | ADR + README 更新 | DuckDB 本格パイプラインは未 |
| R-11 | 計算量 | N 点 × M POI 最近傍 | 前処理遅延 | numpy ベクトル化（~400×32） | 1 万点超は spatial index |
| R-12 | 計算量 | export iterrows | 大規模で遅い | PoC N≈400 で許容 | 完全 vectorize GeoJSON 生成 |
| R-13 | エッジケース | 重み合計 0 | NaN / 除算 | normalize で balanced fallback | export は ValueError |
| R-14 | エッジケース | comfort 範囲外 | Jᵢ 異常 | preprocess clip 0–100 | export 入力検証は最小 |
| R-15 | 再現性 | samples Git 外 | クローン直後空 | pipeline --sample 必須 | seed 42 は samples のみ |
| R-16 | ガバナンス | main 直 push | 品質低下 | CONTRIBUTING PR フロー | CI は手動のみ（意図的） |

## 関連

- [004-open-data-fetch-strategy.md](004-open-data-fetch-strategy.md)
- [operations.md](../operations.md)
