import frappe

def after_submit(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_hbl_sea_link:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_hbl_sea_link)
        item_list = doc.items

        for idx, item in enumerate(item_list):
            # Create a child table row using frappe.get_doc
            row = frappe.new_doc("Fastrack Sales Invoice")  # Replace with your actual child table doctype name
            
            # Set properties on the row
            row.invoice_link = doc.name 
            row.item_code = item.item_code
            row.qty = item.qty
            row.rate = item.rate
            row.total_price = item.amount
            row.date = doc.posting_date if idx == 0 else ""
            row.customer = doc.customer if idx == 0 else ""
            hbl_doc.append("invoice_list", row)
        
        hbl_doc.total_invoice_amount = sum(float(item.total_price) for item in hbl_doc.invoice_list)

        hbl_doc.save(ignore_permissions=True)
def on_cancel(doc, method):
    if doc.custom_hbl_type == "Import Sea House Bill" and doc.custom_hbl_sea_link:
        hbl_doc = frappe.get_doc("Import Sea House Bill", doc.custom_hbl_sea_link)
        for item in hbl_doc.invoice_list:
            if item.invoice_link == doc.name:
                hbl_doc.invoice_list.remove(item)
        hbl_doc.total_invoice_amount = sum(float(item.total_price) for item in hbl_doc.invoice_list)
        hbl_doc.save()