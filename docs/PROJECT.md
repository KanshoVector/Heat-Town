# heat-town — プロジェクト正本（実装準拠）

> **最終更新**: 2026-07-28  
> 実装・README・スライド素材の **単一の参照元**。矛盾時は **コード > 本ファイル**。

---

## 概要

**heat-town** = 猛暑の外勤中に「どこへ逃げればいいか」を、近くの涼み場 Top 3 + Google Maps 徒歩ナビで答える PoC。裏側に説明可能な線形モデル \(J_i\) がある。

| 層 | ユーザー | 体験 |
|----|----------|------|
| **Primary** | 外勤・現場 | Top 3 涼み場 + Maps ナビ（[ADR-007](adr/007-rest-first-ux.md)） |
| **Secondary** | PBL 発表・行政 | 400 点格子・重みスライダー・寄与分解 |

**公開 URL**: https://kanshovector.github.io/Heat-Town/?demo=1  
**本番ホスト**: GitHub Pages（`deploy-pages.yml`）。Vercel も `vercel.json` で可。

---

## 対象エリア

- **中心**: 武蔵野大学 有明キャンパス（35.634, 139.790）
- **評価グリッド**: 2km 四方 · 100m 間隔 · **約 400 点**
- **サービスエリア**: 半径 1500m。エリア外 / `?demo=1` → 有明補正
- **涼み場検索**: 800m 以内の POI のみ

`config/origin.yaml` は preprocess が読込。`config/area.yaml` / `weights.yaml` は参照用（コードは定数ハードコード）。

---

## データ（現状 = サンプルのみ）

```bash
python -m heat_town.cli pipeline --sample
```

| データ | 設計上 | **実装** |
|--------|--------|----------|
| 気象 | Open-Meteo | `samples.py` 決定論的 CSV（seed=42） |
| POI | OSM | `samples.py` GeoJSON **32 点**（公園6・樹18・ビル影8） |
| グリッド | 内部生成 | `samples.py` 400 点 |

- `--full`（実 API）は **未実装**（[ADR-004](adr/004-open-data-fetch-strategy.md)）
- 前処理: **pandas + haversine**（DuckDB 未使用、[ADR-006](adr/006-pandas-preprocess-over-duckdb.md)）
- 固定時刻: **hour=15**。時刻切替 UI なし
- 出力: `data/processed/features.parquet` → `mvp/public/data/*.geojson`（Git 管理外）

---

## モデル

### 格子評価 \(J_i\)

\[
J_i = w_1 d + w_2(100-C) + w_3 \text{WBGT}
\]

低いほど望ましい。重みプリセット: balanced / elderly / commuter / heat_alert（各 README 参照）。

**WBGT**（全格子同一）: `0.735T + 0.0375RH + 0.00292T·RH + 7.85` — 推定値、公式観測ではない。

**格子の d**: origin からの正規化距離（`d_max=1500m`）。  
**格子の C**: 最寄り POI 距離 + 風速プロキシ（kind 区別なし）。

### 涼み場ランキング（`rest_finder.py`）

```
d_norm = min(徒歩距離_m / 800, 1)
J_i = w₁·d_norm + w₂·(100−C) + w₃·WBGT   ← POI 地点、kind 別 C
score = 0.6·d_norm + 0.4·(J_i/100)      ← 低いほど良い、Top 3
```

---

## フロント（`mvp/public/`）

HTML + Leaflet + 素の JS（Next.js なし）。

| 機能 | 説明 |
|------|------|
| 📍 現在地 | Geolocation → Top 3 |
| Top 3 カード | 名称・徒歩・快適度・Maps リンク |
| WBGT バナー | エリア共通推定値 |
| 🕹️ クリックモード | 仮想現在地 |
| 📊 分析モード | 400 点色分け（circleMarker）・スライダー・危険 Top 10 |

J_i 再計算はクライアント側 O(n)（[ADR-005](adr/005-client-side-ji-recompute.md)）。Python/JS で式を二重管理。

---

## 限界（発表で先に言う）

| 項目 | 現状 |
|------|------|
| 日陰 ray tracing | ❌ POI 位置プロキシ |
| リアルタイム WBGT/API | ❌ サンプル静的 GeoJSON |
| 400 点格子 | PoC 固定、理論的根拠なし |
| 因果主張 | ❌ 相対ランキングのみ |
| 実 Open-Meteo/OSM | Phase 2 |

詳細: [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md)

---

## 発表・評価

- **5–6 分スライド**: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)
- **個人レポート**: [delivery.md](delivery.md)
- **社会提言**: [social-proposals.md](social-proposals.md)
- **設計判断**: [ADR.md](ADR.md)

---

## ファイル構成

```
src/heat_town/     model, preprocess, export, rest_finder, samples, cli
mvp/public/        index.html, js/app.js, data/*.geojson
config/            origin.yaml（読込）, area.yaml, weights.yaml（参照）
notebooks/         EDA・感度分析
tests/             34 tests
```

---

## ローカル起動

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e ".[dev]"
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
# → http://localhost:8080/?demo=1
pytest
```
