// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export Air House Bill', {
	refresh: function(frm) {
		frm.doc.hbl_open_by = frappe.session.user;
		frm.refresh_field('hbl_open_by');
	}
});
