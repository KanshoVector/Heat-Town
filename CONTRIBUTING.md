# 開発のしかた

**動けば正義。** Lint・テスト・CI で悩まない。担当フォルダの README だけ見て着手する。

## Git（これだけ）

1. `main` からブランチを切る（例: `feat/data-fetch`）
2. 変更 → commit → push
3. PR を出す → 誰か 1 人に見てもらって merge

```bash
git checkout -b feat/自分の作業
git add .
git commit -m "feat: やったこと"
git push -u origin feat/自分の作業
```

## 禁止

- `main` への直接 push
- `.env` / `.venv` / 個人情報の commit
- `data/raw/` の commit（`data/samples/` のみ OK）

## セットアップ

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e ".[dev]"
```

## CI について

`.github/workflows/` は **発起人が必要なときだけ手動実行** する。PR を止めない。学生が `pytest` や `ruff` を回す必要はない。

## AI を使ったとき

PR 説明にツール名と用途を 1 行書く。数式・ライセンスは人間が確認。
