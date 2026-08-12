from collections import defaultdict

import frappe

from fastrack_erp.doc_events.payment_entry import REPORT_BUCKETS, _recalculate_payment_totals

HBL_DOCTYPES = [
    "Import Sea House Bill",
    "Import Air House Bill",
    "Import D2D Bill",
    "Export Sea House Bill",
    "Export Air House Bill",
    "Export D2D Bill",
]


def execute():
    """
    payment_entry_list used to hold one row per (Payment Entry, HBL the
    payment's own custom_hbl_type/link field pointed to) with the payment's
    full amount -- wrong whenever a payment was actually split across
    several HBLs via its Payment Entry References. Wipe every existing row
    and rebuild it from the references themselves: one row per HBL each
    reference is allocated against (custom_hbl_type/custom_hbl_no on
    Payment Entry Reference), summing allocated_amount / BDT allocated /
    exchange gain-loss per HBL, so a payment referencing N different HBLs
    now correctly produces a row on each of the N HBLs instead of one row
    on whichever HBL the payment happened to be tagged with.
    """
    touched = set(
        (row.parenttype, row.parent)
        for doctype in HBL_DOCTYPES
        for row in frappe.db.get_all(
            "Fastrack Payment Entry", filters={"parenttype": doctype}, fields=["parent", "parenttype"]
        )
    )

    references = frappe.db.get_all(
        "Payment Entry Reference",
        filters={"custom_hbl_type": ["in", HBL_DOCTYPES], "custom_hbl_no": ["is", "set"]},
        fields=[
            "parent",
            "custom_hbl_type",
            "custom_hbl_no",
            "allocated_amount",
            "custom_allocated_total_bdt",
            "exchange_gain_loss",
        ],
    )

    payment_entries = {
        pe.name: pe
        for pe in frappe.db.get_all(
            "Payment Entry",
            filters={"docstatus": 1},
            fields=["name", "payment_type", "custom_payment_type_for_report", "party_name", "party"],
        )
    }

    # groups[(hbl_type, hbl_no)][payment_name] = {"usd":.., "bdt":.., "fx":..}
    groups = defaultdict(lambda: defaultdict(lambda: {"usd": 0.0, "bdt": 0.0, "fx": 0.0}))
    for ref in references:
        pe = payment_entries.get(ref.parent)
        if not pe:
            continue
        report_type = pe.custom_payment_type_for_report or pe.payment_type
        if report_type not in REPORT_BUCKETS:
            continue

        bucket = groups[(ref.custom_hbl_type, ref.custom_hbl_no)][ref.parent]
        bucket["usd"] += float(ref.allocated_amount or 0)
        bucket["bdt"] += float(ref.custom_allocated_total_bdt or 0)
        bucket["fx"] += float(ref.exchange_gain_loss or 0)

    # wipe every existing row first so the rebuild below starts from empty
    # tables on both sides (old HBLs that no longer have valid references,
    # and HBLs about to gain rows for the first time).
    for doctype, name in touched:
        frappe.db.delete("Fastrack Payment Entry", {"parenttype": doctype, "parent": name})

    all_docs = touched | set(groups.keys())

    updated = 0
    for doctype, name in all_docs:
        if not frappe.db.exists(doctype, name):
            continue

        hbl_doc = frappe.get_doc(doctype, name)
        for payment_name, totals in groups.get((doctype, name), {}).items():
            pe = payment_entries[payment_name]
            report_type = pe.custom_payment_type_for_report or pe.payment_type

            row = frappe.new_doc("Fastrack Payment Entry")
            row.payment_link = payment_name
            row.payment_type = pe.payment_type
            row.payment_type_for_report = report_type
            row.party = pe.party_name or pe.party
            row.amount_usd = totals["usd"]
            row.amount = totals["bdt"]
            row.exchange_gain_loss = totals["fx"]
            hbl_doc.append("payment_entry_list", row)

        _recalculate_payment_totals(hbl_doc)
        hbl_doc.flags.ignore_validate_update_after_submit = True
        hbl_doc.save(ignore_permissions=True)
        updated += 1

    frappe.db.commit()
    print(
        f"Rebuilt payment_entry_list on {updated} HBL document(s) from Payment Entry Reference allocations."
    )
