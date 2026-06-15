import frappe


def execute():
    """Backfill final_amount_usd and amountbdt on Container Cost Info rows."""
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
