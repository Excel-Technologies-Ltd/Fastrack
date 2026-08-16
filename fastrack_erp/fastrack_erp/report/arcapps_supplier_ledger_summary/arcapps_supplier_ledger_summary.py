# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
#
# Duplicate of erpnext.accounts.report.supplier_ledger_summary, reusing
# ArcApps Customer Ledger Summary's PartyLedgerSummaryReport (it's generic
# on party_type) so the same USD-equivalent columns/conversion logic apply
# here without duplicating them.

from fastrack_erp.fastrack_erp.report.arcapps_customer_ledger_summary.arcapps_customer_ledger_summary import (
	PartyLedgerSummaryReport,
)


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return PartyLedgerSummaryReport(filters).run(args)
