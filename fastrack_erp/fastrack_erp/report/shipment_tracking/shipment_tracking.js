// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Shipment Tracking"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "shipment_type",
			"label": "Shipment Type",
			"fieldtype": "Select",
			"options": ["Import", "Export"],
			"default": "Import"
		},
		{
			"fieldname": "docu_type",
			"label": "DO Type",
			"fieldtype": "Select",
			"options": ["Air", "Sea", "Door"],
			"default": "Sea"
		},
	]
};
