import frappe

# Map of HBL types to their link field names for Payment Entry
HBL_TYPE_FIELD_MAP = {
    "Import Sea House Bill": "custom_hbl_sea_link",
    "Import Air House Bill": "custom_hbl_air_link",
    "Import D2D Bill": "custom_import_d2d_link",
    "Export Sea House Bill": "custom_export_hbl_sea_link",
    "Export Air House Bill": "custom_export_hbl_air_link",
    "Export D2D Bill": "custom_export_d2d_link",
}

REPORT_BUCKETS = ("Receive", "Pay", "Profit Share")


def after_submit(doc, method):
    report_type = doc.custom_payment_type_for_report or doc.payment_type
    if report_type not in REPORT_BUCKETS or not doc.custom_hbl_type:
        return

    link_field = HBL_TYPE_FIELD_MAP.get(doc.custom_hbl_type)
    if not link_field:
        return

    hbl_link = doc.get(link_field)
    if not hbl_link:
        return

    hbl_doc = frappe.get_doc(doc.custom_hbl_type, hbl_link)

    row = frappe.new_doc("Fastrack Payment Entry")
    row.payment_link = doc.name
    row.payment_type = doc.payment_type
    row.payment_type_for_report = report_type
    row.party = doc.party_name or doc.party
    row.amount_usd = _get_usd_amount(doc)
    row.amount = doc.base_paid_amount
    hbl_doc.append("payment_entry_list", row)

    _recalculate_payment_totals(hbl_doc)
    hbl_doc.flags.ignore_validate_update_after_submit = True
    hbl_doc.save(ignore_permissions=True)


def on_cancel(doc, method):
    _remove_from_hbl_payment_list(doc)


def on_trash(doc, method):
    _remove_from_hbl_payment_list(doc)


def _remove_from_hbl_payment_list(doc):
    if not doc.custom_hbl_type:
        return

    link_field = HBL_TYPE_FIELD_MAP.get(doc.custom_hbl_type)
    if not link_field:
        return

    hbl_link = doc.get(link_field)
    if not hbl_link:
        return

    hbl_doc = frappe.get_doc(doc.custom_hbl_type, hbl_link)

    hbl_doc.payment_entry_list = [
        row for row in hbl_doc.payment_entry_list if row.payment_link != doc.name
    ]

    _recalculate_payment_totals(hbl_doc)
    hbl_doc.flags.ignore_validate_update_after_submit = True
    hbl_doc.save(ignore_permissions=True)


def _get_usd_amount(doc):
    if doc.paid_from_account_currency == "USD":
        return doc.paid_amount
    if doc.paid_to_account_currency == "USD":
        return doc.received_amount
    return 0


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
    hbl_doc.total_purchase_amount = total("Pay", "amount")
    hbl_doc.total_payment_profit_share_usd = total("Profit Share", "amount_usd")
    hbl_doc.total_payment_profit_share_bdt = total("Profit Share", "amount")
