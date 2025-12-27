import frappe

# Map of HBL types to their link field names
HBL_TYPE_FIELD_MAP = {
    "Import Sea House Bill": "custom_hbl_sea_link",
    "Import Air House Bill": "custom_hbl_air_link",
    "Import D2D Bill": "custom_hbl_d2d_link",
    "Export Sea House Bill": "custom_hbl_export_sea_link",
    "Export Air House Bill": "custom_hbl_export_air_link",
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
        row = frappe.new_doc("Fastrack Sales Invoice")

        # Set properties on the row
        row.invoice_link = doc.name
        row.item_code = item.item_code
        row.qty = item.qty
        row.rate = item.net_rate
        row.total_price = item.net_amount
        row.date = doc.posting_date
        row.customer = doc.customer
        row.currency = doc.currency
        row.exchange_rate = doc.conversion_rate
        row.base_net_rate = item.base_net_rate
        row.base_net_amount = item.base_net_amount
        hbl_doc.append("invoice_list", row)

    hbl_doc.total_invoice_amount = sum(float(item.base_net_amount) for item in hbl_doc.invoice_list)
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

    for item in hbl_doc.invoice_list:
        if item.invoice_link == doc.name:
            hbl_doc.invoice_list.remove(item)

    hbl_doc.total_invoice_amount = sum(float(item.base_net_amount) for item in hbl_doc.invoice_list)
    hbl_doc.save()