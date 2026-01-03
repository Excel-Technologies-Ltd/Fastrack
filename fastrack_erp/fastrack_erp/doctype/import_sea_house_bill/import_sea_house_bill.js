frappe.ui.form.on('Import Sea House Bill', {


    refresh:function(frm){
        const container_cost_info = frm.doc.container_cost_info;
        const total_price = container_cost_info.reduce((acc, item) => acc + item.qty * item.amount, 0);
        console.log(total_price)
        frm.set_value("total", total_price);
        const total_qty = container_cost_info.reduce((acc, item) => acc + item.qty, 0);
        console.log(total_qty)
        frm.set_value("average_total", total_price/total_qty);

        // Hide/show container_info based on total_container_hbl
        toggle_container_info_visibility(frm);
    },

    total_container_hbl: function(frm) {
        // Toggle visibility when total_container_hbl changes
        toggle_container_info_visibility(frm);
    },
    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("hbl_open_by",frappe.session.user)
        }    
    },
   
    refresh: function(frm) {
        const expense_list=frm.doc.purchase_invoice_list
        const format_expense= (expense_list && expense_list.length>0) ? expense_list.map(expense => {
            return {
                    label: expense.invoice_link+ "-"+ expense.item_code, 
                    fieldname: expense.name,
                    fieldtype: 'Check',
            }
        }) : []
        const profit_share_list=frm.doc.profit_share_list
        const format_profit_share= (profit_share_list && profit_share_list.length>0) ? profit_share_list.map(profit_share => {
            return {
                    label: profit_share.journal_id + " - " + profit_share.account_name, 
                    fieldname: profit_share.name,
                    fieldtype: 'Check',
            }
        }):[]
        const sales_invoice_list=frm.doc.invoice_list
        const format_sales_invoice= (sales_invoice_list && sales_invoice_list.length>0) ? sales_invoice_list.map(sales_invoice => {
            return {
                    label: sales_invoice.invoice_link+ "-"+ sales_invoice.item_code, 
                    fieldname: sales_invoice.name,
                    fieldtype: 'Check',
            }
        }):[]
       if(frm.doc.docstatus==1){
        frm.add_custom_button(__("Sales Invoice"), function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_sales_invoice_from_hbl",
                frm:frm
            });
        },__("Create"));
        frm.add_custom_button(__("Expense"), function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_purchase_invoice_from_hbl",
                frm:frm
            });
        },__("Create"));
        frm.add_custom_button(__("Profit Share"), function () {
            frappe.new_doc("Payment Entry");
                },__("Create"));
        frm.add_custom_button(__("Payment Entry"), function () {
            frappe.new_doc("Payment Entry");

        },__("Create"));
    }
    frm.add_custom_button(__('Expense PDF'), function() {
        let dialog = new frappe.ui.Dialog({
            title: __('Select Options'),
            fields: [
                ...format_expense,
            ],
            primary_action_label: __('Download Selected'),
            primary_action(values) {
                console.log(values)
                const filteredInvoices = Object.entries(values)
                .filter(([key, value]) => value == 1)
                .map(([key, value]) => key);
                if (filteredInvoices.length===0){
                    frappe.msgprint("Please select an option")
                    return
                }
                if(filteredInvoices.length > 0){
                    console.log(filteredInvoices)
                const url = `/api/method/fastrack_erp.api.download_purchase_invoice_pdf`;
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = url;
                form.target = '_blank'; // Optional: open in new tab
                
                // Add CSRF token
                const csrfToken = document.createElement('input');
                csrfToken.type = 'hidden';
                csrfToken.name = 'csrf_token';
                csrfToken.value = frappe.csrf_token;
                form.appendChild(csrfToken);
                
                // Add invoice_ids parameter
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

                
                // Add form to document, submit, and remove
                document.body.appendChild(form);
                form.submit();
                document.body.removeChild(form);
                
                // Hide loading message after a delay
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
    },__("Download"));
    // add button to download profit share pdf
    frm.add_custom_button(__('Profit Share PDF'), function() {
        let dialog = new frappe.ui.Dialog({
            title: __('Select Options'),
            fields: [
                ...format_profit_share,
            ],
            primary_action_label: __('Download Selected'),
            primary_action(values) {
                const filteredProfitShare = Object.entries(values)
                .filter(([key, value]) => value == 1)
                .map(([key, value]) => key);
                if (filteredProfitShare.length===0){
                    frappe.msgprint("Please select an option")
                    return
                }
                if(filteredProfitShare.length > 0){
                    const url = `/api/method/fastrack_erp.api.download_profit_share_pdf`;
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = url;
                    form.target = '_blank'; // Optional: open in new tab
                    
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
    },__("Download"));
    // sales invoice pdf
    frm.add_custom_button(__('Sales Invoice PDF'), function() {
        let dialog = new frappe.ui.Dialog({
            title: __('Select Options'),
            fields: [
                ...format_sales_invoice,
            ],  
            primary_action_label: __('Download Selected'),
            primary_action(values) {
                const filteredSalesInvoice = Object.entries(values)
                .filter(([key, value]) => value == 1)
                .map(([key, value]) => key);
                if (filteredSalesInvoice.length===0){
                    frappe.msgprint("Please select an option")
                    return
                }
                if(filteredSalesInvoice.length > 0){
                   const url = `/api/method/fastrack_erp.api.download_sales_invoice_pdf`;
                   const form = document.createElement('form');
                   form.method = 'POST';
                   form.action = url;
                   form.target = '_blank'; // Optional: open in new tab
                   
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
    },__("Download"));
},
    generate:function(frm){
     
            const container_items = frm.doc.container_info;
            if(container_items.length>0){
                const sizeQtySummary = getSizeQtySummary(container_items);
                frm.set_value("container_cost_info", sizeQtySummary);
            }else{
                frappe.throw("Please add container info first");
            }
        
    }
    


});

frappe.ui.form.on('Fastrack Sea Item', {
    // Validate before adding a new row
    before_container_info_add: function(frm) {
        const total_containers = frm.doc.total_container_hbl || 0;
        const actual_containers = (frm.doc.container_info || []).length;

        if (actual_containers >= total_containers) {
            frappe.msgprint({
                title: __('Container Limit Reached'),
                message: __('Cannot add more than {0} container(s). Please update "Total Container HBL" field to add more containers.', [total_containers]),
                indicator: 'red'
            });
            return false; // Prevent adding the row
        }
    },

    container_info_add: function(frm, cdt, cdn) {
        // Validate after row is added
        if (!validate_container_limit(frm)) {
            // Remove the last added row if limit exceeded
            const row = frappe.get_doc(cdt, cdn);
            frm.get_field('container_info').grid.grid_rows_by_docname[cdn].remove();
        }
    }
});


  

function getSizeQtySummary(items) {
    const summary = {};
  
    items.forEach(item => {
      const size = item.size;
      if (size) {
        summary[size] = (summary[size] || 0) + 1;
      }
    });
  
    return Object.entries(summary).map(([size, qty]) => ({
      size,
      qty
    }));
  }
  


// child doctype
frappe.ui.form.on('Fastrack Sea Item', {
    // refresh:function(frm, cdt, cdn){
    //     if(cdt === 'Import Sea House Bill'){
    //         setTimeout(function() {
               
    //             frm.fields_dict['container_info'].grid.wrapper.find('.btn-open-row').hide();
    //         }, 1000);
    //     }
    // }
});



//     Container Cost Info

frappe.ui.form.on('Container Cost Info', {
    ex_rate: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        var usd_amount = row.amount || 0;
        var ex_rate = row.ex_rate || 0;  // Get from parent document
        var bdt_amount = usd_amount * ex_rate;

        frappe.model.set_value(cdt, cdn, "amountbdt", bdt_amount);
    }
});

// Helper function to toggle container_info visibility
function toggle_container_info_visibility(frm) {
    const total_containers = frm.doc.total_container_hbl || 0;

    if (total_containers === 0) {
        // Hide container_info field when total is 0 or null
        frm.set_df_property('container_info', 'hidden', 1);
    } else {
        // Show container_info field
        frm.set_df_property('container_info', 'hidden', 0);
    }
}

// Helper function to validate and control container_info row limit
function validate_container_limit(frm) {
    const total_containers = frm.doc.total_container_hbl || 0;
    const actual_containers = (frm.doc.container_info || []).length;

    // If limit exceeded, prevent adding and show message
    if (actual_containers > total_containers) {
        frappe.msgprint({
            title: __('Container Limit Exceeded'),
            message: __('Cannot add more than {0} container(s). Please update "Total Container HBL" field to add more containers.', [total_containers]),
            indicator: 'red'
        });
        return false;
    }
    return true;
}