# heat-town セッション引き継ぎ

> **最終更新**: 2026-07-27 — **最終完成**  
> 短版: [HANDOFF.md](HANDOFF.md)

---

## 状態: 完成

- pytest **33 passed**
- Primary UX（涼み場 Top 3 + Maps）+ Secondary（分析モード）+ Playground
- Vercel ビルド / デモガード / Google Maps 起点固定
- プレゼン: [SLIDE_DECK_MATERIALS.md](SLIDE_DECK_MATERIALS.md)
- 限界: [CRITICAL_REVIEW.md](CRITICAL_REVIEW.md)

---

## クイック起動

```bash
source .venv/bin/activate
python -m heat_town.cli pipeline --sample
cd mvp/public && python -m http.server 8080
# → http://localhost:8080/?demo=1
pytest
```

---

*Show destinations, not datasets.*
