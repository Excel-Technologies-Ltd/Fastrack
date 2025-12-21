frappe.ui.form.on('Import Air House Bill', {
    onload: function(frm){
        if(frm.is_new()){
            frm.set_value("hbl_open_by",frappe.session.user)
            frm.refresh_field("hbl_open_by")
        }    
    },
});

  
