import frappe

def after_submit(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        hbl_doc.append("profit_share_list",{"journal_id":doc.name,"amount":doc.total_debit})
        
        
        hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.profit_share_list)

        hbl_doc.save(ignore_permissions=True)
def on_cancel(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        for item in hbl_doc.profit_share_list:
            if item.journal_id == doc.name:
                hbl_doc.profit_share_list.remove(item)
        hbl_doc.total_profit_share = sum(float(item.amount) for item in hbl_doc.invoice_list)
        hbl_doc.save()