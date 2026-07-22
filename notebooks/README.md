# 分析（`notebooks/`）

**データを読んで仮説検証・図を作る人** が触る。2 人なら 01–03 と 04–05 で分ける。

## 最初の 3 ステップ

```bash
source .venv/bin/activate && pip install -e ".[dev]"
jupyter lab
# 01_data_quality.ipynb を開き、samples が読めるか確認
```

## ノートブック一覧

| # | ファイル | やること |
|---|----------|----------|
| 1 | `01_data_quality.ipynb` | 欠損率・データ確認 |
| 2 | `02_feature_eda.ipynb` | 分布・EDA |
| 3 | `03_ji_analysis.ipynb` | 仮説 H1–H4 検証 |
| 4 | `04_sensitivity.ipynb` | 重みを変えた順位変化 |
| 5 | `05_export_figures.ipynb` | 発表用の図を `reports/figures/` へ |

## 検証する仮説（03 で使う）

| ID | 仮説 |
|----|------|
| H1 | 緑重視（\(w_2\)↑）で緑地周辺の順位が上がる |
| H2 | 15 時の \(J_i\) が 8 時より大きい |
| H3 | POI 欠損区域では \(C\) の分散が小さい |
| H4 | 猛暑日プリセットで WBGT 寄与が増える |

## 完了の目安

- 03 で仮説が 1 件以上検証されている
- 05 で図が出ている
