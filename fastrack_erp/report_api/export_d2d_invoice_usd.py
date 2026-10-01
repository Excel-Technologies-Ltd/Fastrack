import frappe

from fastrack_erp.report_api.import_sea_invoice_usd import download_invoice_usd_pdf


@frappe.whitelist()
def download_export_d2d_invoice_usd_pdf(doc_name, invoice_ids=None, customer_name=None):
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Export D2D Bill",
        html_title="D2D Export Invoice USD",
        heading="D2D EXPORT INVOICE",
        filename_prefix="D2D_Export_Invoice_USD",
        customer_name=customer_name,
    )
