
import frappe


@frappe.whitelist()
def download_arrival_notice_report(doc="SHBL-2025-07-11-0040"):
    """Download Import Arrival Notice report as PDF"""
    doctype = "Import Sea House Bill"
    print_format_name = "Arrival Notice"
    
    # Check existence of print format
    if not frappe.db.exists("Print Format", print_format_name):
        frappe.throw(f"Print Format '{print_format_name}' not found")
    
    # Get the document
    doc_obj = frappe.get_doc(doctype, doc)
    
    
    # Generate PDF using frappe.get_print with as_pdf=True
    pdf_content = frappe.get_print(
        doctype=doctype,
        name=doc,
        doc=doc_obj,
        print_format=print_format_name,
        as_pdf=True,
        pdf_options={"disable-external-links": True, "disable-javascript": True}
    )
    
    # Set up the download response
    filename = f"Arrival_Notice_{doc}.pdf"
    
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "download"