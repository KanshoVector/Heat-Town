# heat-town — 批判的レビュー（PoC 限界の正直な一覧）

> **最終更新**: 2026-07-27  
> 実装を正とし、docs の古い記述より **コードの挙動** を優先して整理。

---

## できていること（docs 要求以上）

| 項目 | 状態 | 備考 |
|------|------|------|
| 近くの涼み場 Top 3 + Maps ナビ | ✅ | Primary UX（docs/mvp.md の旧「格子中心」を上書き） |
| エリア外・デモガード | ✅ | 1.5km 外 / `?demo=1` → 有明補正、0 件フォールバック |
| Google Maps 起点固定 | ✅ | デモ時は有明→涼み場の徒歩ルート |
| Playground（地図クリック） | ✅ | docs 未記載だが QA 用に追加 |
| Vercel ビルド時 GeoJSON 生成 | ✅ | ADR-003 の「空デプロイ」問題を解消 |
| pytest + ruff | ✅ | 33 tests |
| ADR 000–008 | ✅ | 未実装理論（ナイキスト・PCA 等）を排除 |

---

## まだ PoC 限界のもの（言い訳なし）

### データ・モデル

| 限界 | 詳細 |
|------|------|
| **WBGT は全エリア同一値** | 1 時刻の推定式出力。地点別の暑さ差はほぼ快適度 C のみ |
| **WBGT は公式観測ではない** | 気温・湿度からの近似。絶対値より相対比較向け |
| **POI は 32 点のサンプル** | OSM 実データではなく `samples.py` の決定論的生成 |
| **快適度 C は POI 距離プロキシ** | 建物影の ray tracing・日射角は未実装 |
| **kind（公園/樹/ビル影）の差** | 格子前処理では kind 無視。涼み場ランキングのみ kind 別 C |
| **100m × 400 点格子** | 探索的離散化。ナイキスト等の理論保証なし（[ADR.md](ADR.md)） |
| **重み w₁,w₂,w₃** | ペルソナ事前設定。PCA/AHP/逆最適化は未実装（[ADR-008](adr/008-future-extensions.md)） |
| **Jᵢ の d の意味** | 格子=origin 距離、涼み場=徒歩距離（文脈で別） |

### フロント・UX

| 限界 | 詳細 |
|------|------|
| **leaflet.heat 未導入** | docs/mvp.md の「ヒートマップ」は格子点 ON/OFF で代替 |
| **時刻切替（8h/15h）** | 未実装。pipeline は hour=15 固定 |
| **リアルタイム気象 API** | 未接続。静的 GeoJSON |
| **サービスエリア外** | 涼み場データは有明 2km のみ。他都市ではデモ補正のみ |

### インフラ・docs ギャップ

| 限界 | 詳細 |
|------|------|
| **`config/area.yaml` 未読込** | `samples.py` に定数ハードコード |
| **`data.md` の DuckDB 記述** | 実装は pandas（ADR-006） |
| **`fetch --full`（Open-Meteo/OSM）** | 未実装（ADR-004） |
| **Next.js** | 未採用。HTML + Leaflet のみ |

---

## docs vs 実装 — どちらを信じるか

| docs 記述 | 実装（正） |
|-----------|-----------|
| mvp.md: ヒートマップレイヤ | 400 点 circleMarker + 分析モード toggle |
| data.md: DuckDB 前処理 | pandas + haversine |
| README 旧: 24 tests | **33 tests**（demo_guard 等追加） |
| operations.md 旧: Root `mvp/` | ルート `vercel.json` + `mvp/public` 出力 |

---

## 発表で避ける → 言い換え

| 避ける | 言い換え |
|--------|----------|
| ナイキスト・シャノン | 「100m おきに地点を置いて、全体をざっくり見ています」 |
| Pareto 最適 | 「速く動くことと、わかりやすさのバランスを取っています」 |
| 線形多目的モデル | 「距離・快適さ・暑さを足し算して、総合的に評価しています」 |
| variogram | 「近い地点ほど似た傾向になる、という調べ方（将来やりたいこと）」 |
| ray tracing | 「建物の影を光線で計算する方法（今回は公園・樹の位置で代用）」 |

---

## 次にやるなら（Phase 3+）

1. Open-Meteo / OSM `--full` + 日次 Vercel Cron
2. variogram ベースのメッシュ間隔（ADR-008）
3. 日陰ルーティング（ShadeRoute 等）— rejected-approaches 参照
4. `config/area.yaml` のコード読込統一

---

*関連: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md) | [HANDOFF.md](HANDOFF.md)*
