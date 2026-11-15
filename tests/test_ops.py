import contextlib
import io
import os
import tempfile
import unittest

from agentsetup.__main__ import main
from agentsetup.ops import load

BAKERY = os.path.join(os.path.dirname(__file__), "..", "examples", "bakery.json")


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class JobOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "jobs.json")
        self.s = ["--store", self.path]

    def tearDown(self):
        self.tmp.cleanup()

    def ok(self, *argv):
        code, out = run(*argv, *self.s)
        self.assertEqual(code, 0, out)
        return out

    def test_job_closes_only_when_every_step_is_done(self):
        self.assertIn("JOB-0001", self.ok("job-open", "Rosa's Bakery", BAKERY))
        steps = len(load(self.path)["jobs"]["JOB-0001"]["steps"])
        self.assertGreater(steps, 3)
        self.ok("job-step", "JOB-0001", "1", "--note", "used the shop Outlook account")
        self.assertEqual(run("job-close", "JOB-0001", *self.s)[0], 1)
        for n in range(2, steps + 1):
            self.ok("job-step", "JOB-0001", str(n))
        self.assertIn("signed off", self.ok("job-close", "JOB-0001"))
        self.assertIn("used the shop Outlook account", self.ok("job-show", "JOB-0001"))
        self.assertEqual(run("job-step", "JOB-0001", "1", *self.s)[0], 1)  # closed jobs are frozen
        self.assertEqual(run("job-close", "JOB-0001", *self.s)[0], 1)

    def test_price_is_frozen_at_open_and_ids_do_not_collide(self):
        self.ok("job-open", "A", BAKERY, "--rate", "100")
        self.ok("job-open", "B", BAKERY, "--rate", "50")
        jobs = load(self.path)["jobs"]
        self.assertEqual(sorted(jobs), ["JOB-0001", "JOB-0002"])
        self.assertGreater(jobs["JOB-0001"]["one_time"], jobs["JOB-0002"]["one_time"])

    def test_refusals(self):
        self.ok("job-open", "A", BAKERY)
        for argv in (
            ["job-step", "JOB-0001", "999"],
            ["job-step", "JOB-9", "1"],
            ["job-open", "A", BAKERY, "--rate", "0"],
        ):
            with self.subTest(argv=argv):
                self.assertEqual(run(*argv, *self.s)[0], 1)


if __name__ == "__main__":
    unittest.main()
