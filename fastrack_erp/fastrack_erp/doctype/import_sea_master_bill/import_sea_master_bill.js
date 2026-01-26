frappe.ui.form.on('Import Sea Master Bill', {
    refresh: function (frm) {
        // Show Download XML button when document is submitted
        if(frm.doc.docstatus==1){
            frm.add_custom_button('Download XML', function () {
                const url = `/api/method/fastrack_erp.api.download_xml_as_pdf?doctype=${frm.doc.doctype}&docname=${frm.doc.name}`;
                window.open(url, '_blank');
            });
        }
    },

    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("mbl_open_by",frappe.session.user)
        }
    }
});

// Container Info child table validation (Fastrack Item is the child DocType)
frappe.ui.form.on('Fastrack Item', {
    before_container_info_add: function(frm) {
        const total_containers = frm.doc.total_container || 0;
        const actual_containers = (frm.doc.container_info || []).length;

        if (actual_containers >= total_containers) {
            frappe.msgprint({
                title: __('Container Limit Reached'),
                message: __('Cannot add more than {0} container(s). Please increase "Total Container" field to add more.', [total_containers]),
                indicator: 'red'
            });
            return false;
        }
    },

    container_info_add: function(frm, cdt, cdn) {
        if (!validate_container_limit(frm)) {
            const row = frappe.get_doc(cdt, cdn);
            frm.get_field('container_info').grid.grid_rows_by_docname[cdn].remove();
        }
    }
});

// Child Table Logic: HBL Info
frappe.ui.form.on('HBL Info', {
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
        if (!validate_hbl_limit(frm)) {
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
            frappe.set_route("Form", "Import Sea House Bill", row.hbl_link);
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
                            method: "fastrack_erp.api.make_sea_house_bill",
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

// Toggle button visibility based on is_create
function toggle_buttons(row) {
    const grid_row = frappe.get_field('hbl_info').grid.get_row(row.name);
    if (!grid_row) return;

    const create_btn = grid_row.grid_form.fields_dict.create_hbl;
    const view_btn = grid_row.grid_form.fields_dict.view_hbl;

    if (row.is_create) {
        create_btn.df.hidden = 1;
        view_btn.df.hidden = 0;
    } else {
        create_btn.df.hidden = 0;
        view_btn.df.hidden = 1;
    }

    create_btn.refresh();
    view_btn.refresh();
}
  
  
  
  


  function update_hbl_buttons(frm) {
    // Make sure the grid is loaded
    if (!frm.fields_dict.hbl_info || !frm.fields_dict.hbl_info.grid) return;
    
    setTimeout(function() {
        // Process each row in the hbl_info child table
        $.each(frm.fields_dict.hbl_info.grid.grid_rows || [], function(i, grid_row) {
            if (!grid_row || !grid_row.doc) return;
            
            const btn = $(grid_row.row).find('button[data-fieldname="create_hbl"]');
            if (btn.length) {
                if (grid_row.doc.is_create) {
                    btn.html("View");
                } else {
                    btn.html("Create");
                }
            }
        });
    }, 100); // Small delay to ensure the grid is rendered
}

// Helper function to validate container limit
function validate_container_limit(frm) {
    const total_containers = frm.doc.total_container || 0;
    const actual_containers = (frm.doc.container_info || []).length;

    if (actual_containers > total_containers) {
        frappe.msgprint({
            title: __('Container Limit Exceeded'),
            message: __('Cannot add more than {0} container(s). Please increase "Total Container" field to add more.', [total_containers]),
            indicator: 'red'
        });
        return false;
    }
    return true;
}

// Helper function to validate HBL limit
function validate_hbl_limit(frm) {
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