// Copyright (c) 2026, Shaid Azmin and contributors
// For license information, please see license.txt
/* eslint-disable */

function operation_filter_list_query(fieldname) {
	return {
		query: "fastrack_erp.fastrack_erp.report.report_filters.get_filter_list",
		params: { fieldname: fieldname }
	};
}

frappe.query_reports["Operation"] = {
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
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("carrier")
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
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("shipper_name")
		},
		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("customer_name")
		},
		{
			"fieldname": "agent_name",
			"label": "Agent Name",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("agent_name")
		},
		{
			"fieldname": "mbl_consignee",
			"label": "Consignee",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("mbl_consignee")
		},
		{
			"fieldname": "notify_party",
			"label": "Notify Party",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("notify_party")
		},
		{
			"fieldname": "lc_no",
			"label": "L/C No.",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("lc_no")
		},
		{
			"fieldname": "mbl_no",
			"label": "MBL No.",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("mbl_no")
		},
		{
			"fieldname": "hbl_no",
			"label": "HBL No.",
			"fieldtype": "Autocomplete",
			"get_query": operation_filter_list_query("hbl_no")
		},
		{
			"fieldname": "inco_term",
			"label": "Inco Term",
			"fieldtype": "Select",
			"options": "\nPrepaid\nCollect\nFree Hand"
		},
	]
};
