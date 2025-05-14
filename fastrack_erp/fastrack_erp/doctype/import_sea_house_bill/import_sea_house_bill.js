frappe.ui.form.on('Import Sea House Bill', {
    on_load: function(frm) {
        frm.get_field("container_info").grid.cannot_add_rows = true;      
    },
    refresh: function(frm) {
        if (frm.is_new()) {
            frm.trigger('mbl_no');
        }
        
        
        // frm.fields_dict['container_info'].grid.grid_buttons.remove();
        // make a button to make sales invoice from hbl 
        frm.add_custom_button('Make Sales Invoice from HBL', function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_sales_invoice_from_hbl",
                frm:frm
            });
        });
    },
    

    mbl_no: function(frm) {
        const masterBill = frm.doc.mbl_no;
		console.log(masterBill)

        if (masterBill) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Import Sea Master Bill",
                    name: masterBill
                },
                callback: function(response) {
                    if (response.message && response.message.container_info) {
                        const modifiedItems = response.message.container_info.map(item => ({
                            container_no: item.container_no,
                        }));
                        frm.set_value("container_info", modifiedItems);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Fastrack Sea Item', {
    // check if any row container_no empty throw error
    
});

