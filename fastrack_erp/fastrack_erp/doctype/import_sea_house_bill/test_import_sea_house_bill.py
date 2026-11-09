# Copyright (c) 2025, Shaid Azmin and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from fastrack_erp.fastrack_erp.doctype.import_sea_house_bill import import_sea_house_bill as house_bill


class TestImportSeaHouseBill(FrappeTestCase):
	pass


class TestContainerWeightPrecision(TestCase):
	@patch("frappe.get_system_settings", return_value="Banker's Rounding")
	def test_container_weight_limit(self, _settings):
		for weight, exceeds_limit in ((9991.20, False), (9991.19, False), (9991.21, True)):
			with self.subTest(weight=weight):
				item = SimpleNamespace(
					custom_container_no="HALU5652698", seal_no="seal", weight=weight,
					no_of_pkg=1, precision=Mock(return_value=2),
				)
				doc = SimpleNamespace(name="XF261002401B", mbl_link="master", container_info=[item])
				master = dict(weight=16309.30, seal_no="seal", no_of_pkg=2)
				existing = dict(weight=6318.1, no_of_pkg=1)
				with patch.object(house_bill, "get_single_fastrack_item_by_bill_no", side_effect=[master, existing]), patch.object(house_bill, "frappe") as frappe_mock:
					frappe_mock.db.get_list.return_value = [{"name": doc.name}, {"name": "other"}]
					frappe_mock.throw.side_effect = ValueError
					if exceeds_limit:
						with self.assertRaises(ValueError):
							house_bill.ImportSeaHouseBill.validate_container_weight(doc)
						self.assertIn("Weight mismatch", frappe_mock.throw.call_args.args[0])
					else:
						house_bill.ImportSeaHouseBill.validate_container_weight(doc)
						frappe_mock.throw.assert_not_called()
