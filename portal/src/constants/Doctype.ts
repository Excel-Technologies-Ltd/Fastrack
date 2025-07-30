export const DOCTYPE_LIST = {
    IMPORT_SEA_HOUSE_BILL: {
        NAME: "Import Sea House Bill",
        CHILD_DOCTYPE: {
            CONTAINER_INFO: {
                name: "container_info",
                fields: [
                    { name: "name", label: "Id" },
                    { name: "custom_container_no", label: "Container No" },
                    { name: "size", label: "Size" },
                    { name: "no_of_pkg", label: "No of Pkg" },
                ],
            },
            INVOICE_LIST: {
                name: "invoice_list",
                fields: [
                    { name: "name", label: "Id" },
                    { name: "invoice_link", label: "Invoice No" },
                    { name: "customer", label: "Customer" },
                    { name: "item_code", label: "Item Code" },
                    { name: "qty", label: "QTY" },
                ],
            },
            EXPENSE_LIST: {
                name: "purchase_invoice_list",
                fields: [
                    { name: "name", label: "Id" },
                    { name: "invoice_link", label: "Invoice No" },
                    { name: "supplier", label: "Supplier" },
                    { name: "item_code", label: "Item Code" },
                    { name: "qty", label: "Qty" },

                ],
            },
        },
    },
};
