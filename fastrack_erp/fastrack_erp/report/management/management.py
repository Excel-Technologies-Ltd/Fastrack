# Copyright (c) 2026, Shaid Azmin and contributors
# For license information, please see license.txt
#
# Wraps the GetManagmentReport stored procedure (Database/GetManagmentReport.sql),
# same pattern as the VAT report: filters/columns/data all come straight from
# the procedure, shared plumbing lives in report_filters.py.

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
        {"label": "Income (USD)", "fieldname": "Income USD", "fieldtype": "Currency", "width": 130},
        {"label": "Income (BDT)", "fieldname": "Income BDT", "fieldtype": "Currency", "width": 130},
        {"label": "Payment (USD)", "fieldname": "Payment USD", "fieldtype": "Currency", "width": 130},
        {"label": "Payment (BDT)", "fieldname": "Payment BDT", "fieldtype": "Currency", "width": 130},
        {"label": "Due (USD)", "fieldname": "Due USD", "fieldtype": "Currency", "width": 120},
        {"label": "Due (BDT)", "fieldname": "Due BDT", "fieldtype": "Currency", "width": 120},
        {"label": "Expense (BDT)", "fieldname": "Expense BDT", "fieldtype": "Currency", "width": 130},
        {"label": "Expense (USD)", "fieldname": "Expense USD", "fieldtype": "Currency", "width": 130},
        {"label": "Expense Payment (BDT)", "fieldname": "Expense Payment BDT", "fieldtype": "Currency", "width": 150},
        {"label": "Expense Payment (USD)", "fieldname": "Expense Payment USD", "fieldtype": "Currency", "width": 150},
        {"label": "Expense Due (USD)", "fieldname": "Expense Due USD", "fieldtype": "Currency", "width": 140},
        {"label": "Expense Due (BDT)", "fieldname": "Expense Due BDT", "fieldtype": "Currency", "width": 140},
        {"label": "Profit Share (USD)", "fieldname": "Profit Share USD", "fieldtype": "Currency", "width": 140},
        {"label": "Profit Share (BDT)", "fieldname": "Profit Share BDT", "fieldtype": "Currency", "width": 140},
        {"label": "GP (USD)", "fieldname": "GP USD", "fieldtype": "Currency", "width": 110},
        {"label": "GP (BDT)", "fieldname": "GP BDT", "fieldtype": "Currency", "width": 110},
        {"label": "Inco Term", "fieldname": "Inco Term", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    return call_procedure("GetManagmentReport", get_hbl_report_params(filters))
