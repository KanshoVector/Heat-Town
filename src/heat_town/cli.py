"""Command-line interface for heat-town data pipeline.

Examples
--------
    python -m heat_town.cli fetch-weather --sample
    python -m heat_town.cli fetch-poi --sample
    python -m heat_town.cli build-grid
    python -m heat_town.cli pipeline --sample
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from heat_town import samples


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_fetch_weather(args: argparse.Namespace) -> None:
    if args.full:
        raise SystemExit(
            "fetch-weather --full は未実装です。Open-Meteo API 取得はサンプルで代替してください "
            "(--sample)。docs/data.md 参照。"
        )
    path = samples.generate_weather(samples._samples_dir())
    print(f"[fetch-weather] sample -> {path}")


def cmd_fetch_poi(args: argparse.Namespace) -> None:
    if args.full:
        raise SystemExit(
            "fetch-poi --full は未実装です。OSM Overpass 取得はサンプルで代替してください "
            "(--sample)。docs/data.md 参照。"
        )
    path = samples.generate_poi(samples._samples_dir())
    print(f"[fetch-poi] sample -> {path}")


def cmd_build_grid(args: argparse.Namespace) -> None:
    path = samples.generate_grid(samples._samples_dir())
    print(f"[build-grid] -> {path}")


def cmd_pipeline(args: argparse.Namespace) -> None:
    """samples 生成 → preprocess → export を一気通し。

    preprocess / export は後続タスクで実装される。存在すれば呼び、
    無ければ該当ステップをスキップして案内を出す（段階的に動く設計）。
    """
    if not args.sample:
        raise SystemExit("pipeline は現在 --sample のみ対応です。")

    samples.main()
    print("[pipeline] samples 生成完了")

    # --- preprocess（feature/preprocess で実装予定）---
    try:
        from heat_town import preprocess  # type: ignore

        out = preprocess.run_sample()
        print(f"[pipeline] preprocess -> {out}")
    except ImportError:
        print("[pipeline] preprocess 未実装のためスキップ（feature/preprocess で追加）")

    # --- export（feature/export で実装予定）---
    try:
        from heat_town import export

        features = _repo_root() / "data" / "processed" / "features.parquet"
        if features.exists():
            out = export.export_scores_geojson(features)
            print(f"[pipeline] export -> {out}")
        else:
            print("[pipeline] features.parquet が無いため export をスキップ")
    except ImportError:
        print("[pipeline] export 未実装のためスキップ（feature/export で追加）")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="heat_town.cli", description="heat-town data pipeline CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_weather = sub.add_parser("fetch-weather", help="気象データ取得")
    p_weather.add_argument("--sample", action="store_true", help="サンプルを生成")
    p_weather.add_argument("--full", action="store_true", help="実 API 取得（未実装）")
    p_weather.set_defaults(func=cmd_fetch_weather)

    p_poi = sub.add_parser("fetch-poi", help="POI データ取得")
    p_poi.add_argument("--sample", action="store_true", help="サンプルを生成")
    p_poi.add_argument("--full", action="store_true", help="実 API 取得（未実装）")
    p_poi.set_defaults(func=cmd_fetch_poi)

    p_grid = sub.add_parser("build-grid", help="評価グリッド生成")
    p_grid.set_defaults(func=cmd_build_grid)

    p_pipe = sub.add_parser("pipeline", help="samples→preprocess→export 一気通し")
    p_pipe.add_argument("--sample", action="store_true", help="サンプルデータで実行")
    p_pipe.set_defaults(func=cmd_pipeline)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])