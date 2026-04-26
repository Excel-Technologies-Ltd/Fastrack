import frappe

from fastrack_erp.report_api.import_sea_invoice_bdt import download_invoice_bdt_pdf


@frappe.whitelist()
def download_export_d2d_invoice_bdt_pdf(doc_name, invoice_ids=None):
    download_invoice_bdt_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Export D2D Bill",
        html_title="D2D Export Invoice BDT",
        heading="D2D EXPORT INVOICE",
        filename_prefix="D2D_Export_Invoice_BDT",
    )
