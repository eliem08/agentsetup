# agent-geek-squad

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
