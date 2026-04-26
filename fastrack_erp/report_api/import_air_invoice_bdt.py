import frappe

from fastrack_erp.report_api.import_sea_invoice_bdt import download_invoice_bdt_pdf


@frappe.whitelist()
def download_air_import_invoice_bdt_pdf(doc_name, invoice_ids=None):
    download_invoice_bdt_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import Air House Bill",
        html_title="Air Import Invoice BDT",
        heading="AIR IMPORT INVOICE",
        filename_prefix="Air_Import_Invoice_BDT",
    )
