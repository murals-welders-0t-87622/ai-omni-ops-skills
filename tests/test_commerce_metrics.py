import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("commerce_metrics", Path(__file__).resolve().parents[1] / "skills/taobao-tmall-operations/scripts/commerce_metrics.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CommerceMetricsTests(unittest.TestCase):
    def setUp(self):
        self.cost = dict(price="100", productCost="40", shipping="5", packaging="2", platformRate="0.05", taxRate="0.03", refundLossPerUnit="3", otherPerUnit="2", adCostPerUnit="10")

    def test_contribution_is_not_gross_markup(self):
        r = m.calculate({"unitEconomics": self.cost})["unitEconomics"]
        self.assertEqual(r["contributionBeforeAds"], "40.0000")
        self.assertEqual(r["contributionAfterAds"], "30.0000")
        self.assertEqual(r["breakEvenROAS"], "2.5000")

    def test_unknown_tax_does_not_default_to_zero(self):
        self.cost.pop("taxRate")
        r = m.calculate({"unitEconomics": self.cost})
        self.assertIsNone(r["unitEconomics"]["contributionBeforeAds"])
        self.assertIn("unitEconomics.taxRate", r["missing"])

    def test_zero_ad_cost_is_known(self):
        self.cost["adCostPerUnit"] = "0"
        self.assertEqual(m.calculate({"unitEconomics": self.cost})["unitEconomics"]["contributionAfterAds"], "40.0000")

    def test_loss_has_no_positive_break_even(self):
        self.cost["productCost"] = "140"
        self.assertIsNone(m.calculate({"unitEconomics": self.cost})["unitEconomics"]["breakEvenROAS"])

    def test_rate_units_and_nonfinite_rejected(self):
        for value in ["5", "NaN", "Infinity", "-0.01", 0.05]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.calculate({"unitEconomics": {**self.cost, "platformRate": value}})

    def test_buyer_and_order_denominators_are_distinct(self):
        r = m.calculate({"funnel": dict(visitors="100", buyers="10", orders="12", payment="600", impressions="1000", clicks="40", adSpend="20", adAttributedPayment="100")})["funnel"]
        self.assertEqual(r["visitorBuyerFraction"], "0.1000")
        self.assertEqual(r["perBuyerPayment"], "60.0000")
        self.assertEqual(r["perOrderPayment"], "50.0000")
        self.assertEqual(r["roas"], "5.0000")

    def test_empty_and_zero_denominator_unknown(self):
        r = m.calculate({"funnel": {"impressions": "0", "clicks": "0"}})["funnel"]
        self.assertIsNone(r["ctrFraction"])
        self.assertIsNone(r["roas"])


if __name__ == "__main__":
    unittest.main()
