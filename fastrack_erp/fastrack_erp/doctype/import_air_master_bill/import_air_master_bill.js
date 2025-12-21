// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import Air Master Bill', {
	refresh: function(frm) {
		frm.doc.mbl_open_by = frappe.session.user;
		frm.refresh_field('mbl_open_by');
	}
});
