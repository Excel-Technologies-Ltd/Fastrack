frappe.ui.form.on('Purchase Invoice', {
	refresh: function(frm) {
		ensure_save_button_for_hbl_mapped_draft(frm);
	},
});

function ensure_save_button_for_hbl_mapped_draft(frm) {
	if (!frm || !frm.doc || frm.doc.docstatus !== 0) return;

	const has_hbl_link =
		frm.doc.custom_shbl_id ||
		frm.doc.custom_ahbl_id ||
		frm.doc.custom_dhbl_id ||
		frm.doc.custom_export_hbl_sea_link ||
		frm.doc.custom_export_hbl_air_link ||
		frm.doc.custom_export_d2d_link;

	if (!has_hbl_link) return;
	frm.enable_save();
}
