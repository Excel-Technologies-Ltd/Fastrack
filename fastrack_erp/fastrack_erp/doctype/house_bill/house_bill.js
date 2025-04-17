// Copyright (c) 2025, Shaid Azmin and contributors
// For license information, please see license.txt

frappe.ui.form.on('House Bill', {
	// refresh: function(frm) {

	// }
	onload: function(frm) {
		// console.log(frm.doc);
	},

	master_bill_no: function(frm) {
        let masterBill = frm.doc.master_bill_no;

        if (masterBill) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Master Bill",  // The linked DocType
                    name: masterBill        // The ID of the selected record
                },
                callback: function(response) {
                    if (response.message) {
						frm.set_value("container_items", [...response?.message?.item_details]);
                    }
                }
            });
        }
    }

});
