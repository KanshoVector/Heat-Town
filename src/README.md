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
python -m heat_town.cli pipeline --sample
```

## ファイルと作業

| ファイル | やること |
|----------|----------|
| `heat_town/model.py` | \(J_i\) 計算・寄与分解（済） |
| `heat_town/cli.py` | `fetch-weather`, `pipeline --sample` など（済） |
| `heat_town/preprocess.py` | samples → `features.parquet`（済） |
| `heat_town/export.py` | GeoJSON 出力（済） |
| `heat_town/rest_finder.py` | 涼み場 Top-k ランキング（済） |
| `heat_town/samples.py` | 決定論的サンプル生成（済） |

`d` は **origin（基準点）からの正規化距離**。緑・日陰の近さは快適度 \(C\) に反映される。

詳細: [docs/PROJECT.md](../docs/PROJECT.md)

## 完了の目安

- `features.parquet` を読んで `scores.geojson` が出る
- 地図担当が [mvp/README.md](../mvp/README.md) で表示できる
