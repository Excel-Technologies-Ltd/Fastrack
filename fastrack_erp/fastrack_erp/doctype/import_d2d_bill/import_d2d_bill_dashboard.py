from frappe import _


def get_data():
    return {
        "fieldname": "import_d2d_bill",
        "non_standard_fieldnames": {
            "Payment Entry": "custom_hbl_no",

        },

        "transactions": [
            {
                "items": [
                    "Payment Entry",
                ],
            },
        ],
    }
