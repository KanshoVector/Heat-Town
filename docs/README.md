# ドキュメント

heat-town の全ドキュメント索引。**実装フェーズの SSoT は本リポジトリ**（設計追加は行わない）。

## ドキュメント一覧

| ファイル | 内容 |
|----------|------|
| [00-project/overview.md](00-project/overview.md) | **最初に読む** — 概要・目的・チーム・スケジュール |
| [GLOSSARY.md](GLOSSARY.md) | 用語集 |
| [social-challenge.md](social-challenge.md) | 社会課題 |
| [research.md](research.md) | 理論背景・授業対応 |
| [data.md](data.md) | 収集・前処理・特徴量 |
| [decision-model.md](decision-model.md) | 意思決定モデル \(J_i\) |
| [rejected-approaches.md](rejected-approaches.md) | 不採用技術 |
| [analysis.md](analysis.md) | 分析・可視化 |
| [mvp.md](mvp.md) | MVP 仕様・アーキテクチャ |
| [social-proposals.md](social-proposals.md) | 社会提言 |
| [delivery.md](delivery.md) | 発表・レポート・チーム |
| [operations.md](operations.md) | 技術・再現性・CI/CD・デプロイ |

## 初めて読む人

```mermaid
flowchart LR
    A[overview] --> B[GLOSSARY]
    B --> C[social-challenge]
    C --> D[research]
    D --> E[担当 doc へ]
```

| 順 | ファイル | 目安 |
|----|----------|------|
| 1 | [00-project/overview.md](00-project/overview.md) | 10 min |
| 2 | [GLOSSARY.md](GLOSSARY.md) | 5 min |
| 3 | [social-challenge.md](social-challenge.md) | 10 min |
| 4 | [research.md](research.md) | 15 min |
| 5 | [mvp.md](mvp.md) § MVP の位置付け | 5 min |

## 開発者

| 順 | ファイル | 実装参照 |
|----|----------|----------|
| 1 | [overview.md](00-project/overview.md) | スコープ |
| 2 | [data.md](data.md) | `src/`, `data/` |
| 3 | [decision-model.md](decision-model.md) | `src/heat_town/model.py` |
| 4 | [analysis.md](analysis.md) | `notebooks/` |
| 5 | [mvp.md](mvp.md) | `mvp/` |
| 6 | [operations.md](operations.md) | CI, Vercel |
| 7 | [CONTRIBUTING.md](../CONTRIBUTING.md) | GitHub Flow |

**並列開発の境界**

| 担当 | 触る doc | 触るコード |
|------|----------|------------|
| Data | data.md | `src/` fetch, preprocess |
| Analysis | analysis.md | `notebooks/` |
| Model/Viz | decision-model.md | `model.py`, export |
| MVP | mvp.md | `mvp/` |

## 発表担当

| 順 | ファイル |
|----|----------|
| 1 | [delivery.md](delivery.md) § 7 分発表 |
| 2 | [social-proposals.md](social-proposals.md) |
| 3 | [decision-model.md](decision-model.md) |
| 4 | [mvp.md](mvp.md) — デモ手順 |

## 教員

| 順 | ファイル | 確認点 |
|----|----------|--------|
| 1 | [overview.md](00-project/overview.md) | 目的・スコープ |
| 2 | [research.md](research.md) | 授業対応 |
| 3 | [social-proposals.md](social-proposals.md) | 提言 |
| 4 | [delivery.md](delivery.md) | 評価 Rubric |
| 5 | [rejected-approaches.md](rejected-approaches.md) | 技術判断 |

## 更新ルール

- 用語は [GLOSSARY.md](GLOSSARY.md) に従い横断統一
- 実装変更は doc を同一 PR で更新
- 構成の増減は禁止（責務整理のみ）
