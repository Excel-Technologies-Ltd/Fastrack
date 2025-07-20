# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """
    Execute function for the report, returns columns and data based on filters.
    
    Args:
        filters (dict): Filters containing shipment_type, from_date, and to_date.
    
    Returns:
        tuple: (columns, data)
    """
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data

def get_columns():
    """
    Define the column structure for the report.
    
    Returns:
        list: List of column definitions.
    """
    return [
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 120
        },
        {
            "label": _("MBL Link"),
            "fieldname": "mbl_link",
            "fieldtype": "Link",
            "options": "Import Sea Master Bill",
            "width": 120
        },
        {
            "label": _("MBL No"),
            "fieldname": "mbl_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("HBL No"),
            "fieldname": "hbl_id",
            "fieldtype": "Link",
            "options": "Import Sea House Bill",
            "width": 120
        },
        {
            "label": _("MBL Date"),
            "fieldname": "mbl_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("HBL Date"),
            "fieldname": "hbl_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Reference Number"),
            "fieldname": "reference_number",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Shipper"),
            "fieldname": "hbl_shipper",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "label": _("Consignee"),
            "fieldname": "hbl_consignee",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        {
            "label": _("Agent"),
            "fieldname": "agent",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "label": _("LC"),
            "fieldname": "lc",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("POL"),
            "fieldname": "port_of_loading",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("POD"),
            "fieldname": "port_of_delivery",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Vol CBM"),
            "fieldname": "hbl_vol_cbm",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("ETD"),
            "fieldname": "hbl_etd",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("ETA"),
            "fieldname": "eta",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("DOO"),
            "fieldname": "do_party",
            "fieldtype": "Data",
            "width": 120
        }
    ]

def get_data(filters):
    """
    Fetch data based on the provided filters.
    
    Args:
        filters (dict): Filters containing shipment_type, from_date, and to_date.
    
    Returns:
        list: List of data rows.
    """
    if not filters.get("shipment_type"):
        frappe.throw(_("Shipment Type is required."))
    
    shipment_type = filters.get("shipment_type")
    
    if shipment_type == "Export":
        frappe.msgprint(_("coming soon."))
        return []
    elif shipment_type == "Import":
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        
        if not from_date or not to_date:
            frappe.throw(_("From Date and To Date are required for Sea shipment."))
        
        if from_date > to_date:
            frappe.throw(_("From Date cannot be after To Date."))
        if filters.get("docu_type") == "Air":
            frappe.msgprint(_("coming soon."))
            return []
        if filters.get("docu_type") == "Sea":
            return get_sea_import_data(from_date, to_date)
        if filters.get("docu_type") == "Door":
            frappe.msgprint(_("coming soon."))
            return []
        else:
            frappe.msgprint(_("Unsupported DO Type: {0}").format(filters.get("docu_type")))
            return []
    else:
        frappe.msgprint(_("Unsupported shipment type: {0}").format(shipment_type))
        return []

def get_sea_import_data(from_date, to_date):
    """
    Fetch sea shipment data from the database.
    
    Args:
        from_date (str): Start date for filtering.
        to_date (str): End date for filtering.
    
    Returns:
        list: List of dictionaries containing sea shipment data.
    """
    try:
        data = frappe.db.sql("""
            SELECT 
                "Import" AS shipment_type,
                 hbl.sales_person,
                hbl.hbl_open_by,
                hbl.mbl_link,
                hbl.mbl_no,
                hbl.hbl_id,
                hbl.mbl_date,
                hbl.hbl_date,
                hbl.reference_number,
                hbl.hbl_shipper ,
                hbl.hbl_consignee ,
                hbl.agent,
                hbl.lc,
                hbl.port_of_loading,
                hbl.port_of_delivery,
                hbl.hbl_vol_cbm,
                hbl.hbl_etd,
                hbl.eta,
                hbl.do_party,
               
                
            FROM 
                `tabImport Sea House Bill` AS hbl
            WHERE 
                hbl.docstatus = 1 
                AND hbl.mbl_date BETWEEN %s AND %s
        """, (from_date, to_date), as_dict=1)
        return data or []
    except Exception as e:
        frappe.msgprint(f"Error fetching sea shipment data: {str(e)}")
        frappe.log_error(f"Error fetching sea shipment data: {str(e)}")
        