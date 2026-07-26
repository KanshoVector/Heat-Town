# heat-town — 都市熱環境における意思決定支援モデル

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

**heat-town** は、オープンデータと説明可能な多目的評価モデル `Jᵢ` により、都市の熱環境における「どこが暑く危険か」をデータで可視化し、意思決定を支援する大学データサイエンス PBL 向け OSS プロジェクトである。2〜3 日・6 人で完遂可能なスコープ。

> **Web アプリ開発ではない。** 主役は **社会課題 → データ → 分析 → 提言** であり、MVP は分析結果を体験する PoC（地図ビューア）である。初めての人は [START.md](START.md)（1 分）へ。

## アプリ概要

都市の暑さリスクは、気温だけでは説明できない。緑地・日陰までの**距離**、日射や風による**快適度**、そして**暑さ指数（WBGT）** が複合して、その場所の危険度が決まる。heat-town は、この3要素を1つの評価値 `Jᵢ` に統合し、対象エリアを格子状の評価点に分けて地図上で可視化する。

- **入力**: 気象データ（Open-Meteo 相当）、POI（OpenStreetMap の公園・街路樹・建物）、評価グリッド
- **処理**: WBGT 推定・快適度 C（緑・日陰・風）・正規化距離 d（基準点 origin から）を算出し、`Jᵢ` を計算
- **出力**: 各地点の `Jᵢ` と寄与3項を GeoJSON 化し、Leaflet 地図に色分け表示
- **操作**: 重みスライダーとペルソナ別プリセット（一般・高齢者・通勤・猛暑日）で、その場で優先順位の変化を確認できる

ブラックボックスを使わず線形モデルで**寄与を分解して見せる**ため、なぜその地点が危険なのかを行政・市民・都市計画者に説明できる。

## Social Challenge

都市部では **距離（緑・日陰へのアクセス）・快適度・暑さ（WBGT）** が複合し、熱中症リスクと外出判断に影響する。単一の気温マップでは、行政・市民・都市計画者への **説明可能な優先介入** ができない。

## Decision Model

各候補地点 *i* の評価値を次式で定義する。

```text
Jᵢ = w₁·dᵢ + w₂·(100 − Cᵢ) + w₃·WBGTᵢ
```

| 記号 | 説明 |
|------|------|
| `Jᵢ` | 候補地点 *i* の総合評価値（小さいほど望ましい） |
| `dᵢ` | 正規化した距離（0〜1） |
| `Cᵢ` | 快適度（0〜100） |
| `100 − Cᵢ` | 不快度 |
| `WBGTᵢ` | 暑さ指数（Wet Bulb Globe Temperature） |
| `w₁, w₂, w₃` | 各評価項目の重み（合計 1） |

> **評価値 `Jᵢ` が小さいほど望ましい地点である。** 重みはペルソナ（一般・高齢者・通勤・猛暑日）で変更可能。プリセットは [config/weights.yaml](config/weights.yaml)。

## Architecture

```mermaid
flowchart LR
    OD[Open Data] --> PY[Python Pipeline]
    PY --> GEO[GeoJSON]
    GEO --> POC[Leaflet PoC]
    POC --> VER[Vercel]
```

DuckDB / pandas による前処理と静的 PoC。デプロイは Vercel の GitHub 連携（main merge → 自動デプロイ）。

## Quick Start

```bash
git clone https://github.com/KanshoVector/Heat-Town.git
cd Heat-Town
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# サンプルデータ生成 → 前処理 → スコア出力までを一括実行
python -m heat_town.cli pipeline --sample

# 地図 PoC を表示
cd mvp/public && python -m http.server 8080   # http://localhost:8080
```

> **重要：サンプルデータは各自で生成してください。**
> `data/samples/` と `mvp/public/data/scores.geojson` は再生成可能なため Git 管理外です。
> クローン直後は空なので、**必ず一度 `python -m heat_town.cli pipeline --sample` を実行**してください（内部で `python -m heat_town.samples` が走り、weather / poi / grid のサンプルが作られます）。分析ノートや地図はこのデータを前提にしています。

## パイプライン構成

| ステップ | モジュール | 出力 |
|----------|-----------|------|
| データ生成 | `heat_town.samples` | `data/samples/`（weather / poi / grid） |
| 取得 CLI | `heat_town.cli` | `fetch-weather` / `fetch-poi` / `build-grid` / `pipeline` |
| 前処理 | `heat_town.preprocess` | `data/processed/features.parquet` |
| スコア出力 | `heat_town.export` | `mvp/public/data/scores.geojson` |
| 可視化 | `mvp/public/`（Leaflet） | 地図・寄与 popup・重みスライダー |
| 分析 | `notebooks/01`〜`05` | データ品質・EDA・仮説検証・感度分析・図 |

## 発表想定 Q&A

発表時に想定される質問と回答の要点。

