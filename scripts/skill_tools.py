#!/usr/bin/env python3
"""Optional CLI for data lookup, contracts and static report display, not vision."""
import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.contracts import DEFAULT_CATALOG, ContractError, load_catalog, read_json, validate_report
from scripts.rendering import render_html


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("check-catalog")
    commands.add_parser("list")
    commands.add_parser("show").add_argument("style_id")
    commands.add_parser("check-report").add_argument("report", type=Path)
    rendering = commands.add_parser("render")
    rendering.add_argument("report", type=Path)
    rendering.add_argument("--output", required=True, type=Path)
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        if args.command == "check-catalog":
            print("Catalog valid: " + str(len(catalog.styles)) + " styles")
        elif args.command == "list":
            for style in catalog.styles.values():
                print(style["kind"] + "\t" + style["id"] + "\t" + style["name"])
        elif args.command == "show":
            style = catalog.styles.get(args.style_id)
            if style is None:
                raise ContractError("Unknown style: " + args.style_id)
            print(json.dumps(style, ensure_ascii=False, indent=2))
        else:
            report = validate_report(read_json(args.report), catalog)
            if args.command == "check-report":
                print("Report valid: " + report["status"])
            else:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x", encoding="utf-8") as file:
                    file.write(render_html(report, catalog))
                print("Local report: " + str(args.output.resolve()))
        return 0
    except (ContractError, OSError) as exc:
        print("Validation failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
