# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
#
# Duplicate of erpnext.accounts.report.accounts_payable, reusing
# ArcApps Accounts Receivable's ReceivablePayableReport (it's generic on
# account_type) so the same USD-equivalent columns/conversion logic apply
# here without duplicating it.

from fastrack_erp.fastrack_erp.report.arcapps_accounts_receivable.arcapps_accounts_receivable import (
	ReceivablePayableReport,
)


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return ReceivablePayableReport(filters).run(args)
