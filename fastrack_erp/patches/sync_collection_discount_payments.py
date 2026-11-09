import frappe

from fastrack_erp.doc_events.payment_entry import on_update_after_submit


def execute():
    field = frappe.get_doc("Custom Field", "Payment Entry-custom_payment_type_for_report")
    options = (field.options or "").splitlines()
    if "Collection Discount" not in options:
        field.options = "\n".join([*options, "Collection Discount"])
        field.save()

    # Rebuild just these payments' derived rows using their per-reference HBLs.
    # Removing old rows first also makes a repeated run safe.
    for name in frappe.get_all("Payment Entry", filters={
        "docstatus": 1, "custom_payment_type_for_report": "Collection Discount",
    }, pluck="name"):
        on_update_after_submit(frappe.get_doc("Payment Entry", name), None)
