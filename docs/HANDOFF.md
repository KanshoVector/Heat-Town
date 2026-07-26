# heat-town — 完成状態引き継ぎ

> **最終更新**: 2026-07-27（最終完成）  
> 詳細: [SESSION_HANDOFF.md](SESSION_HANDOFF.md)

---

## 完成済み機能

| 機能 | ファイル |
|------|----------|
| 涼み場 Top 3 + Maps ナビ | `mvp/public/js/app.js` |
| Google Maps 起点固定（デモ時） | `currentOrigin` + `updateNavOrigin` |
| Playground（地図クリック） | `playground-toggle` / `reset-ariake` |
| エリア外ガード | `rest_finder.resolve_user_location` |
| Vercel ビルド | `vercel.json` |
| プレゼン素材 | [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md) |
| PoC 限界一覧 | [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md) |

---

## あなたが触る手順

```bash
cd heat-town
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
```

| URL | 用途 |
|-----|------|
| http://localhost:8080/ | 通常 |
| http://localhost:8080/?demo=1 | **発表デモ（推奨）** |

```bash
pytest   # 33 passed 確認
```

---

## Vercel デプロイ

```bash
npm i -g vercel   # 初回のみ
vercel            # リポジトリルートで実行
# 本番 URL + ?demo=1 を QR 化 → Slide 4
```

---

## ドキュメント入口

| 誰向け | ファイル |
|--------|----------|
| 初めての人 | [README.md](../README.md) |
| 発表者 | [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md) |
| 開発者・批評 | [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md) |
| 設計判断 | [ADR.md](ADR.md) |
