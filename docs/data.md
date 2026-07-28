# データパイプライン

> 全体像: [PROJECT.md](PROJECT.md) · 用語: [GLOSSARY.md](GLOSSARY.md)

## 現状（PBL PoC）

**`pipeline --sample` のみ**。Open-Meteo / OSM 相当の **決定論的サンプル**（`samples.py`, seed=42）。  
実 API `--full` は未実装 → [ADR-004](adr/004-open-data-fetch-strategy.md)

```bash
python -m heat_town.cli pipeline --sample
# → data/samples/*, features.parquet, mvp/public/data/*.geojson
```

| 出力 | 内容 |
|------|------|
| `features.parquet` | 400 点 × d, C, WBGT |
| `scores.geojson` | 格子 + J_i + 寄与 |
| `rest_spots.geojson` | POI 32 点 + Top 3 メタ |

生成データは Git 管理外 → [ADR-003](adr/003-generated-data-not-in-git.md)

## 前処理（`preprocess.py`）

- **pandas + numpy**（DuckDB 未使用 → [ADR-006](adr/006-pandas-preprocess-over-duckdb.md)）
- origin: `config/origin.yaml`（有明、d_max=1500m）
- 距離: Haversine（WGS84）
- 固定時刻: hour=15

## 特徴量

### 距離 d（格子）

\[
d_i = \text{clip}(\text{haversine}(origin, i) / d_{\max}, 0, 1)
\]

### 快適度 C（格子）

最寄り POI 距離 + 風速:

\[
C_i = \text{clip}(0.4 \cdot c_{\text{shade}} + 0.4 \cdot c_{\text{green}} + 0.2 \cdot c_{\text{wind}}, 0, 100)
\]

kind は格子前処理では無視。涼み場ランキングのみ kind 別 C（`rest_finder.py`）。

### WBGT

\[
\text{WBGT} = 0.735 T + 0.0375 RH + 0.00292 T \cdot RH + 7.85
\]

全格子同一値。推定式 — 相対比較用。

## 将来（Phase 2）

Open-Meteo / OSM `--full` + `data/raw/` キャッシュ。詳細: [data/README.md](../data/README.md)
