# ADR-008: 将来拡張 — メッシュ導出と重み推定（未実装）

**日付**: 2026-07-27  
**状態**: 提案（Phase 3+）

## 文脈

PoC では以下の**簡略化**を意図的に採用している:

- 格子間隔 100m / \(N \approx 400\) — 探索的離散化（[ADR-001 補足](../ADR.md)）
- 重み \(w_1, w_2, w_3\) — `config/weights.yaml` のペルソナ事前設定

本 ADR は **将来の厳密化オプション** を記録する。PBL スコープ外。

## 将来案 A: 空間相関長からのメッシュ導出

1. 細格子（例: 25m）でパイロットサンプリング
2. 快適度 \(C\) の empirical variogram \(\gamma(h)\) を推定
3. 実効相関長 \(\xi\)（\(\gamma(\xi) \approx \gamma(0)/e\)）から間隔 \(\Delta \in [\xi/2, \xi]\) を決定
4. ADR 更新 + `config/area.yaml` の `grid_spacing_m` をデータ駆動に

**主張しないこと**: 現行 100m 格子がナイキスト・シャノン最小十分統計量であること。

## 将来案 B: 重み推定（PCA ではない）

| 手法 | 用途 | 備考 |
|------|------|------|
| **AHP / デルファイ** | ステークホルダー調査 | Explainability First と整合 |
| **感度分析** | 順位変動の頑健性 | notebook 04 で部分実施 |
| **逆最適化** | 観測された選択行動から \(w\) 推定 | 行動データが必要 |
| ~~PCA loadings → \(w\)~~ | — | **不採用**: 分散最大化 ≠ 規範的重み |

## 将来案 C: デプロイ

- Vercel Cron + Open-Meteo `--full` で日次 GeoJSON 再生成
- ビルド smoke test（GeoJSON 存在・Feature 数 ≥ 3）

## 関連

- [ADR.md](../ADR.md)
- [004-open-data-fetch-strategy.md](004-open-data-fetch-strategy.md)
- [rejected-approaches.md](../rejected-approaches.md)
