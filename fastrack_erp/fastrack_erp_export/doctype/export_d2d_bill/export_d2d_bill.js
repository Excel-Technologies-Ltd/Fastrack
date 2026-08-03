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
		// Auto-populate vat_list with any invoice_link not yet represented, then recalc totals
		sync_vat_list_with_invoices(frm);
		calculate_invoice_totals(frm);

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

// Add a vat_list row for every unique invoice_link in invoice_list that doesn't already have one
function sync_vat_list_with_invoices(frm) {
    // VAT List rows are auto-generated from invoice_list; block manual add
    if (frm.fields_dict.vat_list) {
        frm.fields_dict.vat_list.grid.cannot_add_rows = true;
        frm.fields_dict.vat_list.grid.refresh();
    }

    if (!frm.doc.invoice_list || frm.doc.invoice_list.length === 0) return;

    const unique_invoices = [...new Set(
        frm.doc.invoice_list
            .map(row => row.invoice_link)
            .filter(id => id)
    )];

    const existing_vats = (frm.doc.vat_list || []).map(row => row.invoice_no);

    let is_updated = false;
    unique_invoices.forEach(invoice_link => {
        if (!existing_vats.includes(invoice_link)) {
            const new_row = frm.add_child("vat_list");
            new_row.invoice_no = invoice_link;
            is_updated = true;
        }
    });

    if (is_updated) {
        frm.refresh_field("vat_list");
    }
}

// Sum invoice_list / vat_list child tables into the USD and BDT invoice totals
function calculate_invoice_totals(frm) {
    const invoice_rows = frm.doc.invoice_list || [];
    const invoice_amount_usd = invoice_rows.reduce((sum, r) => sum + flt(r.total_price), 0);
    const invoice_amount_bdt = invoice_rows.reduce((sum, r) => sum + flt(r.base_net_amount), 0);

    const vat_rows = frm.doc.vat_list || [];
    const vat_amount_usd = vat_rows.reduce((sum, r) => sum + flt(r.vat_amount_usd), 0);
    const vat_amount_bdt = vat_rows.reduce((sum, r) => sum + flt(r.vat_amount_bdt), 0);

    frm.set_value("invoice_amount_usd", invoice_amount_usd);
    frm.set_value("vat_amount_usd", vat_amount_usd);
    frm.set_value("total_invoice_amount_usd", invoice_amount_usd + vat_amount_usd);

    frm.set_value("invoice_amount_bdt", invoice_amount_bdt);
    frm.set_value("vat_amount_bdt", vat_amount_bdt);
    frm.set_value("total_invoice_amount", invoice_amount_bdt + vat_amount_bdt);
}

function open_mapped_with_save_fix(frm, method) {
    frappe.model.open_mapped_doc({
        method: method,
        frm: frm,
    });
    ensure_mapped_doc_save_button();
}

function ensure_mapped_doc_save_button(retries = 30, delay = 150) {
    frappe.after_ajax(() => {
        const target = cur_frm;
        if (
            target &&
            target.doc &&
            target.doc.docstatus === 0 &&
            ['Sales Invoice', 'Purchase Invoice', 'Payment Entry'].includes(
                target.doctype
            )
        ) {
            target.enable_save();
            target.refresh_header();
            return;
        }

        if (retries <= 0) return;
        setTimeout(() => {
            ensure_mapped_doc_save_button(retries - 1, delay);
        }, delay);
    });
}
