# 地図 PoC（`mvp/`）

**分析結果を Leaflet で見せる人** が触る。HTML + 静的 GeoJSON だけ。

## 最初の 3 ステップ

```bash
cd mvp/public && python -m http.server 8080
# http://localhost:8080 を開く
# data/scores.geojson を置き、地図に点が出るか確認
```

## 構成

```
mvp/public/
├── index.html
├── js/
└── data/scores.geojson   ← src/export の出力
```

## 最低限やること

1. GeoJSON を読み込んで地図に色分け表示
2. 地点クリック → popup に **寄与 3 行**（距離 / 不快 / 暑さ）
3. （余裕があれば）重みスライダー・`elderly` プリセット

## 完了の目安

- ローカルで地図 + popup が動く
- main merge 後、Vercel URL が開く（連携は発起人）
