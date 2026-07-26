# ADR-002: 静的 GeoJSON + Leaflet PoC

**日付**: 2026-07-26  
**状態**: 採用

## 文脈

2–3 日 PBL。本番 Web アプリではなく **分析結果ビューア**。

## 決定

- `mvp/public/` = HTML + vanilla JS + Leaflet
- 入力 = `scores.geojson`（pipeline 出力）
- ホスト = Vercel 静的（GitHub 連携、Actions デプロイなし）

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| 静的 HTML+JS（採用） | 依存最小、即デモ | リアルタイム不可 |
| Next.js 本番（将来） | SSR/API | PBL スコープ超過 |

## PR #5 から継承した点（2026-07-26）

- quantile 色分け（外れ値に強い）
- プロパティ名互換（`d`/`distance`, `C`/`comfort`）
- popup HTML エスケープ、Leaflet SRI、status 表示

## 不採用（PR #5）

- デモ用 4 点 GeoJSON の Git commit（方針違反）

## 関連

- [mvp.md](../mvp.md)
