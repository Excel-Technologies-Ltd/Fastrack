// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shipping Order', {
	refresh: function(frm) {
		frm.add_custom_button(__('Download Shipping Order PDF'), function() {
			window.open(
				`/api/method/fastrack_erp.report_api.import_to_concern.download_shipping_order_pdf?doc_name=${encodeURIComponent(frm.doc.name)}`,
				'_blank'
			);
		}, __('Print'));
	},
});
