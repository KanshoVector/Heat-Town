# データ（`data/`）

**外部データを取って parquet / geojson に整える人** が触る。

## 最初の 3 ステップ

```bash
source .venv/bin/activate
ls data/samples/weather data/samples/poi data/samples/grid
# cli 実装前は samples/ をそのまま使って OK
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
├── samples/      # Git 管理 — 最初はここだけ触る
├── raw/          # .gitignore — フル取得用
└── processed/    # パイプライン出力 → features.parquet
```

## パイプライン（cli 実装後）

```bash
python -m src.cli fetch-weather --full
python -m src.cli fetch-poi --full
python -m src.cli build-grid
python -m src.cli pipeline --sample   # samples のみ
```

## 完了の目安

- `data/processed/features.parquet` がある（または samples で分析が回る）
- 下表のライセンス帰属を守っている

## ライセンス

| データ | ライセンス | 帰属 |
|--------|------------|------|
| Open-Meteo | [API Terms](https://open-meteo.com/en/terms) | Open-Meteo |
| OpenStreetMap | ODbL 1.0 | © OpenStreetMap contributors |
| 生成データ | MIT（本 repo） | heat-town |
