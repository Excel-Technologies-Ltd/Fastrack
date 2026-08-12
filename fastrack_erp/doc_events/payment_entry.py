from collections import defaultdict

import frappe

REPORT_BUCKETS = ("Receive", "Pay", "Profit Share")


def after_submit(doc, method):
    report_type = doc.custom_payment_type_for_report or doc.payment_type
    if report_type not in REPORT_BUCKETS:
        return

    for (hbl_type, hbl_no), totals in _group_references_by_hbl(doc).items():
        hbl_doc = frappe.get_doc(hbl_type, hbl_no)

        row = frappe.new_doc("Fastrack Payment Entry")
        row.payment_link = doc.name
        row.payment_type = doc.payment_type
        row.payment_type_for_report = report_type
        row.party = doc.party_name or doc.party
        row.amount_usd = totals["allocated_usd"]
        row.amount = totals["allocated_bdt"]
        row.exchange_gain_loss = totals["exchange_gain_loss"]
        hbl_doc.append("payment_entry_list", row)

        _recalculate_payment_totals(hbl_doc)
        hbl_doc.flags.ignore_validate_update_after_submit = True
        hbl_doc.save(ignore_permissions=True)


def _group_references_by_hbl(doc):
    """
    Group this Payment Entry's references (Payment Entry Reference rows) by
    the specific HBL each one is allocated against (its own
    custom_hbl_type / custom_hbl_no), summing the allocated USD/BDT amounts
    and exchange gain/loss within each HBL. A payment split across several
    HBLs -- or with more than one reference against the same HBL -- collapses
    to one entry per HBL.
    """
    groups = defaultdict(lambda: {"allocated_usd": 0.0, "allocated_bdt": 0.0, "exchange_gain_loss": 0.0})

    for ref in doc.references:
        if not ref.custom_hbl_type or not ref.custom_hbl_no:
            continue

        totals = groups[(ref.custom_hbl_type, ref.custom_hbl_no)]
        totals["allocated_usd"] += float(ref.allocated_amount or 0)
        totals["allocated_bdt"] += float(ref.custom_allocated_total_bdt or 0)
        totals["exchange_gain_loss"] += float(ref.exchange_gain_loss or 0)

    return groups


def on_cancel(doc, method):
    _remove_from_all_hbl_payment_lists(doc)


def on_trash(doc, method):
    _remove_from_all_hbl_payment_lists(doc)


def _remove_from_all_hbl_payment_lists(doc):
    """Remove this payment's rows from every HBL it was allocated to (there
    can be more than one), wherever they ended up -- rather than relying on
    doc.references, which may no longer reflect the state that was true at
    submit time."""
    affected = frappe.db.get_all(
        "Fastrack Payment Entry",
        filters={"payment_link": doc.name},
        fields=["parent", "parenttype"],
        distinct=True,
    )

    for row in affected:
        hbl_doc = frappe.get_doc(row.parenttype, row.parent)
        hbl_doc.payment_entry_list = [
            r for r in hbl_doc.payment_entry_list if r.payment_link != doc.name
        ]

        _recalculate_payment_totals(hbl_doc)
        hbl_doc.flags.ignore_validate_update_after_submit = True
        hbl_doc.save(ignore_permissions=True)


def _recalculate_payment_totals(hbl_doc):
    def total(report_type, field):
        return sum(
            float(row.get(field) or 0)
            for row in hbl_doc.payment_entry_list
            if row.payment_type_for_report == report_type
        )

    hbl_doc.total_payment_received_usd = total("Receive", "amount_usd")
    hbl_doc.total_payment_received_bdt = total("Receive", "amount")
    hbl_doc.total_pay_usd = total("Pay", "amount_usd")
    hbl_doc.total_pay_bdt = total("Pay", "amount")
    hbl_doc.total_exchange_gain_loss = total("Pay", "exchange_gain_loss")
    hbl_doc.total_payment_profit_share_usd = total("Profit Share", "amount_usd")
    hbl_doc.total_payment_profit_share_bdt = total("Profit Share", "amount")
