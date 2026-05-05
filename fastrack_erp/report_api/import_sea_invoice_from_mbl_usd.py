import frappe

from fastrack_erp.report_api.import_sea_invoice_usd import (
    download_invoice_usd_pdf,
)


@frappe.whitelist()
def download_sea_import_invoice_from_mbl_usd_pdf(doc_name, invoice_ids=None):
    """Sea Import Invoice USD for Import Sea Master Bill (portal: Invoice from MBL)."""
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import Sea Master Bill",
        heading="SEA IMPORT INVOICE",
        html_title="Sea Import Invoice USD (MBL)",
        filename_prefix="Sea_Import_Invoice_MBL_USD",
    )
