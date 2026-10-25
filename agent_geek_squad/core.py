"""Intake -> agent stack plan, safety settings, checklist and quote."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Recipe", "RECIPES", "Plan", "plan"]


@dataclass
class Recipe:
    key: str
    title: str
    goal: str | None
    audience: str  # household / business / any
    needs_any: list = field(default_factory=list)  # one of these tools must be present
    minutes: int = 30
    monthly: float = 0.0
    local_ok: bool = True
    steps: list = field(default_factory=list)


RECIPES = [
    Recipe(
        "inbox_gmail",
        "Inbox triage agent (Gmail)",
        "inbox",
        "any",
        ["gmail"],
        45,
        20,
        True,
        [
            "Create agent workspace account",
            "Connect Gmail with read+draft scopes only",
            "Teach 5 example labels",
            "Turn on daily digest at 7am",
        ],
    ),
    Recipe(
        "inbox_outlook",
        "Inbox triage agent (Outlook)",
        "inbox",
        "any",
        ["outlook"],
        50,
        20,
        True,
        ["Register app in Microsoft 365", "Grant Mail.ReadWrite (drafts only)", "Set triage rules", "Daily digest"],
    ),
    Recipe(
        "family_calendar",
        "Shared family calendar agent",
        "calendar",
        "household",
        ["google_calendar", "outlook"],
        30,
        0,
        True,
        ["Create shared family calendar", "Connect school email parsing", "Weekly 'week ahead' summary"],
    ),
    Recipe(
        "homework",
        "Homework helper with tutor mode",
        "homework",
        "household",
        [],
        40,
        20,
        True,
        ["Create child profile", "Enable 'explain, don't answer' tutor mode", "Parent weekly report"],
    ),
    Recipe(
        "elder_checkin",
        "Daily check-in & medication reminders",
        "elder_care",
        "household",
        [],
        40,
        10,
        True,
        ["Set up large-text companion app", "Medication schedule", "Missed-check-in alert to family"],
    ),
    Recipe(
        "bookkeeping_qb",
        "Bookkeeping assistant (QuickBooks)",
        "bookkeeping",
        "business",
        ["quickbooks"],
        60,
        30,
        False,
        ["Connect QuickBooks read + categorise", "Receipt inbox forwarding", "Monthly close checklist"],
    ),
    Recipe(
        "customer_replies_shopify",
        "Customer reply agent (Shopify)",
        "customer_replies",
        "business",
        ["shopify"],
        75,
        40,
        False,
        [
            "Connect Shopify orders (read)",
            "Import FAQ & return policy",
            "Draft-only replies for 2 weeks",
            "Escalation rules to owner",
        ],
    ),
    Recipe(
        "social",
        "Social post drafter",
        "social",
        "business",
        [],
        30,
        15,
        False,
        ["Brand voice samples", "Weekly content calendar", "Approval before posting"],
    ),
    # safety recipes (goal None => added by rules)
    Recipe(
        "kid_filters",
        "Kid-safe content filters & time limits",
        None,
        "household",
        [],
        25,
        0,
        True,
        ["Child accounts with age settings", "Block adult content", "Screen-time schedule"],
    ),
    Recipe(
        "scam_shield",
        "Scam protection for seniors",
        None,
        "household",
        [],
        30,
        5,
        True,
        ["Install scam-shield forwarding", "Set family safe word", "Alert adult child on high-risk messages"],
    ),
    Recipe(
        "access_controls",
        "Agent access controls & audit log",
        None,
        "business",
        [],
        45,
        10,
        True,
        ["One identity per agent (agent-okta)", "Least-privilege scopes", "Weekly audit review"],
    ),
    Recipe(
        "backups",
        "Backups before agents get write access",
        None,
        "any",
        [],
        30,
        8,
        True,
        ["Enable cloud backups / version history", "Test a restore"],
    ),
]
BY_KEY = {r.key: r for r in RECIPES}


@dataclass
class Plan:
    recipes: list
    skipped: list
    checklist: list
    tech_minutes: int
    one_time: float
    monthly: float
    care_plan: float


def _fits(r: Recipe, intake: dict) -> str | None:
    if r.audience not in ("any", intake["type"]):
        return "wrong audience"
    if r.needs_any and not set(r.needs_any) & set(intake.get("tools", [])):
        return f"needs one of {r.needs_any}"
    if intake.get("privacy") == "prefer_local" and not r.local_ok:
        return "requires cloud processing"
    return None


def plan(intake: dict, rate_per_hour: float = 85.0, trip_fee: float = 49.0) -> Plan:
    if not isinstance(intake, dict):
        raise ValueError("intake must be a JSON object")
    chosen, skipped = [], []
    for goal in intake.get("goals", []):
        options = [r for r in RECIPES if r.goal == goal]
        fits = [r for r in options if not _fits(r, intake)]
        if fits:
            chosen.append(fits[0])
        else:
            skipped.append((goal, "; ".join(f"{r.title}: {_fits(r, intake)}" for r in options) or "no recipe"))
    ages = [m.get("age", 30) for m in intake.get("members", [])]
    mandatory = ["backups"]
    if intake["type"] == "household" and any(a < 16 for a in ages):
        mandatory.append("kid_filters")
    if intake["type"] == "household" and any(a >= 70 for a in ages):
        mandatory.append("scam_shield")
    if intake["type"] == "business":
        mandatory.append("access_controls")
    chosen += [BY_KEY[k] for k in mandatory]

    budget = intake.get("monthly_budget")
    if budget is not None:
        total = sum(r.monthly for r in chosen)
        for r in sorted([r for r in chosen if r.goal], key=lambda r: -r.monthly):
            if total <= budget:
                break
            chosen.remove(r)
            total -= r.monthly
            skipped.append((r.goal, f"{r.title}: over monthly budget"))

    minutes = sum(r.minutes for r in chosen)
    checklist = [f"[{r.title}] {s}" for r in chosen for s in r.steps]
    one_time = round(trip_fee + minutes / 60 * rate_per_hour, 2)
    monthly = round(sum(r.monthly for r in chosen), 2)
    care = round(19 + 4 * len(chosen), 2)
    return Plan([r.title for r in chosen], skipped, checklist, minutes, one_time, monthly, care)
