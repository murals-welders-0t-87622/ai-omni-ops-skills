import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BusinessRoutingCoverageTests(unittest.TestCase):
    def test_every_registered_skill_has_a_routing_entry(self):
        registry = json.loads((ROOT / "registry/skills.json").read_text(encoding="utf-8"))
        routing = (ROOT / "skills/brand-omni-growth-expert/references/business-routing.md").read_text(encoding="utf-8")
        routed = set()
        for line in routing.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(cells) >= 3:
                routed.add(cells[1])
        registered = {entry["id"] for entry in registry["skills"]}
        self.assertEqual(registered - routed, set(), "Registered skills missing from the business routing table")


if __name__ == "__main__":
    unittest.main()
