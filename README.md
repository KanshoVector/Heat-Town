# heat-town — 都市熱環境における意思決定支援モデル

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

**heat-town** は、オープンデータと説明可能な多目的評価モデル \(J_i\) により、都市熱環境における意思決定を支援する大学データサイエンス PBL 向け OSS プロジェクトである。2〜3 日・6 人で完遂可能なスコープ。

> **初めての人 → [START.md](START.md)（1 分）**  Web アプリ開発ではない。主役は **社会課題 → データ → 分析 → 提言**。MVP は分析結果を体験する PoC。

## Social Challenge

都市部では **距離（緑・日陰へのアクセス）・快適度・暑さ（WBGT）** が複合し、熱中症リスクと外出判断に影響する。単一の気温マップでは、行政・市民・都市計画者への **説明可能な優先介入** ができない。

## Decision Model

本研究では、各候補地点 *i* の評価値を次式で定義する。

```text
Jᵢ = w₁·dᵢ + w₂·(100 − Cᵢ) + w₃·WBGTᵢ
```

| 記号 | 説明 |
|------|------|
| `Jᵢ` | 候補地点 *i* の総合評価値（小さいほど望ましい） |
| `dᵢ` | 正規化した距離 |
| `Cᵢ` | 快適度（0〜100） |
| `100 − Cᵢ` | 不快度 |
| `WBGTᵢ` | 暑さ指数（Wet Bulb Globe Temperature） |
| `w₁, w₂, w₃` | 各評価項目の重み |

> **評価値 `Jᵢ` が小さいほど、避難先として望ましい地点である。**
>
> 重み (`w₁`, `w₂`, `w₃`) は利用者の属性（一般、高齢者、猛暑日など）に応じて変更可能である。

## Architecture

```mermaid
flowchart LR
    OD[Open Data] --> PY[Python Pipeline]
    PY --> GEO[GeoJSON]
    GEO --> POC[Leaflet PoC]
    POC --> VER[Vercel]
```

DuckDB + 静的 PoC。デプロイは Vercel GitHub 連携。

## Quick Start

```bash
git clone https://github.com/KanshoVector/Heat-Town.git
cd Heat-Town
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
cd mvp/public && python -m http.server 8080
```

## はじめ方

**[START.md](START.md)** → 担当フォルダの README だけ読んで着手。`docs/` は設計済みの参考（読む必要なし）。

## Repository Structure

```
heat-town/
├── START.md              # 入口（1 分）
├── data/ notebooks/ src/ mvp/   # 各 README が作業手順
├── docs/                 # 設計参考（熟読不要）
└── .github/workflows/    # 発起人が手動実行するだけ
```

## License

[MIT License](LICENSE)
