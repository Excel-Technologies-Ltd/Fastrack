frappe.ui.form.on('Import Sea House Bill', {
    refresh:function(frm){
        const container_cost_info = frm.doc.container_cost_info;
        const total_price = container_cost_info.reduce((acc, item) => acc + item.qty * item.amount, 0);
        console.log(total_price)
        frm.set_value("total", total_price);
        const total_qty = container_cost_info.reduce((acc, item) => acc + item.qty, 0);
        console.log(total_qty)
        frm.set_value("average_total", total_price/total_qty);
    },
   
    refresh: function(frm) {
       if(frm.doc.docstatus==1){
        frm.add_custom_button(__("Sales Invoice"), function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_sales_invoice_from_hbl",
                frm:frm
            });
        },__("Create"));
        frm.add_custom_button(__("Expense"), function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_purchase_invoice_from_hbl",
                frm:frm
            });
        },__("Create"));
        frm.add_custom_button(__("Profit Share"), function () {
            frappe.model.open_mapped_doc({
                method: "fastrack_erp.api.make_journal_entry_from_hbl",
                frm:frm
            });
        },__("Create"));
    }
    },
    generate:function(frm){
     
            const container_items = frm.doc.container_info;
            if(container_items.length>0){
                const sizeQtySummary = getSizeQtySummary(container_items);
                frm.set_value("container_cost_info", sizeQtySummary);
            }else{
                frappe.throw("Please add container info first");
            }
        
    }
    


});

frappe.ui.form.on('Fastrack Sea Item', {
    // check if any row container_no empty throw error
    
});


  

function getSizeQtySummary(items) {
    const summary = {};
  
    items.forEach(item => {
      const size = item.size;
      if (size) {
        summary[size] = (summary[size] || 0) + 1;
      }
    });
  
    return Object.entries(summary).map(([size, qty]) => ({
      size,
      qty
    }));
  }
  