import json
import pathlib
import unittest

from agentsetup import plan

EX = pathlib.Path(__file__).resolve().parent.parent / "examples"


class Tests(unittest.TestCase):
    def test_family_gets_safety_recipes(self):
        p = plan(json.loads((EX / "family.json").read_text()))
        self.assertIn("Kid-safe content filters & time limits", p.recipes)
        self.assertIn("Scam protection for seniors", p.recipes)
        self.assertIn("Inbox triage agent (Gmail)", p.recipes)
        self.assertLessEqual(p.monthly, 75)

    def test_business(self):
        p = plan(json.loads((EX / "bakery.json").read_text()))
        self.assertIn("Agent access controls & audit log", p.recipes)
        self.assertIn("Inbox triage agent (Outlook)", p.recipes)
        self.assertNotIn("Kid-safe content filters & time limits", p.recipes)
        self.assertGreater(p.one_time, 49)

    def test_privacy_and_missing_tools(self):
        p = plan(
            {
                "type": "business",
                "members": [],
                "tools": [],
                "goals": ["bookkeeping", "inbox"],
                "privacy": "prefer_local",
            }
        )
        goals = [g for g, _ in p.skipped]
        self.assertEqual(sorted(goals), ["bookkeeping", "inbox"])

    def test_budget_trims_most_expensive(self):
        p = plan(
            {
                "type": "household",
                "members": [{"age": 40}],
                "tools": ["gmail"],
                "goals": ["inbox", "homework"],
                "monthly_budget": 30,
            }
        )
        self.assertLessEqual(p.monthly, 30)
        self.assertTrue(any("over monthly budget" in why for _, why in p.skipped))


if __name__ == "__main__":
    unittest.main()
