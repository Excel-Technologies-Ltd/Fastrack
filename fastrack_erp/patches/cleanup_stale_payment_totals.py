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
)


def execute():
    """
    total_pay_bdt ("Total Pay (BDT)") used to be written by
    doc_events.purchase_invoice from submitted Purchase Invoices. That hook no
    longer writes it -- ownership moved to doc_events.payment_entry -- but
    documents with no linked Payment Entry rows were never revisited, so they
    were left showing a stale value from the old calculation. Recompute all
    five payment-driven totals from the current payment_entry_list on every
    HBL document so stale values (including on documents with zero payment
    entries) are cleared.
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
    print(f"Recalculated payment totals on {fixed} HBL document(s) with stale values.")
