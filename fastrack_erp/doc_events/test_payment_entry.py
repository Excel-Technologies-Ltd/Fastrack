from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import frappe

from fastrack_erp.doc_events import payment_entry


HBL_TYPES = (
    "Import Sea House Bill", "Import Air House Bill", "Import D2D Bill",
    "Export Sea House Bill", "Export Air House Bill", "Export D2D Bill",
)


class TestCollectionDiscountSync(TestCase):
    def test_submit_update_and_cancel_across_all_hbl_types(self):
        parents = {}
        refs = []
        for index, doctype in enumerate(HBL_TYPES):
            name = f"HBL-{index}"
            parent = SimpleNamespace(payment_entry_list=[], flags=frappe._dict(), save=Mock())
            parent.append = lambda field, row, parent=parent: parent.payment_entry_list.append(row)
            parents[(doctype, name)] = parent
            for amount in (10, 20):
                refs.append(frappe._dict(custom_hbl_type=doctype, custom_hbl_no=name,
                    allocated_amount=amount, custom_allocated_total_bdt=amount * 124,
                    exchange_gain_loss=amount / 10))
        refs.append(frappe._dict(allocated_amount=999))  # Unlinked references are ignored.
        doc = frappe._dict(name="PAY-TEST", payment_type="Receive",
            custom_payment_type_for_report="Collection Discount", party_name="Customer",
            references=refs)

        def affected(*args, **kwargs):
            return [frappe._dict(parenttype=key[0], parent=key[1])
                    for key, parent in parents.items()
                    if any(row.payment_link == doc.name for row in parent.payment_entry_list)]

        with patch.object(payment_entry, "frappe") as api:
            api.get_doc.side_effect = lambda doctype, name: parents[(doctype, name)]
            api.new_doc.side_effect = lambda doctype: frappe._dict()
            api.db.get_all.side_effect = affected
            payment_entry.after_submit(doc, None)
            for parent in parents.values():
                self.assertEqual(len(parent.payment_entry_list), 1)
                row = parent.payment_entry_list[0]
                self.assertEqual(row.payment_type_for_report, "Collection Discount")
                self.assertEqual(row.payment_type, "Receive")
                self.assertEqual(row.amount_usd, 30)
                self.assertEqual(row.amount, 3720)
                self.assertEqual(row.exchange_gain_loss, 3)
                self.assertEqual(parent.total_payment_received_bdt, 0)

            # Submitted edits replace old allocations, including removed HBLs.
            doc.references = [refs[0]]
            for _ in range(2):
                payment_entry.on_update_after_submit(doc, None)
                self.assertEqual(sum(len(p.payment_entry_list) for p in parents.values()), 1)
                self.assertEqual(parents[(HBL_TYPES[0], "HBL-0")].payment_entry_list[0].amount, 1240)
            payment_entry.before_cancel(doc, None)
            self.assertTrue(all(not p.payment_entry_list for p in parents.values()))

    def test_existing_categories_still_sync(self):
        for category in ("Receive", "Pay", "Profit Share"):
            with self.subTest(category=category), patch.object(payment_entry, "frappe") as api:
                parent = SimpleNamespace(payment_entry_list=[], flags=frappe._dict(), save=Mock())
                parent.append = lambda field, row: parent.payment_entry_list.append(row)
                api.get_doc.return_value = parent
                api.new_doc.side_effect = lambda doctype: frappe._dict()
                doc = frappe._dict(name="PAY", payment_type="Receive",
                    custom_payment_type_for_report=category, party="Customer", references=[
                        frappe._dict(custom_hbl_type=HBL_TYPES[0], custom_hbl_no="HBL",
                            allocated_amount=10, custom_allocated_total_bdt=1240)])
                payment_entry.after_submit(doc, None)
                self.assertEqual(parent.payment_entry_list[0].payment_type_for_report, category)
                total_field = {"Receive": "total_payment_received_bdt", "Pay": "total_pay_bdt",
                    "Profit Share": "total_payment_profit_share_bdt"}[category]
                self.assertEqual(getattr(parent, total_field), 1240)
