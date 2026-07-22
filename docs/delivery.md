# 成果物ガイド（発表・レポート・チーム）

## 7 分発表

### 時間配分（420 秒）

| 秒 | 内容 | スライド |
|----|------|----------|
| 0–30 | タイトル | 1 |
| 30–90 | 社会課題 | 2 |
| 90–180 | データ | 3 |
| 180–270 | モデル \(J_i\) | 4 |
| 270–330 | 分析・デモ | 5 |
| 330–390 | 提言 | 6 |
| 390–420 | まとめ | 7 |

### 台本（抜粋）

**0:00** 「heat-town は距離・快適度・WBGT を統合し、どこを優先的に涼しくすべきか支援する PoC です。」

**3:00** 「\(J_i = w_1 d + w_2(100-C) + w_3 \text{WBGT}\)。線形なので寄与が見えます。」

**6:30** 「GitHub と Vercel URL を共有します。」

### 想定 Q&A

| 質問 | 回答 |
|------|------|
| なぜ ML しない？ | Explainability / PBL スコープ → [rejected-approaches.md](rejected-approaches.md) |
| WBGT 正確？ | 推定値。相対比較用 |

---

## 個人レポート

| 章 | 字数 | 必須 |
|----|------|------|
| はじめに | 300–400 | 社会課題 |
| データ | 500–700 | 担当工程 |
| モデル | 500–700 | \(J_i\) 解釈 |
| 分析 | 600–800 | 仮説 1 件以上 |
| 考察 | 500–700 | 限界 3 点 |
| 提言 | 400–600 | 2 件以上 |
| 合計 | 3000–4500 字 | — |

AI 利用は付録で開示。チーム doc の丸写し禁止。

---

## チームワークフロー

### 6 人役割

| 役割 | 担当 |
|------|------|
| PM | overview, 発表 |
| Data | [data.md](data.md) |
| Analysis ×2 | [analysis.md](analysis.md), notebooks |
| Model/Viz | [decision-model.md](decision-model.md), export |
| MVP/DevOps | [mvp.md](mvp.md), CI, Vercel |

### 2〜3 日スケジュール

| Day | 重点 | 成果物 |
|-----|------|--------|
| 1 | データ・モデル | features.parquet |
| 2 | 分析・PoC | scores.geojson, 提言 v1 |
| 3 | CI・発表 | Actions 緑, レポート |

### 成果物チェックリスト

- [ ] doc 用語・記号統一（[GLOSSARY.md](GLOSSARY.md)）
- [ ] `pytest` / CI 緑
- [ ] PoC 寄与 popup
- [ ] Vercel URL
- [ ] 7 分リハ 420 秒以内
- [ ] 個人レポート 6 本

コミュニケーション: GitHub Issues / PR（review 1 名以上）
