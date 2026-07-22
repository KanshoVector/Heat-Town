# MVP（PoC）

分析結果を体験する静的ビューア。仕様: [docs/mvp.md](../docs/mvp.md)

## 構成

```
mvp/
├── public/
│   ├── index.html      # HTML+JS（デフォルト）
│   ├── js/
│   └── data/scores.geojson
└── package.json        # Next.js 採用時のみ
```

## ローカル起動

```bash
cd mvp/public && python -m http.server 8080
# Next.js 採用時: cd mvp && npm install && npm run dev
```

## デプロイ

Vercel GitHub 連携（Actions から deploy しない）— [docs/operations.md](../docs/operations.md)

## CI Build Check

`mvp/next.config.js` を追加すると CI が `npm run build` を実行する。
