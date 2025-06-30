frappe.ui.form.on('Import Sea House Bill', {
    refresh:function(frm){
        const container_cost_info = frm.doc.container_cost_info;
        const total_price = container_cost_info.reduce((acc, item) => acc + item.qty * item.amount, 0);
        console.log(total_price)
        frm.set_value("total", total_price);
        const total_qty = container_cost_info.reduce((acc, item) => acc + item.qty, 0);
        console.log(total_qty)
        frm.set_value("average_total", total_price/total_qty);
    },
    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("hbl_open_by",frappe.session.user)
        }    
    },
   
    refresh: function(frm) {
        const expense_list=frm.doc.purchase_invoice_list
        const format_expense=expense_list.map(expense => {
            return {
                    label: expense.invoice_link+ "-"+ expense.item_code, 
                    fieldname: expense.name,
                    fieldtype: 'Check',
            }
        })
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
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_journal_entry_from_hbl",
                frm:frm
            });
        },__("Create"));
    }
    frm.add_custom_button(__('DownLoad Expense PDF'), function() {
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
                    // frappe.call({
                    //     method: "fastrack_erp.api.download_purchase_invoice_pdf",  // Path to the method
                    //     args: {
                    //         invoice_ids: filteredInvoices.join(',') // Send as comma-separated string
                    //     },
                    //     callback: function(response) {
                    //         if (response.message) {
                    //             console.log(response.message)
                    //         } else {
                    //             frappe.msgprint(__('Failed to generate PDF.'));
                    //         }
                    //     }
                    // });
                    // Create a form and submit it to trigger file download
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
    });
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
    // check if any row container_no empty throw error
    
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
  