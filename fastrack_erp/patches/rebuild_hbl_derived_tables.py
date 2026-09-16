import frappe

# Every HBL doctype and the doctypes it can pull derived rows from.
HBL_DOCTYPES = [
    "Import Sea House Bill",
    "Import Air House Bill",
    "Import D2D Bill",
    "Export Sea House Bill",
    "Export Air House Bill",
    "Export D2D Bill",
]

# HBL type -> link field on Sales Invoice
SI_LINK_FIELD_MAP = {
    "Import Sea House Bill": "custom_hbl_sea_link",
    "Import Air House Bill": "custom_hbl_air_link",
    "Import D2D Bill": "custom_import_d2d_link",
    "Export Sea House Bill": "custom_export_hbl_sea_link",
    "Export Air House Bill": "custom_export_hbl_air_link",
    "Export D2D Bill": "custom_export_d2d_link",
}

# HBL type -> link field on Purchase Invoice
PI_LINK_FIELD_MAP = {
    "Import Sea House Bill": "custom_shbl_id",
    "Import Air House Bill": "custom_hbl_air_link",
    "Import D2D Bill": "custom_import_d2d_link",
    "Export Sea House Bill": "custom_export_hbl_sea_link",
    "Export Air House Bill": "custom_export_hbl_air_link",
    "Export D2D Bill": "custom_export_d2d_link",
}

# HBL type -> link field on Journal Entry (only types that hold a profit share
# list AND expose a link column on Journal Entry can be rebuilt from JEs;
# Export Air / Export D2D have no such column on the DB, so skip them).
JE_LINK_FIELD_MAP = {
    "Import Sea House Bill": "custom_shbl_id",
    "Import Air House Bill": "custom_ahbl_id",
    "Import D2D Bill": "custom_dhbl_id",
    "Export Sea House Bill": "custom_eshbl_id",
}

# Columns on Journal Entry whose existence we confirm before querying, so the
# patch does not crash on installations where not every column shipped.
JE_COLUMNS = ["custom_shbl_id", "custom_ahbl_id", "custom_dhbl_id", "custom_eshbl_id"]


def execute():
    updated = 0

    for hbl_type in HBL_DOCTYPES:
        if not frappe.db.exists("DocType", hbl_type):
            continue
        meta = frappe.get_meta(hbl_type)

        si_link = SI_LINK_FIELD_MAP.get(hbl_type)
        pi_link = PI_LINK_FIELD_MAP.get(hbl_type)
        je_link = JE_LINK_FIELD_MAP.get(hbl_type)
        if je_link and not frappe.db.has_column("Journal Entry", je_link):
            je_link = None

        for name in _submitted_hbl_names(hbl_type):
            hbl_doc = frappe.get_doc(hbl_type, name)
            changed = False

            if meta.has_field("invoice_list") and si_link:
                changed |= _rebuild_invoice_rows(hbl_doc, si_link)
            if meta.has_field("vat_list") and si_link:
                changed |= _rebuild_vat_rows(hbl_doc)
            if meta.has_field("purchase_invoice_list") and pi_link:
                changed |= _rebuild_purchase_rows(hbl_doc, pi_link)
            if meta.has_field("profit_share_list") and je_link:
                changed |= _rebuild_profit_share_rows(hbl_doc, je_link)

            if not changed:
                continue

            _recalculate_totals(hbl_doc)
            hbl_doc.flags.ignore_validate_update_after_submit = True
            hbl_doc.save(ignore_permissions=True)
            updated += 1

    frappe.db.commit()
    print(
        f"Rebuilt invoice/VAT/purchase/profit-share lists and totals on "
        f"{updated} HBL document(s) from their linked Sales Invoices, "
        f"Purchase Invoices and Journal Entries."
    )


def _submitted_hbl_names(hbl_type):
    return [
        r[0]
        for r in frappe.db.sql(
            "SELECT name FROM `tab{0}` WHERE docstatus = 1".format(hbl_type)
        )
    ]


