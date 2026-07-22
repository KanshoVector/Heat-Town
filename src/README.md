# ソースコード

Python 分析パイプライン。意思決定モデルは `heat_town.model` に実装。

## 構成

```
src/heat_town/
├── __init__.py
└── model.py          # Ji 計算・寄与分解・重み正規化
```

| モジュール | 責務 | ドキュメント |
|------------|------|--------------|
| `model.py` | \(J_i\), contributions | [decision-model.md](../docs/decision-model.md) |

## ローカル開発

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
ruff check src tests
pytest
```

## テスト

`tests/test_model.py` — \(J_i\) 計算、重み正規化、寄与分解。

CI: [.github/workflows/python.yml](../.github/workflows/python.yml)

## 今後追加（並列開発）

| モジュール | 担当 | doc |
|------------|------|-----|
| `cli.py` | Data | [data.md](../docs/data.md) |
| `preprocess.py` | Data | [data.md](../docs/data.md) |
| `export.py` | Model/Viz | [analysis.md](../docs/analysis.md) |
