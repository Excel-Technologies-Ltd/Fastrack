# Copyright (c) 2026, Shaid Azmin and contributors
# For license information, please see license.txt
#
# Shared filter plumbing for the stored-procedure-backed HBL reports (VAT,
# Management, ...): they all take the same 15 filters in the same order,
# and the free-text ones are all backed by the same style of "...ByName"
# search/suggest procedure. Centralized here so each report's .py only
# needs its own columns and its own report procedure name.

import json

import frappe

from fastrack_erp.utils.db_procedures import call_procedure

# Order must match GetVatReport / GetManagmentReport's parameter list
# exactly -- both share this same signature.
HBL_REPORT_FILTER_PARAMS = [
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


def get_hbl_report_params(filters):
	"""Build the positional CALL argument list for GetVatReport /
	GetManagmentReport from a report's filters dict."""
	return [filters.get(key) or None for key in HBL_REPORT_FILTER_PARAMS]


@frappe.whitelist()
def get_filter_list(fieldname, txt=None, **kwargs):
	"""Autocomplete suggestions for one of the *ByName-backed filters (see
	FILTER_LIST_PROCEDURES) -- used as the Autocomplete get_query source in
	both vat.js and management.js. Accepts/ignores stray kwargs since the
	Autocomplete control's query call always includes a `query` arg (its
	own method path) alongside `txt`."""
	procedure = FILTER_LIST_PROCEDURES.get(fieldname)
	if not procedure:
		frappe.throw(f"No filter list procedure registered for {fieldname!r}")

	rows = call_procedure(procedure, [txt or None, 1, 50])
	if not rows:
		return []

	result = rows[0]["Result"]
	result = json.loads(result) if isinstance(result, str) else result
	values = result.get("data") or []

	return [{"value": v, "description": ""} for v in values]
