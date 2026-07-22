# プロジェクト概要

**heat-town** は、都市熱環境という社会課題に対し、オープンデータと説明可能な多目的評価モデル \(J_i\) で意思決定を支援する、大学データサイエンス PBL 向け OSS プロジェクトである。

> 設計フェーズの参考 doc。**着手時は読まない。** [START.md](../../START.md) と各フォルダ README を使う。

## 目的

| 観点 | 内容 |
|------|------|
| 社会 | 暑さリスクの高い地点を説明可能に特定し、行政・市民・都市計画の優先判断を支援する |
| 学術 | データ収集 → 前処理 → 特徴量 → モデル → 分析 → 可視化 → 考察 → 提言 の PBL 完遂 |
| 技術 | GitHub 公開可能な再現パイプライン + PoC（MVP） |

**本研究は Web アプリ開発ではない**。主役はデータサイエンスと社会提言である。

## 成果物

| 成果物 | 配置 | 評価での位置づけ |
|--------|------|------------------|
| プロジェクトドキュメント | `docs/` | 設計・分析・提言の根拠 |
| Python 分析パイプライン | `src/`, `notebooks/` | 再現性・分析 |
| MVP（PoC） | `mvp/` | 分析結果の体験（7 分デモ） |
| 7 分発表 | [delivery.md](../delivery.md) | 授業発表 |
| 個人レポート | [delivery.md](../delivery.md) | 個人評価 |
| 社会提言 | [social-proposals.md](../social-proposals.md) | 提言評価 |

## スコープ

**In Scope**

- Open-Meteo + OSM による \(d\), \(C\), WBGT
- 線形多目的モデル \(J_i = w_1 d + w_2(100-C) + w_3 \text{WBGT}\)
- Leaflet 静的 PoC
- Vercel 静的ホスト（GitHub 連携）

**Out of Scope**

- 本番 Web アプリ・認証・リアルタイム API
- ニューラルネット・予測モデル・FFT（[rejected-approaches.md](../rejected-approaches.md)）
- Actions からの CD（デプロイ）

対象エリア: **1 都市・1 区または大学近傍 2km 四方**。評価点 500–2000。

## 分担（6 人の目安）

仕事は **4 ブロック**。職種名ではなくフォルダで決める（[START.md](../../START.md) 参照）。

| ブロック | フォルダ | 人数目安 |
|----------|----------|----------|
| データ取得・前処理 | `data/`, `src/` cli | 1 |
| 分析 | `notebooks/` | 2 |
| モデル・GeoJSON 出力 | `src/` | 1 |
| 地図 PoC | `mvp/` | 1 |
| （余裕があれば） | 分析 or データを手伝う | 1 |

```mermaid
flowchart LR
    D[data/ src] --> N[notebooks/]
    D --> S[src/ model export]
    S --> M[mvp/]
    N --> M
```

発表・スライドは発起人が担当。全員: 個人レポート（[delivery.md](../delivery.md)）。

## スケジュール（2〜3 日）

| Day | 午前 | 午後 | 夜 |
|-----|------|------|-----|
| **1** | キックオフ・セットアップ | データ取得・前処理 E2E | \(J_i\) 試算 |
| **2** | 仮説検証・感度分析 | GeoJSON + Leaflet 結合 | 社会提言ドラフト |
| **3** | Vercel 確認 | 個人レポート | main merge |

詳細チェックリスト: [delivery.md](../delivery.md#チームワークフロー)

## MVP の位置付け

| 区分 | MVP（本 PoC） | 本番アプリ |
|------|---------------|------------|
| 目的 | **分析結果を体験・説明** | 継続運用 |
| 実体 | Leaflet + 静的 GeoJSON ビューア | SaaS |
| 成功基準 | 7 分で \(J_i\) と寄与を説明できる | DAU / SLA |
| ホスト | Vercel（GitHub 連携） | 任意 |

MVP は分析パイプラインの **出力ビューア** に過ぎない。仕様: [mvp.md](../mvp.md)

## データサイエンスパイプライン

```mermaid
flowchart TD
    S[社会課題] --> DC[データ収集]
    DC --> PP[前処理]
    PP --> FE[特徴量設計]
    FE --> DM[意思決定モデル Ji]
    DM --> AN[分析]
    AN --> VZ[可視化]
    VZ --> RF[社会提言]
    VZ --> MVP[MVP PoC]
```

## 設計思想

Open Data First · OSS First · AI Assisted Development · Serverless First · MVP First · Explainability First · Reproducibility First

## 参考（読まなくていい）

着手は [START.md](../../START.md) → 各フォルダ README。以下は背景資料。

| ファイル | 内容 |
|----------|------|
| [GLOSSARY.md](../GLOSSARY.md) | 用語 |
| [social-challenge.md](../social-challenge.md) | 社会課題の背景 |
