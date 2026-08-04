import frappe


def execute():
    """Backfill final_amount_usd and amountbdt on Container Cost Info rows."""
    # This patch runs in the pre_model_sync phase, before `bench migrate`'s schema
    # sync creates these columns on a fresh site -- add them defensively first.
    for column in ("final_amount_usd", "amountbdt"):
        if not frappe.db.has_column("Container Cost Info", column):
            frappe.db.sql(
                f"ALTER TABLE `tabContainer Cost Info` ADD COLUMN `{column}` decimal(21,9) NOT NULL DEFAULT 0.000000000"
            )

    rows = frappe.db.get_all(
        "Container Cost Info",
        fields=["name", "qty", "amount", "ex_rate"],
    )

    for row in rows:
        qty = int(row.qty or 0)
        amount_usd = float(row.amount or 0)
        ex_rate = float(row.ex_rate or 0)
        final_usd = qty * amount_usd
        amount_bdt = final_usd * ex_rate
        frappe.db.set_value(
            "Container Cost Info",
            row.name,
            {
                "final_amount_usd": final_usd,
                "amountbdt": amount_bdt,
            },
            update_modified=False,
        )

    frappe.db.commit()
    print(f"Backfilled final_amount_usd and amountbdt on {len(rows)} Container Cost Info rows.")
