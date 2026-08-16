# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
#
# Duplicate of erpnext.accounts.report.accounts_payable_summary, reusing
# ArcApps Accounts Receivable Summary's AccountsReceivableSummary (it's
# generic on account_type) so the same USD-equivalent columns apply here
# without duplicating them.

from fastrack_erp.fastrack_erp.report.arcapps_accounts_receivable_summary.arcapps_accounts_receivable_summary import (
	AccountsReceivableSummary,
)


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return AccountsReceivableSummary(filters).run(args)
