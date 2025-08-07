


frappe.ui.form.on('Import Air Master Bill', {
    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("mbl_open_by",frappe.session.user)
        }    
    },
});
// Child Table Logic: HBL Info
frappe.ui.form.on('HBL Air Info', {

    create_hbl: function (frm, cdt, cdn) {
        if(frm.doc.docstatus != 1){
            frappe.msgprint("Please Submit the master bill first")
            return
        }
        const row = locals[cdt][cdn];
        if(row.is_create){
             // route to view hbl
             frappe.set_route("Form", "Import Air House Bill", row.hbl_link);
             return 
            // return frappe.msgprint("HBL already created")
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
                            method: "fastrack_erp.api.make_air_house_bill",
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

// frappe.ui.form.on('Import Sea Master Bill', {
// 	refresh(frm) {
// 	  frm.add_custom_button('Download XML as PDF', function () {
// 		const url = `/api/method/fastrack_erp.api.download_xml_as_pdf?doctype=${frm.doc.doctype}&docname=${frm.doc.name}`;
// 		window.open(url, '_blank');
// 	  });
// 	}
//   });
  
  
  
  