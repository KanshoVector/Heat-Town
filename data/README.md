# データカタログ

## ディレクトリ構成

```
data/
├── README.md          # 本ファイル
├── samples/           # Git 管理 — CI / デモ用最小セット
│   ├── weather/
│   ├── poi/
│   └── grid/
├── raw/               # .gitignore — フル取得データ
│   ├── weather/
│   ├── poi/
│   └── grid/
└── processed/         # パイプライン出力
    ├── preprocessed.parquet
    └── features.parquet
```

## ファイル一覧と由来

| ファイル | 由来 | 更新頻度 |
|----------|------|----------|
| `samples/weather/*.parquet` | Open-Meteo（sample 日付） | 手動 |
| `samples/poi/*.geojson` | OSM Overpass（sample bbox） | 手動 |
| `samples/grid/points.parquet` | 内部生成 | 手動 |
| `processed/features.parquet` | `src/cli pipeline` | パイプライン実行時 |

## 再取得手順

```bash
# フル取得（対象 bbox は config/area.yaml）
python -m src.cli fetch-weather --full
python -m src.cli fetch-poi --full
python -m src.cli build-grid

# sample のみ（CI 同等）
python -m src.cli pipeline --sample
```

詳細: [docs/data.md](../docs/data.md)

## ライセンス

| データ | ライセンス | 帰属 |
|--------|------------|------|
| Open-Meteo | [API Terms](https://open-meteo.com/en/terms) | Open-Meteo |
| OpenStreetMap | ODbL 1.0 | © OpenStreetMap contributors |
| 生成データ（grid, features） | MIT（本 repo） | heat-town |

**注意**: WBGT は Open-Meteo 気象から **推定** した値であり、公式観測ではない。
