# はじめに（1 分）

**heat-town** = 暑い街で「どこが危ないか」をデータで示す PBL。Web アプリ開発ではない。

## フォルダを選んで README を読む

| やること | フォルダ | README |
|----------|----------|--------|
| データを取って整える | `data/` + `src/` | [data/README.md](data/README.md) |
| 分析・図を作る | `notebooks/` | [notebooks/README.md](notebooks/README.md) |
| 式 \(J_i\) と GeoJSON 出力 | `src/` | [src/README.md](src/README.md) |
| 地図で見せる PoC | `mvp/` | [mvp/README.md](mvp/README.md) |

**6 人の目安**: データ 1 + 分析 2 + モデル出力 1 + 地図 1 + 残りは手伝い。  
発表・スライドは発起人。`docs/` は読まなくていい（設計済みの参考置き場）。

## セットアップ（全員・コピペ）

```bash
git clone https://github.com/KanshoVector/Heat-Town.git && cd Heat-Town
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e ".[dev]"
```

## ルール 3 つ

1. **`main` に直接 push しない** → ブランチ → PR
2. **`.env` / `.venv` は commit しない**
3. **動けば正義** — pytest / Lint / CI は気にしない

詳細: [CONTRIBUTING.md](CONTRIBUTING.md)
