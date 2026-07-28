# 分析と可視化

> 全体像: [PROJECT.md](PROJECT.md)

## 研究仮説

| ID | 仮説 | 検証 |
|----|------|------|
| H1 | \(w_2\) 増で緑地周辺順位上昇 | プリセット比較 |
| H2 | 15 時の \(J_i\) が 8 時より大 | notebook 時刻比較 |
| H3 | POI 欠損区域で \(C\) 分散小 | 区域別分散 |
| H4 | `heat_alert` で WBGT 寄与増 | 寄与分解 |

## 手順

1. `features.parquet` 記述統計
2. 空間パターン（top 10% クラスタ）
3. 重み感度（プリセット / スライダー）

notebook: `notebooks/02–04`

## 可視化（実装）

| レイヤ | データ | UI |
|--------|--------|-----|
| OSM タイル | ベース | 常時 |
| 格子 400 点 | `scores.geojson` | 分析モード ON |
| POI Top 3 | `rest_spots.geojson` | Primary |

- 配色: J_i 分位 → 5 色（`app.js` COLORS）
- popup: 寄与 3 項バー
- 重み: クライアント O(n) 再計算（ADR-005）
- 時刻切替 UI: **未実装**

限界: 相関≠因果、単都市、WBGT 推定誤差。

次: [social-proposals.md](social-proposals.md)
