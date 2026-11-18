import argparse
import csv
import json
import math
import os
import sys

from .core import all_recipes, plan
from .ops import OPS, add_ops, custom_recipes, run_ops


def _finite_float(s: str) -> float:
    """argparse type: a float that is not nan/inf, so limits and prices cannot be bypassed."""
    v = float(s)
    if not math.isfinite(v):
        raise argparse.ArgumentTypeError(f"must be a finite number, got {s!r}")
    return v


def build_parser():
    ap = argparse.ArgumentParser(prog="agentsetup")
    sub = ap.add_subparsers(dest="cmd", required=True)
    store = os.environ.get("AGENTSETUP_STORE", "jobs.json")
    sub.add_parser("recipes", help="built-in recipes and your own").add_argument("--store", default=store)
    p = sub.add_parser("plan")
    p.add_argument("intake")
    p.add_argument("--rate", type=_finite_float, default=85.0)
    p.add_argument("--trip-fee", type=_finite_float, default=49.0)
    p.add_argument("--store", default=store, help="where your own recipes are kept")
    add_ops(sub)
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.cmd in OPS:
        return run_ops(a)
    own = custom_recipes(a.store)
    if a.cmd == "recipes":
        keys = {r.key for r in own}
        for r in all_recipes(own):
            mark = "*" if r.key in keys else " "
            print(f"{mark}", end="")
            print(f"{r.key:<26} {r.audience:<10} {r.minutes:>3} min  ${r.monthly:>5.2f}/mo  {r.title}")
        return 0
    with open(a.intake, encoding="utf-8-sig") as fh:
        pl = plan(json.load(fh), a.rate, a.trip_fee, own)
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


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
