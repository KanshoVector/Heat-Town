# 分析ノートブック

| # | ノートブック | 入力 | 出力 |
|---|--------------|------|------|
| 1 | `01_data_quality.ipynb` | samples | 欠損率表 |
| 2 | `02_feature_eda.ipynb` | features.parquet | 分布図 |
| 3 | `03_ji_analysis.ipynb` | features + weights | 仮説 H1–H4 |
| 4 | `04_sensitivity.ipynb` | features | Kendall τ |
| 5 | `05_export_figures.ipynb` | 上記 | `reports/figures/` |

```bash
pip install -e ".[dev]"
jupyter lab
```

計画: [docs/analysis.md](../docs/analysis.md)
