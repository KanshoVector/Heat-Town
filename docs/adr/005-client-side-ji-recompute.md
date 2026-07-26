# ADR-005: クライアント側 Jᵢ 再計算

**日付**: 2026-07-26  
**状態**: 採用

## 文脈

デモで重みスライダーを **1 秒以内** に反映（docs/mvp.md 受入基準）。

## 決定

GeoJSON には **生の** `d`, `comfort`, `wbgt`（+ 参考 ji）を載せ、  
MVP はブラウザで `normalizeWeights` → 再計算 → 再描画。

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| クライアント再計算（採用） | O(n) 即時、サーバー不要 | Python export ji とスライダー ji が一致しない場合あり（スライダーが正） |
| 重みごと事前 export | 完全一致 | ファイル数爆増 |

## バグ修正（2026-07-26）

`export.py` が `normalize_weights` 戻り値を捨てていた問題を修正。export 時 ji は正規化重みで計算。

## 計算量

- n ≈ 400: 再計算 < 1ms（JS）
- n ≈ 10,000: 依然実用（README 記載）

## 関連

- [002-static-geojson-poc.md](002-static-geojson-poc.md)
