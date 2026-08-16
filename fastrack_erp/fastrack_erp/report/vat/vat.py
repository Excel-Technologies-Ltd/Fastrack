# Copyright (c) 2026, Shaid Azmin and contributors
# For license information, please see license.txt

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
    return call_procedure("GetVatReport", get_hbl_report_params(filters))
