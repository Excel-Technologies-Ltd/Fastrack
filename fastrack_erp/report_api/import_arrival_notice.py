import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url
from fastrack_erp.report_api.report_helpers import get_arrival_notice_shipping_html


@frappe.whitelist()
def download_arrival_notice_pdf(doc_name="SHBL-00000064",customer_name="Fastrack"):
    """Download Import Arrival Notice as PDF using HTML template"""
    
    try:
        # Get the document
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Get customer address
        customer_address = ""
        if doc.customer:
            try:
                customer_address = frappe.get_doc("Customer", {"customer_name": customer_name}).primary_address
            except:
                customer_address = ""
        
        html_content = get_arrival_notice_html(
            doc, customer_address, customer_name
        )
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set filename
        filename = f"Arrival_Notice_{doc_name}.pdf"
        
        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_igm_pdf(doc_name="SHBL-00000064", customer_name="Fastrack"):
    """Download IGM (Import General Manifest style) PDF for Import Sea HBL."""
    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        customer_address = ""
        if doc.customer:
            try:
                customer_address = frappe.get_doc(
                    "Customer", {"customer_name": customer_name}
                ).primary_address
            except Exception:
                customer_address = ""
        html_content = get_arrival_notice_html(
            doc,
            customer_address,
            customer_name,
            document_title="IGM",
            page_title="IGM",
        )
        pdf_content = get_pdf(html_content)
        filename = f"IGM_{doc_name}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_arrival_notice_html(
    doc,
    customer_address,
    customer_name,
    document_title="ARRIVAL NOTICE",
    page_title="Arrival Notice",
):
    """Generate HTML content for Arrival Notice or IGM."""
    
    # Get container information
    container_rows = ""
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            container_rows += f"""
            <tr>
                <td class="table-cell-data">{container.get('custom_container_no', '') or ''}</td>
                <td class="table-cell-data">{container.get('seal_no', '') or ''}</td>
                <td class="table-cell-data">{container.get('size', '') or ''}</td>
                <td class="table-cell-data">{container.get('status', '') or ''}</td>
                <td class="table-cell-data">{ int(container.get('no_of_pkg', '') or 0)}</td>
                <td class="table-cell-data">{container.get('weight', '') or ''}</td>
            </tr>
            """
    else:
        # Default empty row if no container data
        container_rows = """
        <tr>
            <td class="table-cell-data">-</td>
            <td class="table-cell-data">-</td>
            <td class="table-cell-data">-</td>
            <td class="table-cell-data">-</td>
            <td class="table-cell-data">-</td>
            <td class="table-cell-data">-</td>
        </tr>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{page_title}</title>
        <style>
            .document-container {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: white;
                font-size: 12px;
            }}
            .text-bold {{
                font-weight: bold;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            .title-box {{
                text-align: center;
                border: 2px solid #000;
                padding: 8px;
                margin: 0 auto 20px auto;
                font-weight: bold;
                font-size: 14px;
                width: 200px;
            }}
            .company-info {{
                margin-bottom: 20px;
            }}
            .attention-line {{
                margin-bottom: 20px;
                font-weight: bold;
            }}
            .section-header {{
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .details-container {{
                display: flex;
                margin-bottom: 20px;
            }}
            .left-column {{
                flex: 1;
                margin-right: 30px;
            }}
            .right-column {{
                flex: 1;
            }}
            .detail-row {{
                margin-bottom: 8px;
            }}
            .spacer {{
                margin-bottom: 40px;
            }}
            .container-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border: 1px solid #000;
            }}
             .details-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                
            }}
            .details-table td {{
                padding: 3px 5px;
                vertical-align: top;
            }}
            .table-header {{
                background-color: #f0f0f0;
            }}
            .table-cell {{
                border: 1px solid #000;
                padding: 5px;
                text-align: center;
                font-weight: bold;
            }}
            .table-cell-data {{
                border: 1px solid #000;
                padding: 5px;
                text-align: center;
            }}
            .total-weight {{
                text-align: right;
                margin-bottom: 20px;
                font-weight: bold;
            }}
            .terms-conditions {{
                font-size: 10px;
                line-height: 1.4;
                margin-bottom: 20px;
            }}
            .footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-top: 10px;
                margin-top: 40px;
            }}
            .footer-note {{
                font-size: 10px;
                font-weight: bold;
            }}
            .signature-section {{
                margin-top: 30px;
                margin-bottom: 30px;
                font-size: 10px;
                text-align: right;
                font-weight: bold;
            }}
            .signature-line {{
                border-bottom: 1px solid #000;
                text-align: right;
                width: 100px;
                margin-top: 20px;
                margin-bottom: 5px;
                margin-left: auto;
            }}
            .office-addresses {{
                margin-top: 20px;
                font-size: 8px;
                line-height: 1.4;
                text-align: center;
                color: black;
                padding-top: 10px;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                padding-left: 20px;
                padding-right: 20px;
            }}
            .center {{
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="document-container">
        

             <table style="width:100%; border-collapse:collapse; margin-bottom: 5px;">
                <tr>
                    <!-- Left: Logo -->
                    <td style="width:25%; vertical-align:middle;">
                        <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg"
                            alt="Fasttrack Logo"
                            style="height:55px;">
                    </td>

                    <!-- Center: Title -->
                    <td style="width:50%; text-align:center; vertical-align:middle;">
                       <div class="title-box">
                            {document_title}
                        </div>
                    </td>

                    <!-- Right: Empty (for balance) -->
                    <td style="width:25%;"></td>
                </tr>
            </table>

            <!-- Company Info -->
            <div class="company-info">
                <div class="text-bold">TO: {customer_name}</div>
                <div class="company-address">
                    {customer_address.split('#')[0] if customer_address else ''}
                </div>
            </div>

            <div class="attention-line">
                ATTN: Import / Commercial Department
            </div>

            <!-- Shipping Details Header -->
            <div class="section-header">Shipping Details:</div>

            <!-- Shipping Details Table -->
            {get_arrival_notice_shipping_html(doc)}

            <!-- Container Table -->
            <table class="container-table">
                <thead>
                    <tr class="table-header">
                        <th class="table-cell">Container No.</th>
                        <th class="table-cell">Seal No.</th>
                        <th class="table-cell">Size</th>
                        <th class="table-cell">Mode</th>
                        <th class="table-cell">No of Pkg</th>
                        <th class="table-cell">Weight</th>
                    </tr>
                </thead>
                <tbody>
                    {container_rows}
                    <tr>
                        <td colspan="5" style="border: 1px solid black; padding: 5px; text-align: right; font-weight: bold; border-top: 2px solid black;">Total Weight :</td>
                        <td style="border: 1px solid black; padding: 5px; text-align: center; font-weight: bold; border-top: 2px solid black;">{doc.get('hbl_weight', '') or ''} KG</td>
                    </tr>
                </tbody>
            </table>


            <!-- Terms and Conditions -->
            <div class="terms-conditions">
                <p>It may be noted that in the event of your failure to take delivery of your goods in the nick of time, we will not be held responsible for any damages and/or shortage etc. Should your consignment be required to be removed from the Landing place to any other shed it will be done at your sole risk and responsibilities and any expenses which maybe incurred by us for such removal will be recovered from you prior to issuing delivery order from this office.</p>
                
                <p>Kindly note that the goods not cleared within 45 days of the date of arrival of the vessel are liable to be auctioned by Customs under Sea Customs Act 167 (8) of 1969 and amended Section 82 issued by the Custom Authority.</p>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-note">
                    Note - This is System Generated, Not Require Signature or Seal.
                </div>
                <div class="signature-section">
                    <div style: "text-align: left;" class="signature-line"></div>
                    PREPARED BY</br>
                </div>
            </div>

            <!-- Office Addresses -->
            <div class="office-addresses">
                <p><strong>DHAKA OFFICE:</strong> HOUSE# 14(2nd Floor), ROAD# 13/C, BLOCK # E, BANANI, DHAKA -1213, BANGLADESH. Tel: +880-2-8836368, Fax: +880-2-8836374</p>
                <p><strong>CHITTAGONG OFFICE:</strong> 259B/A, HARUN BHABON (1st Floor), BADAMTOLI, SK. MUJIB ROAD, AGRABAD C/A, CHITTAGONG. Tel: +880-31-2527634</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


@frappe.whitelist()
def get_arrival_notice_preview(doc_name):
    """Get HTML preview of Arrival Notice (for testing)"""
    
    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Get customer address
        customer_address = ""
        if doc.customer:
            try:
                customer_doc = frappe.get_doc("Customer", doc.customer)
                if customer_doc.customer_primary_address:
                    address_doc = frappe.get_doc("Address", customer_doc.customer_primary_address)
                    customer_address = f"{address_doc.address_line1}, {address_doc.city}"
            except:
                customer_address = "Address not found"
        
        # Generate and return HTML content
        html_content = get_arrival_notice_html(doc, customer_address)
        return {"html": html_content}
        
    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")