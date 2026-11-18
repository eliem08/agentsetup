"""The shop's own recipes: added, preferred over built-ins, used by plan and job-open, and removable."""

import contextlib
import io
import json
import os
import pathlib
import tempfile
import unittest

from agentsetup.__main__ import main

EX = pathlib.Path(__file__).resolve().parent.parent / "examples"


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = os.path.join(self.tmp.name, "jobs.json")
        self.intake = os.path.join(self.tmp.name, "intake.json")
        doc = json.loads((EX / "bakery.json").read_text(encoding="utf-8"))
        doc["goals"] = [*doc.get("goals", []), "crm"]
        doc["tools"] = [*doc.get("tools", []), "hubspot"]
        doc.pop("monthly_budget", None)
        pathlib.Path(self.intake).write_text(json.dumps(doc), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, *extra):
        return run(
            "recipe-add",
            "crm_hubspot",
            "--title",
            "CRM follow-up (HubSpot)",
            "--goal",
            "crm",
            "--needs",
            "hubspot",
            "--minutes",
            "60",
            "--monthly",
            "30",
            "--step",
            "Create a HubSpot private app",
            "--step",
            "Map deal stages",
            *extra,
            "--store",
            self.store,
        )

    def test_own_recipe_fills_a_goal_no_built_in_covers(self):
        _, before = run("plan", self.intake, "--store", self.store)
        self.assertIn("skipped crm", before)
        self.assertEqual(self.add()[0], 0)
        _, after = run("plan", self.intake, "--store", self.store)
        self.assertIn("+ CRM follow-up (HubSpot)", after)
        self.assertIn("Map deal stages", after)
        code, out = run("job-open", "Bakery", self.intake, "--trip-fee", "0", "--store", self.store)
        self.assertEqual(code, 0, out)
        _, out = run("job-show", "JOB-0001", "--store", self.store)
        self.assertIn("[CRM follow-up (HubSpot)] Create a HubSpot private app", out)

    def test_replacing_a_built_in_and_removing_it_again(self):
        _, out = run(
            "recipe-add",
            "backups",
            "--title",
            "Our backup service",
            "--minutes",
            "20",
            "--step",
            "Install our backup agent",
            "--store",
            self.store,
        )
        self.assertIn("replaces the built-in", out)
        _, out = run("plan", self.intake, "--store", self.store)
        self.assertIn("Our backup service", out)
        _, listing = run("recipes", "--store", self.store)
        self.assertEqual(listing.count("backups"), 1)
        self.assertEqual(run("recipe-remove", "backups", "--store", self.store)[0], 0)
        _, out = run("plan", self.intake, "--store", self.store)
        self.assertNotIn("Our backup service", out)

    def test_bad_recipes_are_refused(self):
        base = ["recipe-add", "x", "--title", "t", "--store", self.store]
        self.assertEqual(run(*base, "--minutes", "0", "--step", "s")[0], 1)
        self.assertEqual(run(*base, "--minutes", "10", "--step", "  ")[0], 1)
        self.assertEqual(run(*base, "--minutes", "10", "--monthly", "-1", "--step", "s")[0], 1)
        self.assertEqual(
            run("recipe-add", "bad key!", "--title", "t", "--minutes", "5", "--step", "s", "--store", self.store)[0], 1
        )
        self.assertEqual(run("recipe-remove", "nope", "--store", self.store)[0], 1)


if __name__ == "__main__":
    unittest.main()
