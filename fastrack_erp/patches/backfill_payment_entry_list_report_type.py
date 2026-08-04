import frappe

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
    Backfill payment_type_for_report / amount_usd on Fastrack Payment Entry rows
    created before those fields existed, then recalculate the HBL total fields
    they feed (total_payment_received_usd/bdt, total_purchase_amount,
    total_payment_profit_share_usd/bdt).
    """
    rows = frappe.db.get_all(
        "Fastrack Payment Entry",
        filters={
            "payment_type_for_report": ["in", [None, ""]],
            "parenttype": ["in", HBL_DOCTYPES],
        },
        fields=["name", "parent", "parenttype", "payment_link"],
    )

    affected_parents = set()

    for row in rows:
        if not row.payment_link:
            continue

        pe = frappe.db.get_value(
            "Payment Entry",
            row.payment_link,
            [
                "custom_payment_type_for_report",
                "payment_type",
                "paid_from_account_currency",
                "paid_to_account_currency",
                "paid_amount",
                "received_amount",
                "base_paid_amount",
            ],
            as_dict=True,
        )
        if not pe:
            continue

        report_type = pe.custom_payment_type_for_report or pe.payment_type

        amount_usd = 0
        if pe.paid_from_account_currency == "USD":
            amount_usd = pe.paid_amount
        elif pe.paid_to_account_currency == "USD":
            amount_usd = pe.received_amount

        frappe.db.set_value(
            "Fastrack Payment Entry",
            row.name,
            {
                "payment_type_for_report": report_type,
                "amount_usd": amount_usd,
                "amount": pe.base_paid_amount,
            },
            update_modified=False,
        )
        affected_parents.add((row.parenttype, row.parent))

    for doctype, name in affected_parents:
        hbl_doc = frappe.get_doc(doctype, name)

        def total(report_type, field):
            return sum(
                float(r.get(field) or 0)
                for r in hbl_doc.payment_entry_list
                if r.payment_type_for_report == report_type
            )

        hbl_doc.total_payment_received_usd = total("Receive", "amount_usd")
        hbl_doc.total_payment_received_bdt = total("Receive", "amount")
        hbl_doc.total_purchase_amount = total("Pay", "amount")
        hbl_doc.total_payment_profit_share_usd = total("Profit Share", "amount_usd")
        hbl_doc.total_payment_profit_share_bdt = total("Profit Share", "amount")

        hbl_doc.flags.ignore_validate_update_after_submit = True
        hbl_doc.db_update()

    frappe.db.commit()
    print(
        f"Backfilled payment_type_for_report/amount_usd on {len(rows)} Fastrack Payment Entry "
        f"row(s) across {len(affected_parents)} HBL document(s)."
    )
