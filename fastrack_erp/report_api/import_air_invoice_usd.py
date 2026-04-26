import frappe

from fastrack_erp.report_api.import_sea_invoice_usd import download_invoice_usd_pdf


@frappe.whitelist()
def download_air_import_invoice_usd_pdf(doc_name, invoice_ids=None):
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import Air House Bill",
        heading="AIR IMPORT INVOICE",
        html_title="Air Import Invoice USD",
        filename_prefix="Air_Import_Invoice_USD",
    )
