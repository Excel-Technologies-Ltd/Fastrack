// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export Sea Master Bill', {
	refresh: function(frm) {
		frm.doc.mbl_open_by = frappe.session.user;
		frm.refresh_field('mbl_open_by');
	},
	onload: function(frm){
		if(frm.is_new()){
			frm.set_value("mbl_open_by",frappe.session.user)
		}
	}
});

// Child Table Logic: Export Sea HBL Info
frappe.ui.form.on('Export Sea HBL Info', {
	create_hbl: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if(frm.doc.docstatus!=1){
			return frappe.msgprint("MBL not submitted yet")
		}

		if(row.is_create){
			// route to view hbl
			frappe.set_route("Form", "Export Sea House Bill", row.hbl_link);
			return
		}

		frappe.call({
			method: "fastrack_erp.api.get_first_uncreated_hbl_info",
			args: {
				master_bill_no: frm.doc.name,
				doctype: frm.doc.doctype
			},
			callback: function (r) {
				if (r.message) {
					// match with current hbl name
					if (r.message.name == row.name) {
						frappe.model.open_mapped_doc({
							method: "fastrack_erp.api.make_export_sea_house_bill",
							frm: frm,
						});
					}
					else{
						frappe.msgprint("Create previous HBL first")
					}
				}
			}
		});
	},
});
