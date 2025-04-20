// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Master Bill', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Create House Bill'), function() {
			frappe.model.open_mapped_doc({
				method: "fastrack_erp.api.make_house_bill",
				frm: frm,
			});
		})
		}
	}
});