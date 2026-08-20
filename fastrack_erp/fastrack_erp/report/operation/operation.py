# Copyright (c) 2026, Shaid Azmin and contributors
# For license information, please see license.txt
#
# Wraps the GetOperationReport stored procedure (Database/GetOperationReport.sql),
# same pattern as the VAT/Management reports: filters/columns/data all come
# straight from the procedure, shared plumbing lives in report_filters.py.
#
# Note: the procedure's 10th parameter is named p_consignee (not
# p_mbl_consignee like VAT/Management/Master), but it's still the same
# position in the same 15-argument signature, so the shared
# get_hbl_report_params()/mbl_consignee filter still lines up correctly --
# only the label shown to the user differs (see operation.js).

from fastrack_erp.fastrack_erp.report.report_filters import get_hbl_report_params
from fastrack_erp.utils.db_procedures import call_procedure


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
        {"label": "Agent Name", "fieldname": "Agent Name", "fieldtype": "Data", "width": 160},
        {"label": "MBL Shipper", "fieldname": "MBL Shipper", "fieldtype": "Data", "width": 160},
        {"label": "Shipping Line", "fieldname": "Shipping Line", "fieldtype": "Data", "width": 150},
        {"label": "Customer Name", "fieldname": "Customer Name", "fieldtype": "Data", "width": 160},
        {"label": "Consignee", "fieldname": "Consignee", "fieldtype": "Data", "width": 160},
        {"label": "Notify Party", "fieldname": "Notify Party", "fieldtype": "Data", "width": 160},
        {"label": "L/C No.", "fieldname": "L/C No.", "fieldtype": "Data", "width": 120},
        {"label": "L/C Date", "fieldname": "L/C Date", "fieldtype": "Date", "width": 100},
        {"label": "MBL No.", "fieldname": "MBL No.", "fieldtype": "Data", "width": 130},
        {"label": "HBL No.", "fieldname": "HBL No.", "fieldtype": "Data", "width": 130},
        {"label": "Ref. No.", "fieldname": "Ref. No.", "fieldtype": "Data", "width": 110},
        {"label": "CI Number", "fieldname": "CI Number", "fieldtype": "Data", "width": 110},
        {"label": "POL", "fieldname": "POL", "fieldtype": "Data", "width": 120},
        {"label": "Port of Discharge", "fieldname": "Port of Discharge", "fieldtype": "Data", "width": 140},
        {"label": "Port of Delivery", "fieldname": "Port of Delivery", "fieldtype": "Data", "width": 140},
        {"label": "MV", "fieldname": "MV", "fieldtype": "Data", "width": 100},
        {"label": "MV Voyage No.", "fieldname": "MV Voyage No.", "fieldtype": "Data", "width": 120},
        {"label": "FV", "fieldname": "FV", "fieldtype": "Data", "width": 100},
        {"label": "FV Voyage No.", "fieldname": "FV Voyage No.", "fieldtype": "Data", "width": 120},
        {"label": "ETD", "fieldname": "ETD", "fieldtype": "Date", "width": 100},
        {"label": "ETA", "fieldname": "ETA", "fieldtype": "Date", "width": 100},
        {"label": "MBL Surrender", "fieldname": "MBL Surrender", "fieldtype": "Data", "width": 120},
        {"label": "DO Date", "fieldname": "DO Date", "fieldtype": "Date", "width": 100},
        {"label": "Container No.", "fieldname": "Container No.", "fieldtype": "Data", "width": 160},
        {"label": "Total Container", "fieldname": "Total Container", "fieldtype": "Float", "width": 110},
        {"label": "Freight Charge (USD)", "fieldname": "Freight Charge USD", "fieldtype": "Currency", "width": 140},
        {"label": "Freight Charge (BDT)", "fieldname": "Freight Charge BDT", "fieldtype": "Currency", "width": 140},
        {"label": "NOC (USD)", "fieldname": "NOC USD", "fieldtype": "Currency", "width": 110},
        {"label": "NOC (BDT)", "fieldname": "NOC BDT", "fieldtype": "Currency", "width": 110},
        {"label": "Others Income (USD)", "fieldname": "Others Income USD", "fieldtype": "Currency", "width": 150},
        {"label": "Others Income (BDT)", "fieldname": "Others Income BDT", "fieldtype": "Currency", "width": 150},
        {"label": "Inco Term", "fieldname": "Inco Term", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    return call_procedure("GetOperationReport", get_hbl_report_params(filters))
