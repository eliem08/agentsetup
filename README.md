<!-- sell-kit:start -->
# AgentSetup

[![CI](https://github.com/eliem08/agentsetup/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/agentsetup/actions/workflows/ci.yml)

> **Set up safe personal AI agents for families and small businesses.**

**Who it's for:** IT consultants and MSPs, and the households and small firms they serve.

**The problem:** People want AI agents working for them but can't tell which tools are safe, how to set them up or what it should cost.

**What you get:** Turn an intake form into a safe agent stack, a step-by-step setup checklist and a one-time plus monthly quote, with backups and protections included by default.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install agentsetup-0.1.0-py3-none-any.whl
agentsetup recipes
agentsetup plan examples/family.json
agentsetup plan examples/bakery.json --rate 95
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
agentsetup-web --port 8000          # then open http://127.0.0.1:8000
agentsetup-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t agentsetup . && docker run -p 8000:8000 -e API_KEYS=sk_... -v agentsetup-data:/data agentsetup
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `agentsetup-web usage` prints calls per key for billing.

Endpoints: `POST /api/recipes`, `POST /api/plan`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Solo Tech** | $39 per month | Unlimited intakes and quotes; Setup checklists; Safety defaults |
| **Shop** | $149 per month | 5 technicians; Custom recipes and rates; Branded quotes |
| **Done-for-you** | $299 per household setup | We set it up for you; Backups and protections included; 30 days of support |

To start a trial or buy a plan, [request access](https://github.com/eliem08/agentsetup/issues/new?title=AgentSetup%20trial&labels=sales).

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

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
agentsetup recipes
agentsetup plan examples/family.json
agentsetup plan examples/bakery.json --rate 95
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
agentsetup/core.py       domain logic (pure, importable, fully tested)
agentsetup/__main__.py   CLI (`agentsetup ...` / `python -m agentsetup ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #16).
