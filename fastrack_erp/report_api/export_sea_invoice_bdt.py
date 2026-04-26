import frappe

from fastrack_erp.report_api.import_sea_invoice_bdt import download_invoice_bdt_pdf


@frappe.whitelist()
def download_export_sea_invoice_bdt_pdf(doc_name, invoice_ids=None):
    download_invoice_bdt_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Export Sea House Bill",
        html_title="Sea Export Invoice BDT",
        heading="SEA EXPORT INVOICE",
        filename_prefix="Sea_Export_Invoice_BDT",
    )
