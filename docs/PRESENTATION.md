# heat-town プレゼンガイド（7 分デモ）

> 発表者向け。詳細 spec は [mvp.md](mvp.md)、モデルは [decision-model.md](decision-model.md)。

## 1. オープニング（30 秒）

- **社会課題**: 都市部の熱中症 — 気温だけでは説明できない（距離・快適度・WBGT）
- **heat-town の答え**: 説明可能な線形モデル Jᵢ + **現場向け「近くの涼み場」UX**

## 2. デモ Part A — 休憩モード（2 分）★ メイン

1. `python -m heat_town.cli pipeline --sample` 済みの地図を開く
2. **WBGT バナー**を指差し — 今日の暑さレベル
3. **「📍 現在地から一番近い涼み場を探す」** をタップ
4. Top 3 カード — 名称・種別・徒歩分数・快適度
5. **「🧭 Google Maps でナビ起動」** — 2 タップで現場 JTBD 完走

> **キーメッセージ**: *Show destinations, not datasets.* 格子 400 個はデータ、涼み場 3 つがプロダクト。

## 3. デモ Part B — 分析モード（3 分）

1. 下部 **「📊 モデル検証・分析モード」** を展開
2. **400 点格子 ON** — Jᵢ 色分けヒートマップ
3. **ペルソナ切替**（高齢者 / 猛暑日）— 順位が変わることを実演
4. popup で **寄与 3 項**（距離・不快・暑さ）を説明
5. **危険点 Top 10** — 行政向け優先介入候補

## 4. モデル説明（1 分）

```text
Jᵢ = w₁·d + w₂·(100−C) + w₃·WBGT
```

- 線形 → 寄与分解可能（ADR-001）
- POI ランキングでも同じ Jᵢ を再利用（ADR-007）
- 重みはペルソナ別 — 説明可能性 First

## 5. 提言・限界（30 秒）

- **提言**: 高 Jᵢ 区域への緑化・街路樹（[social-proposals.md](social-proposals.md) P1–P9）
- **限界**: WBGT は推定値、因果ではなく優先順位づけ、POI 密度依存
- **将来**: 日陰ルーティング（ShadeRoute 等）は Phase 3

## 6. 想定 Q&A

| 質問 | 回答の要点 |
|------|-----------|
| なぜ ML ではない？ | 説明可能性。寄与を見せられる |
| 400 点は何？ | 分析用格子。現場 UX は POI Top 3 |
| データは本物？ | Open-Meteo / OSM 相当のサンプル。各自 pipeline で生成 |
| すずみばとの違い？ | Jᵢ モデルで「なぜそこが涼しいか」を説明できる |

## 7. 起動チェックリスト

```bash
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
# → http://localhost:8080
pytest   # 全テスト green 確認
```

---

*参照: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md) | [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md) | [delivery.md](delivery.md)*
