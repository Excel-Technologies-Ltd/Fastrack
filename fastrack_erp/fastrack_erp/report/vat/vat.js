// Copyright (c) 2026, Shaid Azmin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["VAT"] = {
	"filters": [
		{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "import_export",
			"label": "Import/Export",
			"fieldtype": "Select",
			"options": "\nImport\nExport"
		},
		{
			"fieldname": "hbl_type",
			"label": "HBL Type",
			"fieldtype": "Select",
			"options": "\nImport Sea House Bill\nImport Air House Bill\nImport D2D Bill\nExport Sea House Bill\nExport Air House Bill\nExport D2D Bill"
		},
		{
			"fieldname": "carrier",
			"label": "Carrier",
			"fieldtype": "Data"
		},
		{
			"fieldname": "sales_person",
			"label": "Sales Person",
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "shipper_name",
			"label": "Shipper Name",
			"fieldtype": "Data"
		},
		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Data"
		},
		{
			"fieldname": "agent_name",
			"label": "Agent Name",
			"fieldtype": "Data"
		},
		{
			"fieldname": "mbl_consignee",
			"label": "MBL Consignee",
			"fieldtype": "Data"
		},
		{
			"fieldname": "notify_party",
			"label": "Notify Party",
			"fieldtype": "Data"
		},
		{
			"fieldname": "lc_no",
			"label": "L/C No.",
			"fieldtype": "Data"
		},
		{
			"fieldname": "mbl_no",
			"label": "MBL No.",
			"fieldtype": "Data"
		},
		{
			"fieldname": "hbl_no",
			"label": "HBL No.",
			"fieldtype": "Data"
		},
		{
			"fieldname": "inco_term",
			"label": "Inco Term",
			"fieldtype": "Select",
			"options": "\nPrepaid\nCollect\nFree Hand"
		},
	]
};