def _rebuild_invoice_rows(hbl_doc, si_link):
    rows = frappe.db.sql(
        """
        SELECT si.name, si.posting_date, si.customer, si.currency, si.conversion_rate
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1 AND si.`{0}` IS NOT NULL AND si.`{0}` = %s
        ORDER BY si.name
        """.format(si_link),
        hbl_doc.name,
        as_dict=True,
    )

    new_rows = []
    for si in rows:
        items = frappe.db.sql(
            """
            SELECT item_code, qty, uom, net_rate, net_amount,
                   base_net_rate, base_net_amount
            FROM `tabSales Invoice Item`
            WHERE parent = %s
            """,
            si.name,
            as_dict=True,
        )
        for item in items:
            new_rows.append(
                {
                    "invoice_link": si.name,
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "rate": item.net_rate,
                    "total_price": item.net_amount,
                    "date": si.posting_date,
                    "customer": si.customer,
                    "currency": si.currency,
                    "exchange_rate": si.conversion_rate,
                    "base_net_rate": item.base_net_rate,
                    "base_net_amount": item.base_net_amount,
                }
            )

    if not new_rows:
        return False
    if _rows_equal(hbl_doc, "invoice_list", new_rows):
        return False
    _wipe_child(hbl_doc, "invoice_list")
    for row in new_rows:
        hbl_doc.append("invoice_list", row)
    return True


def _rebuild_vat_rows(hbl_doc):
    if not hbl_doc.meta.has_field("vat_list"):
        return False

    existing_invoices = {
        row.invoice_link for row in hbl_doc.invoice_list if row.invoice_link
    }
    new_rows = []
    for invoice in sorted(existing_invoices):
        vat = frappe.db.get_value(
            "Sales Invoice",
            invoice,
            ["total_taxes_and_charges", "base_total_taxes_and_charges"],
        )
        vat_usd, vat_bdt = vat or (0, 0)
        new_rows.append(
            {
                "invoice_no": invoice,
                "vat_amount_usd": vat_usd or 0,
                "vat_amount_bdt": vat_bdt or 0,
            }
        )

    if not new_rows:
        return False
    if _rows_equal(hbl_doc, "vat_list", new_rows):
        return False
    _wipe_child(hbl_doc, "vat_list")
    for row in new_rows:
        hbl_doc.append("vat_list", row)
    return True


def _rebuild_purchase_rows(hbl_doc, pi_link):
    rows = frappe.db.sql(
        """
        SELECT pi.name, pi.posting_date, pi.supplier, pi.currency
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1 AND pi.`{0}` IS NOT NULL AND pi.`{0}` = %s
        ORDER BY pi.name
        """.format(pi_link),
        hbl_doc.name,
        as_dict=True,
    )

    new_rows = []
    for pi in rows:
        items = frappe.db.sql(
            """
            SELECT item_code, qty, net_rate, base_net_rate, net_amount,
                   base_amount, custom_exchange_rate
            FROM `tabPurchase Invoice Item`
            WHERE parent = %s
            """,
            pi.name,
            as_dict=True,
        )
        for item in items:
            new_rows.append(
                {
                    "invoice_link": pi.name,
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.net_rate,
                    "base_rate": item.base_net_rate,
                    "amount": item.net_amount,
                    "exchange_rate": item.custom_exchange_rate or None,
                    "total_price": item.base_amount,
                    "date": pi.posting_date,
                    "supplier": pi.supplier,
                    "currency": pi.currency,
                }
            )

    if not new_rows:
        return False
    if _rows_equal(hbl_doc, "purchase_invoice_list", new_rows):
        return False
    _wipe_child(hbl_doc, "purchase_invoice_list")
    for row in new_rows:
        hbl_doc.append("purchase_invoice_list", row)
    return True


