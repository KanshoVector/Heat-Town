# ADR-007: Rest-first UX（休憩モード Primary）

**日付**: 2026-07-27  
**状態**: 採用

## 文脈

heat-town の JTBD は 2 層ある。

| 層 | ユーザー | 求めるもの |
|----|----------|------------|
| **Primary** | 外勤・肉体労働者 | 今すぐ近くで休める涼しい場所 + ナビ |
| **Secondary** | PBL 発表者・行政デモ | Jᵢ 式・寄与・400 点格子の説明 |

旧 MVP は Secondary のみ（400 点 + 重みスライダー）で、Primary JTBD を満たしていなかった。

## 決定

1. **Primary UX = 休憩モード**: Geolocation → Top-3 涼み場カード → Google Maps 徒歩ナビ
2. **Secondary UX = 分析モード**: `<details>` 折りたたみ内に格子 400 点・スライダー・危険 Top 10
3. **コアアルゴリズム = `find_rest_spots()`**（`src/heat_town/rest_finder.py`）
   - 候補: POI（公園 / 街路樹 / ビル影）
   - 距離: Haversine（max 800m）
   - 不快度: 既存 `compute_ji()` を再利用
   - 複合スコア: `0.6 × (距離/800) + 0.4 × (Jᵢ/100)` — 低いほど良い
4. **地図**: OSM 標準タイル。POI ピンのみ表示（格子は分析モード ON 時のみ）
5. **パイプライン出力**: `rest_spots.geojson`（デフォルト現在地 = 有明キャンパス）

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| POI ランキング（採用） | すずみば型 JTBD に直結、3 タップでナビ | POI 密度が低いエリアでは候補不足 |
| 400 点格子を Primary（不採用） | モデル説明に便利 | 現場ユーザーが「どこに行けばいいか」わからない |
| 日陰ルーティング（Phase 3） | 経路最適 | PBL スコープ外（数日〜） |
| クライアント側再ランキング（採用） | Geolocation 即時反映（ADR-005 延長） | Python/JS でスコア式の二重管理 |

## 結果

- `rest_finder.py` + `export_rest_spots_geojson()` + `mvp/public/js/app.js`
- 既存 Jᵢ モデル（ADR-001）は分析エンジンとして温存
- 格子 400 点は「データセット」、涼み場 3 つが「プロダクト」

## 関連

- [SESSION_HANDOFF.md](../SESSION_HANDOFF.md)
- [ADR-001](001-linear-decision-model.md) — Jᵢ 線形モデル
- [ADR-005](005-client-side-ji-recompute.md) — クライアント側再計算
