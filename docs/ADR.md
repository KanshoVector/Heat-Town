# Architecture Decision Records（ADR）

> **目的**: 「なぜそうしたか」を数秒で思い出し、後からのハルシネーション・ブラックボックス化を防ぐ。  
> 正本の実装詳細: [PROJECT.md](PROJECT.md)

**更新ルール**: 判断を変えたら本ファイルに追記。未実装の理論（ナイキスト・PCA 重み等）を **主張しない**。

---

## 索引

| ID | 決定 | 状態 |
|----|------|------|
| [001](#adr-001-線形-j_i-モデル) | 線形 \(J_i\) + 400 点格子 | 採用 |
| [002](#adr-002-静的-geojson--leaflet) | 静的 GeoJSON 配信 | 採用 |
| [003](#adr-003-生成データは-git-外) | 生成データ Git 外 | 採用 |
| [004](#adr-004-オープンデータ取得方針) | PBL は `--sample` | 採用 |
| [005](#adr-005-クライアント側-j_i-再計算) | ブラウザ即時再計算 | 採用 |
| [006](#adr-006-pandas-前処理) | pandas 優先 | 採用 |
| [007](#adr-007-rest-first-ux) | Top 3 + ナビ Primary | 採用 |
| [008](#adr-008-将来拡張) | メッシュ・重み推定 | 提案 |
| [R](#残リスク) | 残リスク | 監視 |

---

## ADR-001: 線形 J_i モデル

**文脈**: 行政・市民への説明が評価軸。予測精度競争ではない。

**決定**: \(J_i = w_1 d + w_2(100-C) + w_3 \text{WBGT}\)。寄与分解 + 重みスライダー。

| 採用 | 不採用 |
|------|--------|
| 線形和（`model.py`） | ML / NN（説明困難） |
| 400 点格子（100m 間隔） | ナイキスト等の理論的主張 |
| ペルソナ重み（`weights.yaml` 参照） | PCA → 重み（分散最大化 ≠ 規範的判断） |

**400 点の位置づけ**: O(N) でブラウザ即時 UX との妥協点。**100m 未満の現象は見逃す**。

---

## ADR-002: 静的 GeoJSON + Leaflet

**文脈**: PBL 期間中にサーバー運用・認証は不要。

**決定**: `pipeline --sample` → GeoJSON → HTML/JS 地図。ビルド時生成。

| 採用 | 不採用 |
|------|--------|
| Leaflet + 静的ファイル | リアルタイム API サーバー |
| GitHub Pages / Vercel 静的 | Next.js 本番（スコープ超過） |

**実装**: `export.py`, `mvp/public/`

---

## ADR-003: 生成データは Git 外

**文脈**: GeoJSON / parquet は大きくなりうる。clone 直後は空。

**決定**: `data/samples/`, `processed/`, `mvp/public/data/` を .gitignore。デプロイ時に `pipeline --sample` 実行。

| 採用 | 不採用 |
|------|--------|
| CI/Pages ビルド時生成 | 生成物を Git に commit |
| seed=42 で再現 | 手動アップロード依存 |

**実装**: `deploy-pages.yml`, `vercel.json`

---

## ADR-004: オープンデータ取得方針

**文脈**: Open Data First だが PBL は非商用・低頻度。

**決定**: 現フェーズは **`--sample` のみ**。`--full`（Open-Meteo / OSM）は Phase 2。

| 採用 | 不採用 |
|------|--------|
| 決定論的サンプル（再現性） | 毎回 live API（レート・ライセンスリスク） |
| 将来: 1 call/bbox + キャッシュ | Overpass 常時依存 |

**注意**: サンプルは API **相当形式** であり、実取得済みではない（発表で明言）。

---

## ADR-005: クライアント側 J_i 再計算

**文脈**: 重みスライダーを 1 秒以内に反映したい。

**決定**: 400 点 × スライダー変更を **ブラウザ O(n)** で再計算。涼み場 Top 3 も同様。

| 採用 | 不採用 |
|------|--------|
| JS 即時反映 | サーバー再計算 API |
| Python export + JS 実行 | サーバーレス関数 |

**トレードオフ**: `compute_ji` / `find_rest_spots` が **Python/JS 二重管理**（drift リスク）。

**実装**: `mvp/public/js/app.js`

---

## ADR-006: pandas 前処理

**文脈**: PoC データ量（400 点 × 32 POI）は pandas で十分。

**決定**: `preprocess.py` = pandas + haversine。DuckDB / EPSG:6677 は **将来**。

| 採用 | 不採用 |
|------|--------|
| pandas（学習コスト低） | DuckDB 統合（PBL 期間中は過剰） |
| Haversine WGS84 | 平面直角座標変換 |

**実装**: `preprocess.py`（`origin.yaml` のみ読込）

---

## ADR-007: Rest-first UX

**文脈**: 旧 MVP は 400 点格子中心で、現場 JTBD「どこへ逃げるか」を満たさなかった。

**決定**:

1. **Primary** = Geolocation → Top 3 → Google Maps 徒歩ナビ
2. **Secondary** = 分析モード（格子・スライダー・危険 Top 10）
3. 複合スコア: `0.6×(距離/800) + 0.4×(J_i/100)`

| 採用 | 不採用 |
|------|--------|
| POI ランキング（800m） | 格子を Primary に |
| クライアント再ランキング | 日陰ルート最適（Phase 3） |

**キーメッセージ**: 400 点はデータセット、涼み場 3 つがプロダクト。

**実装**: `rest_finder.py`, `app.js`

---

## ADR-008: 将来拡張（未実装）

**提案のみ**。PBL スコープ外。

| 案 | 内容 |
|----|------|
| A メッシュ | variogram → 相関長 ξ → 間隔 Δ をデータ駆動 |
| B 重み | AHP / 逆最適化（**PCA 不採用**） |
| C デプロイ | Vercel Cron + `--full` 日次再生成 |

---

## 残リスク

| ID | リスク | 緩和 |
|----|--------|------|
| R-01 | WBGT 推定誤差 | 相対比較に限定、発表で明言 |
| R-02 | POI サンプル 32 点 | `--full` は Phase 2 |
| R-03 | Python/JS 式 drift | 変更時は両方テスト |
| R-04 | エリア外 GPS | 有明補正 + `?demo=1` |
| R-05 | 因果の過大解釈 | 優先順位づけのみと説明 |

---

## 主張しないこと（ハルシネーション防止）

- ナイキスト / シャノンに基づく最小サンプル数
- PCA による重みの「最適」決定
- 建物影 ray tracing による日陰
- Open-Meteo / OSM **実データ取得済み**
- 因果関係・絶対的安全の保証

---

*関連: [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md) | [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)*
