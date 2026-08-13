# Copyright (c) 2026, Shaid Azmin and contributors
# For license information, please see license.txt

import json

import frappe
import pymysql

# Order must match GetVatReport's parameter list exactly.
FILTER_PARAMS = [
    "start_date",
    "end_date",
    "import_export",
    "hbl_type",
    "carrier",
    "sales_person",
    "shipper_name",
    "customer_name",
    "agent_name",
    "mbl_consignee",
    "notify_party",
    "lc_no",
    "mbl_no",
    "hbl_no",
    "inco_term",
]

# Report filter fieldname -> the "...ByName" search/suggest procedure backing
# its Autocomplete dropdown (Database/<name>.sql). All of them share the same
# (p_search, p_page, p_page_size) signature and the same
# {"data": [...], "pagination": {...}} JSON result shape.
FILTER_LIST_PROCEDURES = {
    "carrier": "GetCarrierListByName",
    "shipper_name": "GetShipperByName",
    "customer_name": "GetCustomerByName",
    "agent_name": "GetAgentByName",
    "mbl_consignee": "GetMblConsigneeByName",
    "notify_party": "GetNotifyPartyByName",
    "lc_no": "GetLcNoByName",
    "mbl_no": "GetMblNoByName",
    "hbl_no": "GetHblNoByName",
}


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Import/Export", "fieldname": "Import/Export", "fieldtype": "Data", "width": 100},
        {"label": "HBL Type", "fieldname": "HBL Type", "fieldtype": "Data", "width": 170},
        {"label": "Carrier", "fieldname": "Carrier", "fieldtype": "Data", "width": 150},
        {"label": "Sales Person", "fieldname": "Sales Person", "fieldtype": "Data", "width": 130},
        {"label": "Shipper Name", "fieldname": "Shipper Name", "fieldtype": "Data", "width": 160},
        {"label": "Customer Name", "fieldname": "Customer Name", "fieldtype": "Data", "width": 160},
        {"label": "Agent Name", "fieldname": "Agent Name", "fieldtype": "Data", "width": 160},
        {"label": "Notify Party", "fieldname": "Notify Party", "fieldtype": "Data", "width": 160},
        {"label": "MBL Consignee", "fieldname": "MBL Consignee", "fieldtype": "Data", "width": 160},
        {"label": "L/C No.", "fieldname": "L/C No.", "fieldtype": "Data", "width": 120},
        {"label": "L/C Date", "fieldname": "L/C Date", "fieldtype": "Date", "width": 100},
        {"label": "MBL No.", "fieldname": "MBL No.", "fieldtype": "Data", "width": 130},
        {"label": "HBL No.", "fieldname": "HBL No.", "fieldtype": "Data", "width": 130},
        {"label": "ETD", "fieldname": "ETD", "fieldtype": "Date", "width": 100},
        {"label": "ETA", "fieldname": "ETA", "fieldtype": "Date", "width": 100},
        {"label": "Freight Charge (BDT)", "fieldname": "Freight Charge BDT", "fieldtype": "Currency", "width": 140},
        {"label": "Freight Charge (USD)", "fieldname": "Freight Charge USD", "fieldtype": "Currency", "width": 140},
        {"label": "Service Commission (BDT)", "fieldname": "Service Commission BDT", "fieldtype": "Currency", "width": 160},
        {"label": "Service Commission (USD)", "fieldname": "Service Commission USD", "fieldtype": "Currency", "width": 160},
        {"label": "NOC (BDT)", "fieldname": "NOC BDT", "fieldtype": "Currency", "width": 110},
        {"label": "NOC (USD)", "fieldname": "NOC USD", "fieldtype": "Currency", "width": 110},
        {"label": "Others Income (BDT)", "fieldname": "Others Income BDT", "fieldtype": "Currency", "width": 150},
        {"label": "Others Income (USD)", "fieldname": "Others Income USD", "fieldtype": "Currency", "width": 150},
        {"label": "VAT (BDT)", "fieldname": "VAT (BDT)", "fieldtype": "Currency", "width": 110},
        {"label": "VAT (USD)", "fieldname": "VAT (USD)", "fieldtype": "Currency", "width": 110},
        {"label": "Inco Term", "fieldname": "Inco Term", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    params = [filters.get(key) or None for key in FILTER_PARAMS]
    return _call_procedure("GetVatReport", params)


@frappe.whitelist()
def get_filter_list(fieldname, txt=None, **kwargs):
    """Autocomplete suggestions for one of the report's *ByName-backed
    filters (see FILTER_LIST_PROCEDURES) -- used as vat.js's get_query
    source. Accepts/ignores stray kwargs since the Autocomplete control's
    query call always includes a `query` arg (its own method path)
    alongside `txt`."""
    procedure = FILTER_LIST_PROCEDURES.get(fieldname)
    if not procedure:
        frappe.throw(f"No filter list procedure registered for {fieldname!r}")

    rows = _call_procedure(procedure, [txt or None, 1, 50])
    if not rows:
        return []

    result = rows[0]["Result"]
    result = json.loads(result) if isinstance(result, str) else result
    values = result.get("data") or []

    return [{"value": v, "description": ""} for v in values]


def _call_procedure(name, params):
    placeholders = ", ".join(["%s"] * len(params))

    # A stored procedure's own SELECTs return normally, but a MySQL CALL
    # always leaves an extra "procedure status" result set behind on the
    # connection afterwards. frappe.db.sql() only reads the first result
    # set and never drains that trailing one, which then makes every later
    # query on that same shared connection fail with "Commands out of
    # sync". Use a separate, throwaway connection (built from frappe's own
    # settings) so the stored procedure call can't corrupt the connection
    # the rest of the request relies on.
    connection = frappe.db.create_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"CALL {name}({placeholders})", params)
            data = cursor.fetchall()
            while cursor.nextset():
                pass
        return data
    finally:
        connection.close()
