import frappe

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

    hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)
    hbl_doc.save(ignore_permissions=True)


def on_cancel(doc, method):
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

    for item in hbl_doc.profit_share_list:
        if item.journal_id == doc.name:
            hbl_doc.profit_share_list.remove(item)

    hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)
    hbl_doc.save()