import frappe

from fastrack_erp.doc_events.payment_entry import _recalculate_payment_totals

HBL_DOCTYPES = [
    "Import Sea House Bill",
    "Import Air House Bill",
    "Import D2D Bill",
    "Export Sea House Bill",
    "Export Air House Bill",
    "Export D2D Bill",
]

TOTAL_FIELDS = (
    "total_payment_received_usd",
    "total_payment_received_bdt",
    "total_pay_usd",
    "total_pay_bdt",
    "total_exchange_gain_loss",
    "total_payment_profit_share_usd",
    "total_payment_profit_share_bdt",
    "total_collection_discount_usd",
    "total_collection_discount_bdt",
)


def execute():
    """
    Total Received now includes Collection Discount rows, and dedicated
    Collection Discount (USD/BDT) totals were added. Recompute payment
    totals on every HBL from payment_entry_list.
    """
    fixed = 0

    for doctype in HBL_DOCTYPES:
        names = frappe.db.get_all(doctype, pluck="name")
        for name in names:
            hbl_doc = frappe.get_doc(doctype, name)
            before = {field: hbl_doc.get(field) for field in TOTAL_FIELDS}

            _recalculate_payment_totals(hbl_doc)

            after = {field: hbl_doc.get(field) for field in TOTAL_FIELDS}
            if before == after:
                continue

            hbl_doc.flags.ignore_validate_update_after_submit = True
            hbl_doc.db_update()
            fixed += 1

    frappe.db.commit()
    print(
        f"Recalculated received + collection discount totals on {fixed} HBL(s)."
    )
