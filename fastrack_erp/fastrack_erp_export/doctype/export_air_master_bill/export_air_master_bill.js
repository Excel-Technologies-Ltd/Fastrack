// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export Air Master Bill', {
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

// Child Table Logic: Export Air HBL Info
frappe.ui.form.on('Export Air HBL Info', {
	before_hbl_info_add: function(frm) {
		const total_hbl = frm.doc.total_no_of_hbl || 0;
		const actual_hbl = (frm.doc.hbl_info || []).length;

		if (actual_hbl >= total_hbl) {
			frappe.msgprint({
				title: __('HBL Limit Reached'),
				message: __('Cannot add more than {0} HBL(s). Please increase "Total No. of HBL" field to add more.', [total_hbl]),
				indicator: 'red'
			});
			return false;
		}
	},

	hbl_info_add: function(frm, cdt, cdn) {
		if (!validate_export_air_hbl_limit(frm)) {
			frm.get_field('hbl_info').grid.grid_rows_by_docname[cdn].remove();
		}
	},

	create_hbl: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if(frm.doc.docstatus!=1){
			return frappe.msgprint("MBL not submitted yet")
		}

		if(row.is_create){
			// route to view hbl
			frappe.set_route("Form", "Export Air House Bill", row.hbl_link);
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
							method: "fastrack_erp.api.make_export_air_house_bill",
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

// Helper function to validate HBL limit
function validate_export_air_hbl_limit(frm) {
	const total_hbl = frm.doc.total_no_of_hbl || 0;
	const actual_hbl = (frm.doc.hbl_info || []).length;

	if (actual_hbl > total_hbl) {
		frappe.msgprint({
			title: __('HBL Limit Exceeded'),
			message: __('Cannot add more than {0} HBL(s). Please increase "Total No. of HBL" field to add more.', [total_hbl]),
			indicator: 'red'
		});
		return false;
	}
	return true;
}
