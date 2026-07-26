# ADR-004: Open-Meteo / OSM 取得方針（2026-07 時点）

**日付**: 2026-07-26  
**状態**: 採用  
**調査基準日**: 2026-07-26

## 文脈

PoC は Open Data First。PBL 期間中は **非商用・低頻度** 利用を想定。実 API `--full` は将来拡張。

## Open-Meteo（2026-07 最新）

出典: [Terms](https://open-meteo.com/en/terms), [Pricing](https://open-meteo.com/en/pricing)

| 項目 | 無料 API |
|------|----------|
| 用途 | **非商用のみ** |
| レート | 600/min, 5,000/h, **10,000/day**, 300,000/month |
| 認証 | 不要（GET JSON） |
| データライセンス | **CC BY 4.0**（帰属必須） |
| 商用 | Standard $29/月〜（専用 endpoint + API key） |
| Historical / Ensemble 等 | 無料 tier でも一部 API 利用可。商用大量は Professional $99/月〜 |

**実装方針（heat-town）**

1. PBL / 授業: `pipeline --sample`（決定論的生成、API 不要）
2. `--full` 実装時: 1 リクエストで bbox+variables をまとめ、キャッシュ `data/raw/`（gitignore）
3. 帰属: `data/README.md` + スライドに Open-Meteo CC BY 4.0
4. 大学 PBL = 非商用に該当する想定だが、**有料イベント・企業スポンサー展示は要確認**

## OpenStreetMap / Overpass（2026-07 最新）

出典: [Overpass doc](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html), [OSM Wiki](https://wiki.openstreetmap.org/wiki/Overpass_API), コミュニティ報告（2025–2026）

| 項目 | 公共 Overpass |
|------|----------------|
| 目安 | **~10,000 req/day**, **~1 GB/day** |
| 429/504 | クエリ過大・混雑時に頻発 |
| 2026 運用 | 主 instance 過負荷、**User-Agent / Referer 必須化**の方向、クラウド IP 制限事例 |
| 代替 | mirror（例: `overpass.kumi.systems` / `overpass.private.coffee`）、Geofabrik `.pbf` ローカル |

**実装方針（heat-town）**

1. PoC: サンプル POI（`samples.py`）
2. `--full` 実装時:
   - bbox を `config/area.yaml` に厳密化
   - `[timeout:60][maxsize:...]`、`out body`（meta 避ける）
   - **User-Agent: heat-town/0.1 (+contact)** 必須
   - 429 → `Retry-After` 尊重 + exponential backoff
   - 本番パイプラインは **Overpass 依存を避け `.pbf` + osmium/pyosmium** を推奨（レート限界回避）

## 決定

| フェーズ | 気象 | POI |
|----------|------|-----|
| 現在（PBL） | `--sample` | `--sample` |
| 次段 `--full` | Open-Meteo forecast/historical（1 call/bbox/day） | Overpass + キャッシュ、または `.pbf` |

## トレードオフ

最小リソースで最大結果 → **API を叩かず seed サンプルで全パイプラインを完走**し、デモは静的 GeoJSON。実データは「拡張」として ADR 更新後に追加。

## 関連

- [data.md](../data.md)
- [000-risks-register.md](000-risks-register.md) R-04–R-06
