# データ（`data/`）

**外部データを取って parquet / geojson に整える人** が触る。

## 最初の 3 ステップ

```bash
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
ls data/samples/weather data/samples/poi data/samples/grid
ls data/processed/features.parquet mvp/public/data/scores.geojson
```

## データの出どころ

| データ | 取得元 | 置き場 |
|--------|--------|--------|
| 気象・WBGT 推定 | Open-Meteo API | `samples/weather/` |
| POI（緑・日陰） | OSM Overpass | `samples/poi/` |
| 評価グリッド | 内部生成 | `samples/grid/` |

対象エリア: **大学近傍 2km 四方**（`config/area.yaml` 参照）。  
WBGT は気象から **推定** した値（公式観測ではない）。

## ディレクトリ

```
data/
├── samples/      # .gitignore — 各自 pipeline --sample で生成
├── raw/          # .gitignore — フル取得用（将来）
└── processed/    # .gitignore — features.parquet
```

`mvp/public/data/scores.geojson` も Git 管理外。クローン直後は **必ず pipeline を 1 回実行** する。

## パイプライン

```bash
python -m heat_town.cli fetch-weather --sample
python -m heat_town.cli fetch-poi --sample
python -m heat_town.cli build-grid
python -m heat_town.cli pipeline --sample
```

`--full`（実 API 取得）は未実装。方針は [docs/adr/004-open-data-fetch-strategy.md](../docs/adr/004-open-data-fetch-strategy.md)。

## 完了の目安

- `data/processed/features.parquet` と `mvp/public/data/scores.geojson` がある
- 下表のライセンス帰属を守っている

## ライセンス

| データ | ライセンス | 帰属 |
|--------|------------|------|
| Open-Meteo | [API Terms](https://open-meteo.com/en/terms)（データ CC BY 4.0） | Open-Meteo |
| OpenStreetMap | ODbL 1.0 | © OpenStreetMap contributors |
| 生成データ | MIT（本 repo） | heat-town |
