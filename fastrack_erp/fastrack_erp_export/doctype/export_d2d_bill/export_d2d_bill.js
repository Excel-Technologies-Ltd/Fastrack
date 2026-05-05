// Copyright (c) 2026, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Export D2D Bill', {
     eta: function(frm) {
        if (frm.doc.eta && frm.doc.etd && frm.doc.eta < frm.doc.etd) {
                frappe.msgprint({
                    title: __('Invalid ETA Date'),
                    message: __('ETA date cannot be before ETD Date.'),
                    indicator: 'red'
                });
                frm.set_value('eta', null);
            }
    },
	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Sales Invoice"), function () {
                open_mapped_with_save_fix(
                    frm,
                    "fastrack_erp.api.make_sales_invoice_from_hbl"
                );
            }, __("Create"));

            frm.add_custom_button(__("Expense"), function () {
                open_mapped_with_save_fix(
                    frm,
                    "fastrack_erp.api.make_purchase_invoice_from_hbl"
                );
            }, __("Create"));

            frm.add_custom_button(__("Profit Share"), function () {
                frappe.new_doc("Payment Entry");
            }, __("Create"));

            frm.add_custom_button(__("Payment Entry"), function () {
                open_mapped_with_save_fix(
                    frm,
                    "fastrack_erp.api.make_payment_entry_from_hbl"
                );
            }, __("Create"));
        }

	}
});

function open_mapped_with_save_fix(frm, method) {
    frappe.model.open_mapped_doc({
        method: method,
        frm: frm,
    });
    setTimeout(() => {
        const target = cur_frm;
        if (!target || target.doc.docstatus !== 0) return;
        if (
            ['Sales Invoice', 'Purchase Invoice', 'Payment Entry'].includes(
                target.doctype
            )
        ) {
            target.enable_save();
        }
    }, 400);
}
