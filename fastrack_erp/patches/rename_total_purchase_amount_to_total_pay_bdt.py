import frappe

HBL_DOCTYPES = [
    "Import Sea House Bill",
    "Import Air House Bill",
    "Import D2D Bill",
    "Export Sea House Bill",
    "Export Air House Bill",
    "Export D2D Bill",
]


def execute():
    """
    Rename total_purchase_amount -> total_pay_bdt (same Currency column, just
    a clearer name matching the sibling total_pay_usd field).

    Runs pre_model_sync and renames the column directly with ALTER TABLE so
    existing data is preserved. If this instead ran after schema sync (or if
    the field were simply renamed in the doctype JSON with no patch at all),
    schema sync would see total_purchase_amount missing from the JSON and
    total_pay_bdt newly present, and would drop the old (data-bearing) column
    while adding the new one empty -- losing every existing value.
    """
    for doctype in HBL_DOCTYPES:
        table = f"tab{doctype}"
        if frappe.db.has_column(doctype, "total_purchase_amount") and not frappe.db.has_column(
            doctype, "total_pay_bdt"
        ):
            frappe.db.sql(
                f"ALTER TABLE `{table}` "
                f"CHANGE COLUMN `total_purchase_amount` `total_pay_bdt` "
                f"decimal(21,9) NOT NULL DEFAULT 0.000000000"
            )

    # Custom Field "insert_after" and Property Setter references, if any
    # target this field on these doctypes, need to follow the rename too.
    frappe.db.sql(
        """
        UPDATE `tabProperty Setter`
        SET field_name = 'total_pay_bdt'
        WHERE field_name = 'total_purchase_amount' AND doc_type IN ({})
        """.format(", ".join(["%s"] * len(HBL_DOCTYPES))),
        HBL_DOCTYPES,
    )
    frappe.db.sql(
        """
        UPDATE `tabCustom Field`
        SET insert_after = 'total_pay_bdt'
        WHERE insert_after = 'total_purchase_amount' AND dt IN ({})
        """.format(", ".join(["%s"] * len(HBL_DOCTYPES))),
        HBL_DOCTYPES,
    )

    # field_order Property Setters store the whole field list as one JSON
    # string in `value` -- the old fieldname needs replacing there too, or
    # the customized ordering keeps pointing at a field that no longer exists.
    for row in frappe.db.get_all(
        "Property Setter",
        filters={"property": "field_order", "doc_type": ["in", HBL_DOCTYPES], "value": ["like", "%total_purchase_amount%"]},
        fields=["name", "value"],
    ):
        frappe.db.set_value(
            "Property Setter",
            row.name,
            "value",
            row.value.replace('"total_purchase_amount"', '"total_pay_bdt"'),
            update_modified=False,
        )

    frappe.db.commit()
    print("Renamed total_purchase_amount -> total_pay_bdt on HBL doctypes.")
