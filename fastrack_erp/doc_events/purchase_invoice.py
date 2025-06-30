import frappe

def after_submit(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        item_list = doc.items

        for idx, item in enumerate(item_list):
            # Create a child table row using frappe.get_doc
            row = frappe.new_doc("Fastrack Purchase Invoice")  # Replace with your actual child table doctype name
            
            # Set properties on the row
            row.invoice_link = doc.name 
            row.item_code = item.item_code
            row.qty = item.qty
            row.rate = item.net_rate
            row.amount = item.net_amount
            row.exchange_rate = item.custom_exchange_rate if item.custom_exchange_rate else None
            row.total_price = item.base_amount
            row.date = doc.posting_date 
            row.supplier = doc.supplier
            row.currency = doc.currency
            hbl_doc.append("purchase_invoice_list", row)
        
        hbl_doc.total_purchase_amount = sum(float(item.total_price) for item in hbl_doc.purchase_invoice_list)

        hbl_doc.save(ignore_permissions=True)
def on_cancel(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_shbl_id:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_shbl_id)
        for item in hbl_doc.purchase_invoice_list:
            if item.invoice_link == doc.name:
                hbl_doc.purchase_invoice_list.remove(item)
        hbl_doc.total_purchase_amount = sum(float(item.total_price) for item in hbl_doc.purchase_invoice_list)
        hbl_doc.save()