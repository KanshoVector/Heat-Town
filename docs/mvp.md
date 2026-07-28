# MVP（PoC）

> 全体像: [PROJECT.md](PROJECT.md)

## 位置づけ

分析パイプラインの **出力ビューア**。本番 Web アプリではない。

| 区分 | PoC | 本番 |
|------|-----|------|
| 目的 | 行動支援 + モデル説明 | 継続運用 |
| データ | 静的 GeoJSON | リアルタイム API |
| 成功 | 5–6 分で JTBD + \(J_i\) 説明 | DAU / SLA |

## UX（実装済み）

**Primary — 休憩モード**

1. Geolocation または有明デフォルト
2. 涼み場 Top 3 カード（800m 以内）
3. Google Maps 徒歩ナビ
4. `?demo=1` で安全デモ

**Secondary — 分析モード**（`<details>` 折りたたみ）

1. 400 点格子 ON/OFF（circleMarker 色分け）
2. 重みスライダー + 4 プリセット
3. popup 寄与 3 項
4. 危険 Top 10

## 未実装（Should だったもの）

- 時刻切替（8h/15h）
- leaflet.heat レイヤ
- npm / Next.js

## 起動

[mvp/README.md](../mvp/README.md) · 運用: [operations.md](operations.md)
