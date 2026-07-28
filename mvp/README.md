# 地図 PoC（`mvp/`）

**Rest-first UX**: 涼み場 Top 3 + Google Maps ナビ。分析モードは折りたたみ内。

詳細: [docs/PROJECT.md](../docs/PROJECT.md)

## 起動

```bash
python -m heat_town.cli pipeline --sample   # 初回必須
cd mvp/public && python -m http.server 8080
# http://localhost:8080/?demo=1
```

## 構成

```
mvp/public/
├── index.html
├── js/app.js
└── data/
    ├── scores.geojson      ← 400 点格子
    └── rest_spots.geojson  ← POI + Top 3
```

## 完了の目安

- [ ] Top 3 カード + Maps リンクが動く
- [ ] 分析モードで格子 + popup 寄与 3 項
- [ ] GitHub Pages URL が開く
