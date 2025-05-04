frappe.ui.form.on('Import Sea Master Bill', {
    refresh: function (frm) {
        // Any additional refresh logic if needed
    }
});

// Child Table Logic: HBL Info
frappe.ui.form.on('HBL Info', {
    create_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
		
        // Perform routing to a new form (replace 'House Bill' with actual target Doctype)
        frappe.model.open_mapped_doc({
			method: "fastrack_erp.api.make_sea_house_bill",
			frm: {name:frm.doc.name,agent:frm.doc.agent,consignee:frm.doc.consignee,parent:row.parent},
		});
    },

    view_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.hbl_no) {
            frappe.msgprint(__('HBL No. not found'));
            return;
        }
		frappe.msgprint("work")
        // Redirect to the existing form for the HBL
        // frappe.set_route('Form', 'Import Sea House Bill', row.hbl_no);
    },

    is_create: function (frm, cdt, cdn) {
        toggle_buttons(locals[cdt][cdn]);
    },

    hbl_no: function (frm, cdt, cdn) {
        toggle_buttons(locals[cdt][cdn]);
    }
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
	  frm.add_custom_button('Download XML as PDF', function () {
		const url = `/api/method/fastrack_erp.api.download_xml_as_pdf?doctype=${frm.doc.doctype}&docname=${frm.doc.name}`;
		window.open(url, '_blank');
	  });
	}
  });
  
  
  
  