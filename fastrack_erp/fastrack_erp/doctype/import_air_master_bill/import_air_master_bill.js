frappe.ui.form.on('Import Air Master Bill', {
    
});
// Child Table Logic: HBL Info
frappe.ui.form.on('HBL Air Info', {
    create_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
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

// Toggle button visibility based on is_create
// frappe.ui.form.on('Import Sea Master Bill', {
// 	refresh(frm) {
// 	  frm.add_custom_button('Download XML as PDF', function () {
// 		const url = `/api/method/fastrack_erp.api.download_xml_as_pdf?doctype=${frm.doc.doctype}&docname=${frm.doc.name}`;
// 		window.open(url, '_blank');
// 	  });
// 	}
//   });
  
  
  
  