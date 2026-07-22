# ソースコード（`src/`）

**式 \(J_i\) を計算して GeoJSON を出す人** が触る。

\[
J_i = w_1 \cdot d_i + w_2 \cdot (100 - C_i) + w_3 \cdot \text{WBGT}_i
\]

低い \(J_i\) = より望ましい地点。`model.py` に実装済み。

## 最初の 3 ステップ

```bash
source .venv/bin/activate          # 未作成なら START.md
python -c "from heat_town.model import compute_ji; print('OK')"
# 担当に応じて cli / preprocess / export を実装（下表）
```

## ファイルと作業

| ファイル | やること |
|----------|----------|
| `heat_town/model.py` | \(J_i\) 計算・寄与分解（済） |
| `cli.py`（未実装） | `fetch-weather`, `pipeline --sample` など |
| `preprocess.py`（未実装） | parquet 整形 |
| `export.py`（未実装） | `mvp/public/data/scores.geojson` 出力 |

データ取得の詳細は [data/README.md](../data/README.md)。

## 完了の目安

- `features.parquet` を読んで `scores.geojson` が出る
- 地図担当が [mvp/README.md](../mvp/README.md) で表示できる
