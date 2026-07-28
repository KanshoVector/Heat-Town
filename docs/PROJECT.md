# heat-town — プロジェクト正本

> 実装・発表の **唯一の参照元**。矛盾時は **コード > 本ファイル**。

---

## 概要

猛暑の外勤中に「どこへ逃げればいいか」を、**涼み場 Top 3 + Google Maps 徒歩ナビ** で答える PoC。裏側に説明可能な線形モデル \(J_i\)。

| 層 | 体験 |
|----|------|
| **Primary** | Geolocation → Top 3 → Maps ナビ |
| **Secondary** | 400 点格子・重みスライダー・寄与分解・危険 Top 10 |

**URL**: https://kanshovector.github.io/Heat-Town/?demo=1  
**ホスト**: GitHub Pages（`deploy-pages.yml`）。Vercel も `vercel.json` で可。

---

## チーム分担（取り決め）

**フォルダ単位のブロック分担**のみ記録。個人名と担当の対応表はリポジトリに残っていない。

| ブロック | フォルダ | 人数目安 |
|----------|----------|----------|
| データ取得・前処理 | `data/`, `src/` cli | 1 |
| 分析 | `notebooks/` | 2 |
| モデル・GeoJSON | `src/` | 1 |
| 地図 PoC | `mvp/` | 1 |
| 手伝い | 上記のサポート | 1 |
| 発表・スライド | `docs/` | 発起人 |

コミット履歴上は複数メンバーが存在するが、**誰がどこまでやったかの公式記録はない**。個人レポート等は各自で記述する想定。

---

## 対象エリア

- 中心: 武蔵野大学 有明キャンパス（35.634, 139.790）
- 格子: 2km 四方 · 100m 間隔 · **約 400 点**
- サービスエリア: 半径 1500m（外 / `?demo=1` → 有明補正）
- 涼み場: **800m 以内** POI のみ

---

## データ（現状 = サンプルのみ）

```bash
python -m heat_town.cli pipeline --sample
```

| データ | 実装 |
|--------|------|
| 気象 | `samples.py` 決定論的 CSV（seed=42） |
| POI | 32 点（公園6・樹18・ビル影8） |
| グリッド | 400 点 |

- `--full`（Open-Meteo / OSM 実 API）**未実装**
- 前処理: **pandas + haversine**（DuckDB 未使用）
- 固定時刻 hour=15。生成物は Git 管理外 → デプロイ時に自動生成

---

## モデル

### 格子 \(J_i\)（低いほど良い）

\[
J_i = w_1 d + w_2 \frac{100-C}{100} + w_3 \frac{\text{WBGT}}{40}
\]

各項は [0,1] に正規化してから加重和（低いほど望ましい）。

**WBGT**（全格子同一）: `0.735T + 0.0375RH + 0.00292T·RH + 7.85` — 推定値（式中は `/40` で正規化）。  
**格子の d**: origin からの正規化距離（`d_max=1500m`）。  
**格子の C**: `0.8·c_green + 0.2·c_wind`（最寄り POI 距離 + 風速）。

### 涼み場ランキング（`rest_finder.py`）

```
d_norm = min(徒歩距離_m / 800, 1)
J_i = w₁·d_norm + w₂·(100−C)/100 + w₃·WBGT/40   ← kind 別 C
score = 0.6·d_norm + 0.4·J_i                   ← 低いほど良い、Top 3
```

### 重みプリセット

| preset | w₁ | w₂ | w₃ |
|--------|----|----|-----|
| balanced | 0.3 | 0.4 | 0.3 |
| elderly | 0.2 | 0.5 | 0.3 |
| commuter | 0.5 | 0.2 | 0.3 |
| heat_alert | 0.2 | 0.2 | 0.6 |

ペルソナ事前設定。PCA/AHP 等の自動決定はしていない。

---

## フロント（`mvp/public/`）

HTML + Leaflet + 素の JS。J_i 再計算はクライアント O(n)（Python/JS 二重管理）。

| 機能 | 説明 |
|------|------|
| Top 3 + Maps | Primary |
| WBGT バナー | エリア共通推定値 |
| 分析モード | 格子色分け・スライダー・危険 Top 10 |
| クリックモード | 仮想現在地 |

---

## 設計判断

トレードオフ・採否理由の詳細: **[ADR.md](ADR.md)**（数秒で思い出す用）

| 決定 | 理由（一行） |
|------|-------------|
| 線形 \(J_i\) | 説明可能性（ML 不採用） |
| 静的 GeoJSON | サーバーレス、再現性 |
| Rest-first UX | 現場 JTBD 優先 |
| `--sample` のみ | 再現性・ライセンス |
| pandas 前処理 | PoC スコープ優先 |

---

## 社会提言（分析結果の例）

| ID | 提言 |
|----|------|
| P1 | 14–16 時 Cooling Shelter 拡充 |
| P2 | \(J_i\) top 10% を重点パトロール |
| P7 | 不快寄与 top 区域へ街路樹 |
| P8 | 分散型緑 300m 圏 |

※ 数値根拠は notebook 分析に依存。サンプルデータベースである点は [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md) 参照。

---

## 限界・運用

限界の詳細・Q&A 言い換え: [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md)  
設計判断・トレードオフ: [ADR.md](ADR.md)  
発表素材: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)

**ローカル起動**:

```bash
pip install -r requirements.txt && pip install -e ".[dev]"
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
pytest   # 34 tests
```
