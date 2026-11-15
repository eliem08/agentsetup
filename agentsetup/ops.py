"""Operating commands: track a setup visit from intake to sign-off (also served by the web app).

A job freezes the plan, checklist and price when it is opened. The technician ticks steps off on site;
a job closes only when every step is done, and the close-out is the record handed to the client.
"""

import itertools
import json
import os
import time

from .core import plan

OPS = ("job-open", "job-step", "job-show", "job-close", "jobs")


class JobError(ValueError):
    pass


def load(path: str) -> dict:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return {"jobs": {}, "next_id": 1}
    if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), dict):
        raise JobError(f"{path}: not an agentsetup store")
    return doc


def save(doc: dict, path: str):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    os.replace(tmp, path)


def add_ops(sub):
    store = os.environ.get("AGENTSETUP_STORE", "jobs.json")
    p = sub.add_parser("job-open", help="turn a client intake into a priced job with a checklist")
    p.add_argument("client")
    p.add_argument("intake", help="the intake JSON file")
    p.add_argument("--rate", type=float, default=85.0, help="technician rate per hour")
    p = sub.add_parser("job-step", help="tick off a checklist step on site")
    p.add_argument("job_id")
    p.add_argument("step", type=int, help="step number from job-show")
    p.add_argument("--note", default="", help="what was done, or what the client should know")
    sub.add_parser("job-show", help="the checklist and what is left").add_argument("job_id")
    sub.add_parser("job-close", help="sign the job off once every step is done").add_argument("job_id")
    sub.add_parser("jobs", help="every job and its progress")
    for name in OPS:
        sub.choices[name].add_argument("--store", default=store)


def run_ops(a) -> int:
    try:
        doc = load(a.store)
        _run(doc, a)
        save(doc, a.store)
        return 0
    except (ValueError, KeyError) as e:
        print(f"refused: {e.args[0] if e.args else e}")
        return 1


def _job(doc: dict, jid: str) -> dict:
    if jid not in doc["jobs"]:
        raise JobError(f"no job {jid!r}")
    return doc["jobs"][jid]


def _left(job: dict) -> int:
    return sum(not s["done"] for s in job["steps"])


def _run(doc: dict, a):
    c = a.cmd
    if c == "job-open":
        if not (a.rate > 0):
            raise JobError("rate must be > 0")
        with open(a.intake, encoding="utf-8-sig") as fh:
            pl = plan(json.load(fh), a.rate)
        if not pl.checklist:
            raise JobError("this intake produces no work: check its goals and tools")
        ids = itertools.count(int(doc.get("next_id", 1)))
        jid = f"JOB-{next(ids):04d}"
        doc["next_id"] = next(ids)
        doc["jobs"][jid] = {
            "client": a.client,
            "status": "open",
            "opened": int(time.time()),
            "recipes": pl.recipes,
            "steps": [{"text": s, "done": False, "note": ""} for s in pl.checklist],
            "tech_minutes": pl.tech_minutes,
            "one_time": pl.one_time,
            "monthly": pl.monthly,
            "care_plan": pl.care_plan,
        }
        print(f"{jid} for {a.client}: {len(pl.checklist)} steps, about {pl.tech_minutes} min")
        print(
            f"  ${pl.one_time:,.2f} one-time, ${pl.monthly:,.2f}/mo software, optional care plan ${pl.care_plan:,.2f}/mo"
        )
    elif c == "job-step":
        job = _job(doc, a.job_id)
        if job["status"] != "open":
            raise JobError(f"{a.job_id} is closed")
        if not 1 <= a.step <= len(job["steps"]):
            raise JobError(f"step must be between 1 and {len(job['steps'])}")
        step = job["steps"][a.step - 1]
        step["done"], step["note"] = True, a.note.strip() or step["note"]
        print(f"step {a.step} done: {step['text']}  ({_left(job)} left)")
    elif c == "job-show":
        job = _job(doc, a.job_id)
        print(f"{a.job_id} for {job['client']} ({job['status']})")
        for i, s in enumerate(job["steps"], 1):
            note = f"  - {s['note']}" if s["note"] else ""
            print(f"  [{'x' if s['done'] else ' '}] {i:>2}. {s['text']}{note}")
        print(f"{_left(job)} step(s) left")
    elif c == "job-close":
        job = _job(doc, a.job_id)
        if job["status"] != "open":
            raise JobError(f"{a.job_id} is already closed")
        left = [i for i, s in enumerate(job["steps"], 1) if not s["done"]]
        if left:
            raise JobError(f"{len(left)} step(s) still open: {left}")
        job["status"], job["closed"] = "closed", int(time.time())
        print(f"{a.job_id} signed off for {job['client']}: {', '.join(job['recipes'])}")
        print(f"  invoice ${job['one_time']:,.2f} one-time; software ${job['monthly']:,.2f}/mo")
    else:
        for jid, job in doc["jobs"].items():
            done = len(job["steps"]) - _left(job)
            print(
                f"{jid}  {job['status']:<7}{job['client']:<20}{done}/{len(job['steps'])} steps  ${job['one_time']:>9,.2f}"
            )
        if not doc["jobs"]:
            print("no jobs yet")
