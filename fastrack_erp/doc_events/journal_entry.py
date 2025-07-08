import frappe

def after_submit(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        for account in doc.accounts:
            party_name=""
            if account.party and account.party_type=="Customer":
                party_name=frappe.get_doc("Customer",account.party).customer_name
            elif account.party and account.party_type=="Supplier":
                party_name=frappe.get_doc("Supplier",account.party).supplier_name
            elif account.party and account.party_type=="Employee":
                party_name=frappe.get_doc("Employee",account.party).employee_name
            elif account.party and account.party_type=="Other":
                party_name=account.party
            account_info={
                "journal_id":doc.name,
                "party_type":account.party_type,
                "party":party_name,
                "account_name":account.account,
                "credit":account.credit_in_account_currency if account.credit_in_account_currency else 0,
                "debit":account.debit_in_account_currency if account.debit_in_account_currency else 0,
                "amount":account.debit_in_account_currency if account.debit_in_account_currency else 0,
            }
            hbl_doc.append("profit_share_list",account_info)
        
        
        hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)

        hbl_doc.save(ignore_permissions=True)
def on_cancel(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        for item in hbl_doc.profit_share_list:
            if item.journal_id == doc.name:
                hbl_doc.profit_share_list.remove(item)
        hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)
        hbl_doc.save()