1. **なぜ気温マップではダメなのか？**
   気温は暑さの一因に過ぎない。実際の危険度は、逃げ込める緑地・日陰までの距離や、風・日射による快適度にも左右される。heat-town はそれらを1つの指標に統合し、単一気温では見えない「複合的に危ない地点」を示す。

2. **`Jᵢ` の重み `w₁, w₂, w₃` はどう決めたのか？**
   固定値ではなく、ペルソナ別プリセット（一般・高齢者・通勤・猛暑日）として `config/weights.yaml` に定義。合計1に正規化して用いる。利用者が地図上のスライダーで動かして順位変化を確認できる。

3. **WBGT は公式の観測値か？**
   いいえ。気温と湿度から推定式で算出した近似値であり、公式観測ではない。そのため絶対値ではなく地点間の**相対比較**に用いる（[docs/data.md](docs/data.md) に明記）。

4. **なぜニューラルネットなどを使わないのか？**
   説明可能性を最優先したため。線形モデルなら各地点で「距離・不快・暑さ」の寄与を分解して提示でき、行政や市民に根拠を説明できる。予測精度より意思決定支援を重視した設計判断。

5. **データの信頼性・ライセンスは？**
   Open-Meteo（気象）と OpenStreetMap（ODbL、© OpenStreetMap contributors）を使用。個人情報を含む GPS 等は使わず、公開 POI のみ。帰属は [data/README.md](data/README.md) に記載。

6. **`Jᵢ` が低い＝安全、で本当に良いのか（因果の主張は？）**
   `Jᵢ` は優先順位づけの指標であり、因果関係を主張するものではない。あくまで「相対的に望ましい／注意すべき地点」を示す点評価であることを限界として明示している。

7. **対象エリアと評価点はどれくらいか？**
   大学近傍 2km 四方を 100m 間隔の格子に分割（約400点）。設定は [config/area.yaml](config/area.yaml)。エリアや粒度は config で変更可能。

8. **スケールしたときの性能は？**
   PoC はクライアント側で `Jᵢ` を再計算するため、重み変更は即座に反映される（点数が数千規模までは実用的）。それ以上は事前計算・タイル化などの拡張余地がある。

9. **リアルタイムの気象には対応しているか？**
   現状の PoC は静的 GeoJSON による分析結果ビューア。リアルタイム API 連携は本番アプリの領域として設計上分離している（[docs/mvp.md](docs/mvp.md)）。

10. **この分析から具体的にどんな提言ができるのか？**
    高 `Jᵢ` 地点への緑化・日陰（クールスポット）の重点整備、高齢者向けプリセットで浮かぶ地点の優先的対策、猛暑日プリセットでの外出注意喚起など。詳細は [docs/social-proposals.md](docs/social-proposals.md)。

## Repository Structure

```
heat-town/
├── START.md                    # 入口（1 分）
├── README.md                   # プロジェクト概要・使い方・想定 Q&A
├── CONTRIBUTING.md             # 開発ルール
├── LICENSE                     # MIT
├── pyproject.toml              # パッケージ設定・依存
├── requirements.txt            # 基本依存
├── config/                     # 設定ファイル
│   ├── weights.yaml            #   ペルソナ別の重みプリセット
│   ├── area.yaml               #   対象エリア（2km 四方・格子間隔）
│   └── origin.yaml             #   距離 d の基準点
├── src/heat_town/              # Python パッケージ
│   ├── samples.py              #   サンプルデータ生成
│   ├── cli.py                  #   fetch-weather / fetch-poi / build-grid / pipeline
│   ├── preprocess.py           #   WBGT・快適度・距離 → features.parquet
│   ├── model.py                #   Jᵢ 計算・重み正規化・寄与分解
│   └── export.py               #   features → scores.geojson
├── notebooks/                  # 分析ノートブック
│   ├── 01_data_quality.ipynb   #   データ品質チェック
│   ├── 02_feature_eda.ipynb    #   特徴量 EDA
│   ├── 03_ji_analysis.ipynb    #   仮説 H1–H4 検証
│   ├── 04_sensitivity.ipynb    #   重み感度分析・順位変動
│   └── 05_export_figures.ipynb #   発表用の図を出力
├── mvp/public/                 # Leaflet PoC（地図ビューア）
│   ├── index.html              #   地図・サイドバー UI
│   ├── js/app.js               #   色分け・寄与 popup・重みスライダー
│   └── data/scores.geojson     #   ← 各自生成（Git 管理外）
├── data/                       # データ
│   ├── samples/                #   サンプル（各自生成・Git 管理外）
│   └── processed/              #   features.parquet（Git 管理外）
├── tests/                      # pytest（model / cli / preprocess / export）
├── docs/                       # 設計ドキュメント（参考）
└── .github/workflows/          # CI（lint, test）
```

## License

[MIT License](LICENSE)