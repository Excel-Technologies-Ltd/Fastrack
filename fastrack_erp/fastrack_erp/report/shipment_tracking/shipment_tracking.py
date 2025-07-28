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
    columns = get_columns_from_data(get_data(filters or {}))
    data = get_data(filters or {})
    return columns, data

def get_columns_from_data(data):
    """
    Generate columns dynamically from data fields.
    Args:
        data (list): List of dictionaries (rows).
    Returns:
        list: List of column definitions.
    """
    if not data:
        return []
    
    columns = []
    for field in data[0].keys():
        parts = field.split("_")
        if parts[0].lower() == "mbl":
            # Capitalize 'MBL' prefix, rest as title
            label = "MBL " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "fv":
            label = "FV " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "eta":
            label = "ETA " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "etd":
            label = "ETD " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "mv":
            label = "MV " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "hbl":
            label = "HBL " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "inv":
            label = "INV " + " ".join(p.title() for p in parts[1:])
        elif parts[0].lower() == "lc":
            label = "LC " + " ".join(p.title() for p in parts[1:])
        else:
            label = field.replace("_", " ").title()

        columns.append({
            "label": label,
            "fieldname": field,
            "fieldtype": "Data",  # You can add logic to infer type if needed
            "width": 200
        })
    return columns

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
                hbl.carrier,
                hbl.agent,
                mbl.shipper,
                hbl.mbl_no as mbl_no    ,
                hbl.mbl_date as mbl_date,
                hbl.hbl_id as hbl_no,
                hbl.hbl_date as date,
                hbl.name as link,
                hbl.reference_number,
                hbl.inco_term,
                hbl.total_container_hbl,
                hbl.hbl_shipper as shipper,
                hbl.hbl_consignee as consignee,
                hbl.notify_to as notify_party,
                hbl.customer as customer,
                hbl.lc,
                hbl.lc_date,
                GROUP_CONCAT(si.name ORDER BY si.posting_date) as inv_no,
                GROUP_CONCAT(si.posting_date ORDER BY si.posting_date) as inv_date,
                GROUP_CONCAT(cci.size, "⛌", cci.qty ORDER BY cci.size) as container_size,
                hbl.port_of_loading,
                hbl.port_of_delivery,
                hbl.port_of_discharge,
                hbl.mv,
                hbl.mv_voyage_no,
                hbl.fv,
                hbl.fv__v_no as fv_voyage_no,
                hbl.hbl_etd as etd,
                hbl.eta as eta,
                hbl.mbl_surrender_status,
                hbl.do_validity as do_date,
                hbl.total_purchase_amount as expense,
                hbl.total_invoice_amount as income,
                (hbl.total_invoice_amount - hbl.total_purchase_amount) as profit      
            FROM 
                `tabImport Sea House Bill` AS hbl
            LEFT JOIN `tabImport Sea Master Bill` as mbl ON mbl.name = hbl.mbl_link
            LEFT JOIN `tabSales Invoice` as si ON si.custom_hbl_sea_link = hbl.name
             LEFT JOIN `tabContainer Cost Info` as cci ON cci.parent = hbl.name
            WHERE 
                hbl.docstatus = 1 
                AND hbl.mbl_date BETWEEN %s AND %s
            GROUP BY
                hbl.name
        """, (from_date, to_date), as_dict=1)
        return data or []
    except Exception as e:
        frappe.msgprint(f"Error fetching sea shipment data: {str(e)}")
        frappe.log_error(f"Error fetching sea shipment data: {str(e)}")
        