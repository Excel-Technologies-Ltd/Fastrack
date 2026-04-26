import frappe

from fastrack_erp.report_api.import_sea_invoice_bdt import download_invoice_bdt_pdf


@frappe.whitelist()
def download_d2d_import_invoice_bdt_pdf(doc_name, invoice_ids=None):
    download_invoice_bdt_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import D2D Bill",
        html_title="D2D Import Invoice BDT",
        heading="D2D IMPORT INVOICE",
        filename_prefix="D2D_Import_Invoice_BDT",
    )
