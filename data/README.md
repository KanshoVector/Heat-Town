# データ（`data/`）

**現状**: `samples.py` による決定論的サンプル（Open-Meteo/OSM **相当**）。実 API は Phase 2。

詳細: [docs/PROJECT.md](../docs/PROJECT.md) · [docs/data.md](../docs/data.md)

## 最初の 3 ステップ

```bash
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
ls data/processed/features.parquet mvp/public/data/scores.geojson
```

## サンプル内容

| データ | 点数/件数 | 生成 |
|--------|-----------|------|
| 気象 | 24h CSV | 真夏日パターン（hour=15 を使用） |
| POI | 32 点 | 公園6・樹18・ビル影8 |
| グリッド | 400 点 | 2km 四方 · 100m 間隔 |

## ディレクトリ（すべて .gitignore）

```
data/samples/     pipeline --sample で生成
data/processed/   features.parquet
mvp/public/data/  scores.geojson, rest_spots.geojson
```

## 将来

`fetch-weather --full` / `fetch-poi --full` → [ADR-004](../docs/adr/004-open-data-fetch-strategy.md)

## ライセンス（実 API 利用時）

| ソース | ライセンス |
|--------|------------|
| Open-Meteo | CC BY 4.0 |
| OpenStreetMap | ODbL 1.0 |
