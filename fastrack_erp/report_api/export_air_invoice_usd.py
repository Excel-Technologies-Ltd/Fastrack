import frappe

from fastrack_erp.report_api.import_sea_invoice_usd import download_invoice_usd_pdf


@frappe.whitelist()
def download_export_air_invoice_usd_pdf(doc_name, invoice_ids=None):
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Export Air House Bill",
        heading="AIR EXPORT INVOICE",
        html_title="Air Export Invoice USD",
        filename_prefix="Air_Export_Invoice_USD",
    )
