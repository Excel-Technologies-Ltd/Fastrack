import frappe

# Map of HBL types to their link field names for Purchase Invoice
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
    item_list = doc.items

    for idx, item in enumerate(item_list):
        # Create a child table row
        row = frappe.new_doc("Fastrack Purchase Invoice")

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

    for item in hbl_doc.purchase_invoice_list:
        if item.invoice_link == doc.name:
            hbl_doc.purchase_invoice_list.remove(item)

    hbl_doc.total_purchase_amount = sum(float(item.total_price) for item in hbl_doc.purchase_invoice_list)
    hbl_doc.save()