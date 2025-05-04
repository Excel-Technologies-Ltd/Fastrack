frappe.ui.form.on('Import Sea House Bill', {
    refresh: function(frm) {
        if (frm.is_new()) {
            frm.trigger('mbl_no');
        }
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
                            ...item,
                            weight: 0
                        }));
                        frm.set_value("container_info", modifiedItems);
                    }
                }
            });
        }
    }
});
