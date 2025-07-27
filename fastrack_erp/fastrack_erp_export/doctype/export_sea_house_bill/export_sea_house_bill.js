// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export Sea House Bill', {
	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("hbl_open_by",frappe.session.user);
		}

	}
});
