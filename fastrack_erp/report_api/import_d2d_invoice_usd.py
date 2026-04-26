import frappe

from fastrack_erp.report_api.import_sea_invoice_usd import download_invoice_usd_pdf


@frappe.whitelist()
def download_d2d_import_invoice_usd_pdf(doc_name, invoice_ids=None):
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import D2D Bill",
        heading="D2D IMPORT INVOICE",
        html_title="D2D Import Invoice USD",
        filename_prefix="D2D_Import_Invoice_USD",
    )
