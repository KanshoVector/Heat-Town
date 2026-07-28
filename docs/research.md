# 理論背景と授業対応

## 都市熱環境（UHI）の基礎

**都市ヒートアイランド（UHI）** は都市部の気温が周辺より高くなる現象。本 PoC では UHI を直接モデル化せず、**WBGT・快適度・距離** を統合する（[GLOSSARY.md](GLOSSARY.md)）。

| 要因 | データ proxy |
|------|--------------|
| 不浸透面 | 土地利用 / 舗装率 |
| 人工排熱 | 人口・道路密度 |
| 緑不足 | 公園 POI、NDVI（拡張） |

## 暑さ指数 — WBGT

\[
\text{WBGT} \approx 0.735 T + 0.0375 RH + 0.00292 T \cdot RH + 7.85
\]

| WBGT（℃） | 目安 |
|-----------|------|
| 25–28 | 警戒 |
| 28–31 | 厳重警戒 |
| 31 以上 | 危険 |

\(J_i\) 第 3 項: \(w_3 \cdot \text{WBGT}\)

## 快適度（C）と距離（d）

\[
C_i = \alpha C_{\text{shade}} + \beta C_{\text{green}} + \gamma C_{\text{wind}}, \quad d_i = \frac{\text{dist}(origin, i)}{d_{\max}}
\]

\(J_i\) では \(100 - C_i\)（不快度）を使用。詳細は [data.md](data.md)。

## 本プロジェクトの位置づけ

説明可能性を最優先し、2〜3 日・6 人で完遂可能な PBL 向け MVP。予測精度競争ではなく **意思決定支援** が評価軸。

---

## PBL 要件チェックリスト

| 授業要件 | 対応 |
|----------|------|
| 5–6 分発表 | [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md) |
| 個人レポート | [delivery.md](delivery.md) |
| 社会課題 | [social-challenge.md](social-challenge.md) |
| MVP で十分 | [mvp.md](mvp.md) |
| 分析・考察・提言 | [analysis.md](analysis.md), [social-proposals.md](social-proposals.md) |

## データサイエンス工程との対応

| 工程 | 実装 | ドキュメント |
|------|------|--------------|
| データ収集 | サンプル（将来 Open-Meteo/OSM） | [data.md](data.md) |
| 前処理 | pandas + haversine | [data.md](data.md) |
| 特徴量 | \(d, C, WBGT\) | [data.md](data.md) |
| 意思決定モデル | \(J_i\) | [decision-model.md](decision-model.md) |
| 分析・可視化 | 感度分析 + Leaflet | [analysis.md](analysis.md) |
| 社会提言 | P1–P9 | [social-proposals.md](social-proposals.md) |

## 評価観点

| 観点 | 個人レポートでの期待 |
|------|----------------------|
| 分析 | 仮説検証の過程 |
| 考察 | 限界・バイアス（WBGT 推定、POI 欠損） |
| 提言 | 実行可能な施策と \(J_i\) 根拠 |

## アイデアの差別化

| 一般的 PBL | heat-town |
|------------|-----------|
| 気温マップのみ | 距離・快適・WBGT の多目的統合 |
| 精度競争 | Explainability First |
| アプリありき | 分析 → PoC → 提言 |
