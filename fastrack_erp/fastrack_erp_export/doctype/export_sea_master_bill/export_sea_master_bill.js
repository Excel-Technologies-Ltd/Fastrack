// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export Sea Master Bill', {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("mbl_open_by",frappe.session.user);
		}

	}
});
