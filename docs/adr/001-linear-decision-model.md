# ADR-001: 線形多目的モデル Jᵢ

**日付**: 2026-07-26  
**状態**: 採用

## 文脈

都市熱リスクを行政・市民に説明する PBL。予測精度より **Explainability First**。

## 決定

\[
J_i = w_1 d_i + w_2 (100 - C_i) + w_3 \text{WBGT}_i
\]

線形和 + 重み正規化 + 寄与分解 popup。

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| 線形（採用） | 寄与可視化、スライダー即時反映 | 非線形相互作用を表現不可 |
| ML / NN（不採用） | 精度向上余地 | ブラックボックス、説明困難 |

## 結果

- `src/heat_town/model.py` が SSoT
- 重みプリセットは `config/weights.yaml` と MVP JS で一致

## 関連

- [decision-model.md](../decision-model.md)
- [rejected-approaches.md](../rejected-approaches.md)
