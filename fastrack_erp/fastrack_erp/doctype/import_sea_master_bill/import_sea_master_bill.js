frappe.ui.form.on('Import Sea Master Bill', {
    refresh: function (frm) {
        // Any additional refresh logic if needed
    }
});

// Child Table Logic: HBL Info
frappe.ui.form.on('HBL Info', {
    create_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
       if(frm.doc.docstatus!=1){
        return frappe.msgprint("MBL not submitted yet")
       }
        if(row.is_create){
            return frappe.msgprint("HBL already created")
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
frappe.ui.form.on('Import Sea Master Bill', {
	refresh(frm) {
	  if(frm.doc.docstatus==1){
        frm.add_custom_button('Download XML', function () {
            const url = `/api/method/fastrack_erp.api.download_xml_as_pdf?doctype=${frm.doc.doctype}&docname=${frm.doc.name}`;
            window.open(url, '_blank');
          });
      }
	}
  });
  
  
  
  