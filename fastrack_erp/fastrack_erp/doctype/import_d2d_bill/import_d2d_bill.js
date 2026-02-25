// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Import D2D Bill', {
    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("hbl_open_by",frappe.session.user)
            frm.refresh_field("hbl_open_by")
        }
    },

    refresh: function(frm) {
        const expense_list = frm.doc.purchase_invoice_list
        const format_expense = (expense_list && expense_list.length > 0) ? expense_list.map(expense => {
            return {
                label: expense.invoice_link + "-" + expense.item_code,
                fieldname: expense.name,
                fieldtype: 'Check',
            }
        }) : []

        const profit_share_list = frm.doc.profit_share_list
        const format_profit_share = (profit_share_list && profit_share_list.length > 0) ? profit_share_list.map(profit_share => {
            return {
                label: profit_share.journal_id + " - " + profit_share.account_name,
                fieldname: profit_share.name,
                fieldtype: 'Check',
            }
        }) : []

        const sales_invoice_list = frm.doc.invoice_list
        const format_sales_invoice = (sales_invoice_list && sales_invoice_list.length > 0) ? sales_invoice_list.map(sales_invoice => {
            return {
                label: sales_invoice.invoice_link + "-" + sales_invoice.item_code,
                fieldname: sales_invoice.name,
                fieldtype: 'Check',
            }
        }) : []

        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Sales Invoice"), function () {
                frappe.model.open_mapped_doc({
                    method: "fastrack_erp.api.make_sales_invoice_from_hbl",
                    frm: frm
                });
            }, __("Create"));

            frm.add_custom_button(__("Expense"), function () {
                frappe.model.open_mapped_doc({
                    method: "fastrack_erp.api.make_purchase_invoice_from_hbl",
                    frm: frm
                });
            }, __("Create"));

            frm.add_custom_button(__("Profit Share"), function () {
                frappe.new_doc("Payment Entry");
            }, __("Create"));

            frm.add_custom_button(__("Payment Entry"), function () {
                frappe.model.open_mapped_doc({
                    method: "fastrack_erp.api.make_payment_entry_from_hbl",
                    frm: frm
                });
            }, __("Create"));
        }

        // Expense PDF
        frm.add_custom_button(__('Expense PDF'), function() {
            let dialog = new frappe.ui.Dialog({
                title: __('Select Options'),
                fields: [...format_expense],
                primary_action_label: __('Download Selected'),
                primary_action(values) {
                    const filteredInvoices = Object.entries(values)
                        .filter(([key, value]) => value == 1)
                        .map(([key, value]) => key);
                    if (filteredInvoices.length === 0) {
                        frappe.msgprint("Please select an option")
                        return
                    }
                    if (filteredInvoices.length > 0) {
                        const url = `/api/method/fastrack_erp.api.download_purchase_invoice_pdf`;
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = url;
                        form.target = '_blank';

                        const csrfToken = document.createElement('input');
                        csrfToken.type = 'hidden';
                        csrfToken.name = 'csrf_token';
                        csrfToken.value = frappe.csrf_token;
                        form.appendChild(csrfToken);

                        const invoiceInput = document.createElement('input');
                        invoiceInput.type = 'hidden';
                        invoiceInput.name = 'invoice_ids';
                        invoiceInput.value = filteredInvoices.join(',');

                        const doctype_name = document.createElement('input');
                        doctype_name.type = 'hidden';
                        doctype_name.name = 'doctype_name';
                        doctype_name.value = frm.doc.name;
                        form.appendChild(invoiceInput);
                        form.appendChild(doctype_name);

                        document.body.appendChild(form);
                        form.submit();
                        document.body.removeChild(form);

                        setTimeout(() => {
                            frappe.show_alert({
                                message: __('PDF download started'),
                                indicator: 'green'
                            });
                        }, 1000);
                    }
                    dialog.hide();
                }
            });
            dialog.show();
        }, __("Download"));

        // Profit Share PDF
        frm.add_custom_button(__('Profit Share PDF'), function() {
            let dialog = new frappe.ui.Dialog({
                title: __('Select Options'),
                fields: [...format_profit_share],
                primary_action_label: __('Download Selected'),
                primary_action(values) {
                    const filteredProfitShare = Object.entries(values)
                        .filter(([key, value]) => value == 1)
                        .map(([key, value]) => key);
                    if (filteredProfitShare.length === 0) {
                        frappe.msgprint("Please select an option")
                        return
                    }
                    if (filteredProfitShare.length > 0) {
                        const url = `/api/method/fastrack_erp.api.download_profit_share_pdf`;
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = url;
                        form.target = '_blank';

                        const csrfToken = document.createElement('input');
                        csrfToken.type = 'hidden';
                        csrfToken.name = 'csrf_token';
                        csrfToken.value = frappe.csrf_token;
                        form.appendChild(csrfToken);

                        const journalInput = document.createElement('input');
                        journalInput.type = 'hidden';
                        journalInput.name = 'journal_ids';
                        journalInput.value = filteredProfitShare.join(',');

                        const doctype_name = document.createElement('input');
                        doctype_name.type = 'hidden';
                        doctype_name.name = 'doctype_name';
                        doctype_name.value = frm.doc.name;
                        form.appendChild(journalInput);
                        form.appendChild(doctype_name);

                        document.body.appendChild(form);
                        form.submit();
                        document.body.removeChild(form);

                        setTimeout(() => {
                            frappe.show_alert({
                                message: __('PDF download started'),
                                indicator: 'green'
                            });
                        }, 1000);
                    }
                }
            });
            dialog.show();
        }, __("Download"));

        // Sales Invoice PDF
        frm.add_custom_button(__('Sales Invoice PDF'), function() {
            let dialog = new frappe.ui.Dialog({
                title: __('Select Options'),
                fields: [...format_sales_invoice],
                primary_action_label: __('Download Selected'),
                primary_action(values) {
                    const filteredSalesInvoice = Object.entries(values)
                        .filter(([key, value]) => value == 1)
                        .map(([key, value]) => key);
                    if (filteredSalesInvoice.length === 0) {
                        frappe.msgprint("Please select an option")
                        return
                    }
                    if (filteredSalesInvoice.length > 0) {
                        const url = `/api/method/fastrack_erp.api.download_sales_invoice_pdf`;
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = url;
                        form.target = '_blank';

                        const csrfToken = document.createElement('input');
                        csrfToken.type = 'hidden';
                        csrfToken.name = 'csrf_token';
                        csrfToken.value = frappe.csrf_token;
                        form.appendChild(csrfToken);

                        const invoiceInput = document.createElement('input');
                        invoiceInput.type = 'hidden';
                        invoiceInput.name = 'invoice_ids';
                        invoiceInput.value = filteredSalesInvoice.join(',');

                        const doctype_name = document.createElement('input');
                        doctype_name.type = 'hidden';
                        doctype_name.name = 'doctype_name';
                        doctype_name.value = frm.doc.name;
                        form.appendChild(invoiceInput);
                        form.appendChild(doctype_name);

                        document.body.appendChild(form);
                        form.submit();
                        document.body.removeChild(form);

                        setTimeout(() => {
                            frappe.show_alert({
                                message: __('PDF download started'),
                                indicator: 'green'
                            });
                        }, 1000);
                    }
                }
            });
            dialog.show();
        }, __("Download"));
    }
});
