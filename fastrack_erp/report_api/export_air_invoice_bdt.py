import frappe

from fastrack_erp.report_api.import_sea_invoice_bdt import download_invoice_bdt_pdf


@frappe.whitelist()
def download_export_air_invoice_bdt_pdf(doc_name, invoice_ids=None):
    download_invoice_bdt_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Export Air House Bill",
        html_title="Air Export Invoice BDT",
        heading="AIR EXPORT INVOICE",
        filename_prefix="Air_Export_Invoice_BDT",
    )