def _rebuild_profit_share_rows(hbl_doc, je_link):
    jes = frappe.db.sql(
        """
        SELECT name FROM `tabJournal Entry`
        WHERE docstatus = 1 AND `{0}` IS NOT NULL AND `{0}` = %s
        ORDER BY name
        """.format(je_link),
        hbl_doc.name,
    )
    if not jes:
        return False

    new_rows = []
    for (je_name,) in jes:
        accounts = frappe.db.sql(
            """
            SELECT party_type, party, account,
                   credit_in_account_currency, debit_in_account_currency
            FROM `tabJournal Entry Account`
            WHERE parent = %s
            """,
            je_name,
            as_dict=True,
        )
        for acc in accounts:
            new_rows.append(
                {
                    "journal_id": je_name,
                    "party_type": acc.party_type,
                    "party": _resolve_party_name(acc.party_type, acc.party),
                    "account_name": acc.account,
                    "credit": acc.credit_in_account_currency or 0,
                    "debit": acc.debit_in_account_currency or 0,
                    "amount": acc.debit_in_account_currency or 0,
                }
            )

    if not new_rows:
        return False
    if _rows_equal(hbl_doc, "profit_share_list", new_rows):
        return False
    _wipe_child(hbl_doc, "profit_share_list")
    for row in new_rows:
        hbl_doc.append("profit_share_list", row)
    return True


def _resolve_party_name(party_type, party):
    if not party:
        return ""
    if party_type == "Customer":
        return frappe.db.get_value("Customer", party, "customer_name") or party
    if party_type == "Supplier":
        return frappe.db.get_value("Supplier", party, "supplier_name") or party
    if party_type == "Employee":
        return frappe.db.get_value("Employee", party, "employee_name") or party
    return party


def _recalculate_totals(hbl_doc):
    if hbl_doc.meta.has_field("invoice_amount_usd"):
        hbl_doc.invoice_amount_usd = sum(
            float(x.total_price or 0) for x in hbl_doc.invoice_list
        )
    if hbl_doc.meta.has_field("invoice_amount_bdt"):
        hbl_doc.invoice_amount_bdt = sum(
            float(x.base_net_amount or 0) for x in hbl_doc.invoice_list
        )
    if hbl_doc.meta.has_field("vat_amount_usd"):
        hbl_doc.vat_amount_usd = sum(
            float(x.vat_amount_usd or 0) for x in hbl_doc.vat_list
        )
    if hbl_doc.meta.has_field("vat_amount_bdt"):
        hbl_doc.vat_amount_bdt = sum(
            float(x.vat_amount_bdt or 0) for x in hbl_doc.vat_list
        )
    if hbl_doc.meta.has_field("total_invoice_amount_usd"):
        hbl_doc.total_invoice_amount_usd = (
            float(hbl_doc.invoice_amount_usd or 0) + float(hbl_doc.vat_amount_usd or 0)
        )
    if hbl_doc.meta.has_field("total_invoice_amount"):
        hbl_doc.total_invoice_amount = (
            float(hbl_doc.invoice_amount_bdt or 0) + float(hbl_doc.vat_amount_bdt or 0)
        )
    if hbl_doc.meta.has_field("expense_amount_usd"):
        hbl_doc.expense_amount_usd = sum(
            float(x.amount or 0) for x in hbl_doc.purchase_invoice_list
        )
    if hbl_doc.meta.has_field("expense_amount_bdt"):
        hbl_doc.expense_amount_bdt = sum(
            float(x.total_price or 0) for x in hbl_doc.purchase_invoice_list
        )
    if hbl_doc.meta.has_field("total_profit_share"):
        hbl_doc.total_profit_share = sum(
            float(x.amount or 0) for x in hbl_doc.profit_share_list
        )


def _wipe_child(hbl_doc, table):
    while hbl_doc.get(table):
        hbl_doc.get(table).pop()


def _rows_equal(hbl_doc, table, expected):
    current = hbl_doc.get(table)
    if len(current) != len(expected):
        return False
    sample = []
    for row in expected:
        sample.append(sorted(str(row.get(f)) for f in row))
    got = []
    for row in current:
        keys = [f.fieldname for f in row.meta.fields if f.fieldname in expected[0]]
        got.append(sorted(str(row.get(f)) for f in keys))
    return sorted(got) == sorted([
        sorted(str(r.get(f)) for f in expected[0]) for r in expected
    ])
