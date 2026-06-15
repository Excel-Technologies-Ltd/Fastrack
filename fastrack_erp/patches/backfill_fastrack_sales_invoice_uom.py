import frappe


def execute():
    """Backfill UOM on Fastrack Sales Invoice child rows from their source Sales Invoice Item."""
    if not frappe.db.has_column("Fastrack Sales Invoice", "uom"):
        frappe.db.sql(
            "ALTER TABLE `tabFastrack Sales Invoice` ADD COLUMN `uom` varchar(140) DEFAULT NULL"
        )

    frappe.db.sql("""
        UPDATE `tabFastrack Sales Invoice` fsi
        JOIN `tabSales Invoice Item` sii
            ON sii.parent = fsi.invoice_link
           AND sii.item_code = fsi.item_code
        SET fsi.uom = sii.uom
        WHERE (fsi.uom IS NULL OR fsi.uom = '')
          AND sii.uom IS NOT NULL
          AND sii.uom != ''
    """)
    frappe.db.commit()
