import frappe

HBL_DOCTYPES = [
    "Import Sea House Bill",
    "Import Air House Bill",
    "Import D2D Bill",
    "Export Sea House Bill",
    "Export Air House Bill",
    "Export D2D Bill",
    "Profit Share List",
]

# Map of HBL types to their link field names for Journal Entry
HBL_TYPE_FIELD_MAP = {
    "Import Sea House Bill": "custom_shbl_id",
    "Import Air House Bill": "custom_ahbl_id",
    "Import D2D Bill": "custom_dhbl_id",
    "Export Sea House Bill": "custom_eshbl_id",
    "Export Air House Bill": "custom_eahbl_id",
    "Export D2D Bill": "custom_edhbl_id",
}


def after_submit(doc, method):
    if not doc.custom_hbl_type:
        return

    # Get the link field for this HBL type
    link_field = HBL_TYPE_FIELD_MAP.get(doc.custom_hbl_type)
    if not link_field:
        return

    # Get the HBL link value
    hbl_link = doc.get(link_field)
    if not hbl_link:
        return

    # Get the HBL document
    hbl_doc = frappe.get_doc(doc.custom_hbl_type, hbl_link)

    # Not every HBL doctype stores a profit share list (e.g. D2D bills keep
    # profit share in Payment Entry) -- skip those instead of failing.
    if not hbl_doc.meta.has_field("profit_share_list"):
        return

    for account in doc.accounts:
        party_name = ""
        if account.party and account.party_type == "Customer":
            party_name = frappe.get_doc("Customer", account.party).customer_name
        elif account.party and account.party_type == "Supplier":
            party_name = frappe.get_doc("Supplier", account.party).supplier_name
        elif account.party and account.party_type == "Employee":
            party_name = frappe.get_doc("Employee", account.party).employee_name
        elif account.party and account.party_type == "Other":
            party_name = account.party

        account_info = {
            "journal_id": doc.name,
            "party_type": account.party_type,
            "party": party_name,
            "account_name": account.account,
            "credit": account.credit_in_account_currency if account.credit_in_account_currency else 0,
            "debit": account.debit_in_account_currency if account.debit_in_account_currency else 0,
            "amount": account.debit_in_account_currency if account.debit_in_account_currency else 0,
        }
        hbl_doc.append("profit_share_list", account_info)

    if hbl_doc.meta.has_field("total_profit_share"):
        hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)
    hbl_doc.flags.ignore_validate_update_after_submit = True
    hbl_doc.save(ignore_permissions=True)


def on_update_after_submit(doc, method):
    _remove_from_hbl_profit_share_list(doc)
    after_submit(doc, method)


def before_cancel(doc, method):
    doc.ignore_linked_doctypes = HBL_DOCTYPES
    _remove_from_hbl_profit_share_list(doc)


def on_cancel(doc, method):
    pass


def on_trash(doc, method):
    doc.ignore_linked_doctypes = HBL_DOCTYPES
    _remove_from_hbl_profit_share_list(doc)


def _remove_from_hbl_profit_share_list(doc):
    """Remove this journal's rows from every HBL that holds them, not just the
    one currently set on the journal (the link fields may have changed)."""
    affected = frappe.db.get_all(
        "Profit Share List",
        filters={"journal_id": doc.name},
        fields=["parent", "parenttype"],
        distinct=True,
    )

    all_affected = {(row.parenttype, row.parent) for row in affected}

    if doc.custom_hbl_type:
        link_field = HBL_TYPE_FIELD_MAP.get(doc.custom_hbl_type)
        if link_field and (hbl_link := doc.get(link_field)):
            all_affected.add((doc.custom_hbl_type, hbl_link))

    for parenttype, parent in all_affected:
        if not frappe.db.exists(parenttype, parent):
            continue

        hbl_doc = frappe.get_doc(parenttype, parent)
        if not hbl_doc.meta.has_field("profit_share_list"):
            continue

        hbl_doc.profit_share_list = [
            item for item in hbl_doc.profit_share_list if item.journal_id != doc.name
        ]

        if hbl_doc.meta.has_field("total_profit_share"):
            hbl_doc.total_profit_share = sum(float(item.amount or 0) for item in hbl_doc.profit_share_list)
        hbl_doc.flags.ignore_validate_update_after_submit = True
        hbl_doc.save(ignore_permissions=True)
