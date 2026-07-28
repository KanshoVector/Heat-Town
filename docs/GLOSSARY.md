# 用語集（Glossary）

heat-town プロジェクトで使用する用語の定義。記号・略語は全 doc で本表に従う。

| 用語 | 英語 | 説明 |
|------|------|------|
| **WBGT** | Wet Bulb Globe Temperature | 暑さ指数（℃）。本 PoC では Open-Meteo の気温・湿度から **推定**（観測器値ではない）。\(J_i\) の第 3 項に使用。 |
| **UHI** | Urban Heat Island | 都市ヒートアイランド。都市部が非都市部より気温が高くなる現象。本 PoC では直接モデル化せず、WBGT・快適度で proxy。 |
| **Cooling Shelter** | — | 冷却・休憩スペース（給水所、クールスポット等）。提言 P1 で猛暑時間帯の一時拡充対象。 |
| **DuckDB** | — | 組込み OLAP DB。**PoC では未使用**（pandas 前処理。将来拡張 → ADR-006）。 |
| **Feature Engineering** | 特徴量設計 | ドメイン知識をモデル入力に数値化する工程。本 PoC では \(d\)（距離）、\(C\)（快適度）、WBGT。 |
| **Explainability** | 説明可能性 | モデル出力の根拠を人間が理解・説明できる性質。線形 \(J_i\) の寄与分解と PoC popup で実装。 |
| **MVP** | Minimum Viable Product | 本プロジェクトでは **分析を体験する最小 PoC** を指す。Web アプリ製品ではない。 |
| **PoC** | Proof of Concept | 涼み場 Top 3 + Maps ナビ（Primary）と 400 点分析モード（Secondary）の静的ビューア。 |
| **Open Data** | オープンデータ | 設計上 Open-Meteo/OSM。**現状は `samples.py` サンプル**（`--full` は Phase 2）。 |
| **OSS** | Open Source Software | MIT ライセンスで GitHub 公開。CONTRIBUTING.md に従い共同開発。 |
| **Decision Model** | 意思決定モデル | 地点 \(i\) の総合評価 \(J_i = w_1 d + w_2(100-C) + w_3 \text{WBGT}\)。**低いほど望ましい**。 |
| **Sensitivity Analysis** | 感度分析 | 重み \(w_1, w_2, w_3\) や時刻を変えたときの順位・寄与の変化を調べる分析。 |
| **Normalization** | 正規化 | スケールを揃える処理。例: \(d_i = \text{dist}/d_{\max}\) で 0–1 に正規化。重みは \(w_1+w_2+w_3=1\)。 |

## 記号一覧

| 記号 | 意味 |
|------|------|
| \(J_i\) | 地点 \(i\) の総合スコア（低い = 良い） |
| \(d_i\) | 正規化距離 [0, 1] |
| \(C_i\) | 快適度 [0, 100]（高い = 快適） |
| \(100 - C_i\) | 不快度（\(J_i\) への入力） |
| \(w_1, w_2, w_3\) | 距離・快適・暑さの重み（非負、合計 1） |

## 関連ドキュメント

| 用語 | 詳細 |
|------|------|
| WBGT, UHI, \(C\), \(d\) | [research.md](research.md) |
| Feature Engineering | [data.md](data.md) |
| Decision Model | [decision-model.md](decision-model.md) |
| Sensitivity Analysis | [analysis.md](analysis.md) |
| MVP / PoC | [PROJECT.md](PROJECT.md), [mvp.md](mvp.md) |
| Open Data / OSS | [operations.md](operations.md) |
