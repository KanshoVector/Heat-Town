# ADR-006: PoC 前処理は pandas 優先（DuckDB は将来）

**日付**: 2026-07-26  
**状態**: 採用

## 文脈

`docs/data.md` / [PROJECT.md](../PROJECT.md) は pandas 実装に準拠。

## 決定

- **現行 SSoT**: `heat_town.preprocess.run_sample()` → `features.parquet`
- DuckDB / EPSG:6677 平面距離は **スコープ外**（docs は参考 spec）
- 距離: haversine（EPSG:4326）で PoC 十分
- POI 最近傍: numpy ベクトル化（2026-07-26 改善）

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| pandas のみ（採用） | 依存既存、学生が読みやすい | docs との用語差 |
| DuckDB 統合（将来） | 大規模 join、SQL 再現性 | セットアップ・学習コスト |

## 関連

- [data.md](../data.md)
- [000-risks-register.md](000-risks-register.md) R-10, R-11
