# heat-town セッション引き継ぎ

> **最終更新**: 2026-07-28 · 正本: [PROJECT.md](PROJECT.md)

## 状態: 完成

- pytest **34 passed**
- Primary UX（Top 3 + Maps）+ Secondary（分析モード）+ Playground
- GitHub Pages 本番 / Vercel 代替
- 発表: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)

## クイック起動

```bash
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
# → http://localhost:8080/?demo=1
pytest
```

*Show destinations, not datasets.*
