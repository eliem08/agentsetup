# agent-geek-squad

[![CI](https://github.com/eliem08/agent-geek-squad/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/agent-geek-squad/actions/workflows/ci.yml)

> **Geek Squad for AI** — set up personal agents for families and small businesses.

Most families and 5-person businesses will never wire up their own agents.
They'll pay someone to come in, set it up safely and keep it running.
`agent-geek-squad` is the technician's toolkit: an intake questionnaire
becomes a recommended agent stack, safety settings, a step-by-step setup
checklist and a priced service quote.

## What the MVP does

- **Intake** (JSON or interactive): household vs. business, members & ages,
  tools already used (Gmail, Outlook, QuickBooks, Shopify…), goals, privacy
  preference (`cloud_ok` / `prefer_local`), monthly budget
- **Recipe catalogue** of ~12 setup recipes (inbox triage, family calendar,
  homework helper with guardrails, elder check-in + scam shield, bookkeeping
  assistant, customer-reply bot, …) each with prerequisites, setup steps,
  minutes of tech time, monthly software cost
- **Planner** picks recipes matching goals and tools, adds mandatory safety
  recipes (kids → content filters; seniors → scam protection; business →
  access controls + backups), drops ones over budget or violating privacy
- **Quote**: tech time × rate + monthly software + optional care plan
- Printable **setup checklist** for the visit

## Quickstart

```bash
pip install -e .
agent-geek-squad recipes
agent-geek-squad plan examples/family.json
agent-geek-squad plan examples/bakery.json --rate 95
```

## Roadmap

- Technician app with credential vault handoff and photo-verified completion
- Remote "care plan" monitoring using agent-alarm + agent-tracer
- Franchise / partner network with certification

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
agent_geek_squad/core.py       domain logic (pure, importable, fully tested)
agent_geek_squad/__main__.py   CLI (`agent-geek-squad ...` / `python -m agent_geek_squad ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #16).
