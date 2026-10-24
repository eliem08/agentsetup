import argparse
import json
import sys

from .core import RECIPES, plan


def main(argv=None):
    ap = argparse.ArgumentParser(prog="agent-geek-squad")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("recipes")
    p = sub.add_parser("plan")
    p.add_argument("intake")
    p.add_argument("--rate", type=float, default=85.0)
    a = ap.parse_args(argv)
    if a.cmd == "recipes":
        for r in RECIPES:
            print(f"{r.key:<26} {r.audience:<10} {r.minutes:>3} min  ${r.monthly:>5.2f}/mo  {r.title}")
        return 0
    with open(a.intake, encoding="utf-8") as fh:
        pl = plan(json.load(fh), a.rate)
    print("Recommended stack:")
    for t in pl.recipes:
        print(f"  + {t}")
    for goal, why in pl.skipped:
        print(f"  - skipped {goal}: {why}")
    print(f"\nSetup visit: {pl.tech_minutes} min -> ${pl.one_time:,.2f} one-time")
    print(f"Software: ${pl.monthly:,.2f}/mo   Optional care plan: ${pl.care_plan:,.2f}/mo")
    print("\nChecklist:")
    for i, step in enumerate(pl.checklist, 1):
        print(f"  [ ] {i:>2}. {step}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
