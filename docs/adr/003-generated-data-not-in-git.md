# ADR-003: 生成データを Git 管理外にする

**日付**: 2026-07-26  
**状態**: 採用

## 文脈

- 再生成可能な artifacts を repo に載せると PR 衝突・容量増
- ライセンス混在リスク（OSM 派生物）

## 決定

`.gitignore` で除外:

- `data/samples/*`
- `data/processed/*`
- `mvp/public/data/*`

クローン後は **必ず** `python -m heat_town.cli pipeline --sample`。

## トレードオフ

| 選択 | 利点 | 欠点 |
|------|------|------|
| 生成物 ignore（採用） | クリーン repo、再現性は seed で担保 | 初回 1 コマンド必須 |
| samples commit（旧 docs 記載） | 即 notebook 実行 | 更新 PR が肥大化 |

## 結果

- `data/README.md` / `README.md` を SSoT に統一
- 旧 `docs/operations.md` の「samples コミット」記述は本 ADR と矛盾 → operations 更新推奨

## 関連

- [000-risks-register.md](000-risks-register.md) R-09, R-15
