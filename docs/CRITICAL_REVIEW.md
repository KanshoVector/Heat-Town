# heat-town — 批判的レビュー（PoC 限界）

> **最終更新**: 2026-07-28  
> 実装を正とする。詳細正本: [PROJECT.md](PROJECT.md)

---

## できていること

| 項目 | 状態 |
|------|------|
| 涼み場 Top 3 + Maps ナビ | ✅ Primary UX |
| エリア外・デモガード | ✅ 1500m 外 / `?demo=1` → 有明補正 |
| Google Maps 起点固定 | ✅ デモ時は有明→涼み場 |
| 分析モード（格子・スライダー） | ✅ Secondary UX |
| Playground（地図クリック） | ✅ |
| GitHub Pages / Vercel ビルド時 GeoJSON 生成 | ✅ |
| pytest + ruff | ✅ 34 tests |
| ADR 000–008 | ✅ |

---

## PoC 限界（言い訳なし）

### データ・モデル

| 限界 | 詳細 |
|------|------|
| WBGT 全エリア同一 | 1 時刻（hour=15）固定 |
| WBGT 推定式 | 公式観測ではない |
| POI 32 点サンプル | OSM 実データではない |
| 快適度 C | POI 距離/kind プロキシ。ray tracing なし |
| 格子前処理 | kind 無視。涼み場のみ kind 別 C |
| 400 点格子 | 理論的根拠なし |
| 重み | ペルソナ事前設定。PCA/AHP なし |
| J_i の d | 格子=origin 距離、涼み場=徒歩/800m |
| `--full` API | 未実装 |

### UX

| 限界 | 詳細 |
|------|------|
| 時刻切替 | 未実装 |
| leaflet.heat | 未使用（circleMarker） |
| サービスエリア | 有明 2km のみ |

### 設定

| 限界 | 詳細 |
|------|------|
| `area.yaml` / `weights.yaml` | コード未読込（定数ハードコード） |

---

## 発表で避ける → 言い換え

| 避ける | 言い換え |
|--------|----------|
| ナイキスト | 100m おき PoC 区切り |
| 実データ取得済み | サンプルでパイプライン完走、実 API は Phase 2 |
| ray tracing | 公園・樹の位置で代用 |
| 因果・安全保証 | 相対的な休憩候補の優先順位 |

---

## Phase 3+

1. Open-Meteo / OSM `--full`
2. variogram メッシュ（ADR-008）
3. 日陰ルーティング
4. config YAML のコード読込統一

---

*関連: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)*
