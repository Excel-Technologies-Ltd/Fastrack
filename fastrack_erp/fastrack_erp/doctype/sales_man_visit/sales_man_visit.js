// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Man Visit', {
	// refresh: function(frm) {
	// 	console.log(frm);
	// },
	onload: function(frm) {
        if (!frm.doc.date && !frm.doc.time) {
            frm.set_value('date', frappe.datetime.get_today());
			frm.set_value('time', frappe.datetime.now_datetime());
        }
    }
});
