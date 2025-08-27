import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url


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
        
        # Generate HTML content
        html_content = get_arrival_notice_html(doc, customer_address,customer_name)
        
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


def get_arrival_notice_html(doc, customer_address,customer_name):
    """Generate HTML content for Arrival Notice"""
    
    # Get container information
    container_rows = ""
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            container_rows += f"""
            <tr>
                <td class="table-cell-data">{container.get('custom_container_no', '') or ''}</td>
                <td class="table-cell-data">{container.get('seal_no', '') or ''}</td>
                <td class="table-cell-data">{container.get('size', '') or ''}</td>
                <td class="table-cell-data">{doc.get('nature', '') or ''}</td>
                <td class="table-cell-data">{container.get('weight', '') or ''}</td>
                <td class="table-cell-data">{doc.get('description_of_good', '') or ''}</td>
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
        <title>Arrival Notice</title>
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
                border-top: 1px solid #000;
                padding-top: 10px;
                margin-top: 40px;
            }}
            .footer-note {{
                font-size: 10px;
                font-weight: bold;
            }}
            .signature-section {{
                font-size: 10px;
                text-align: right;
                font-weight: bold;
            }}
            .signature-line {{
                border-bottom: 1px solid #000;
                width: 120px;
                margin-top: 20px;
            }}
            .office-addresses {{
                font-size: 9px;
                margin-top: 30px;
                line-height: 1.3;
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
            <!-- Header -->
            <div class="header">
                <div class="logo">
                    <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 55px;" />
                </div>
            </div>

            <!-- Title -->
            <div class="center">
                <div class="title-box">
                    ARRIVAL NOTICE
                </div>
            </div>

            <!-- Company Info -->
            <div class="company-info">
                <div class="text-bold">TO: {customer_name}</div>
                <div class="company-address">
                    {customer_address}
                </div>
            </div>

            <div class="attention-line">
                ATTN: Import / Commercial Department
            </div>

            <!-- Shipping Details Header -->
            <div class="section-header">Shipping Details:</div>

            <!-- Details Container -->
            <div class="details-container">
                <table class="details-table">
                    <tr>
                        <td>
                            <div class="detail-row"><strong>Notify Party</strong>: {doc.get('notify_to', '') or ''}</div>
                            <div class="detail-row"><strong>Shipper</strong>: {doc.get('hbl_shipper', '') or ''}</div>
                            <div class="detail-row"><strong>HBL No</strong>: {doc.get('hbl_id', '') or ''}</div>
                            <div class="detail-row"><strong>HBL Date</strong>: {doc.get('hbl_date', '') or ''}</div>
                            <div class="detail-row"><strong>MBL No</strong>: {doc.get('mbl_no', '') or ''}</div>
                            <div class="detail-row"><strong>MBL Date</strong>: {doc.get('mbl_date', '') or ''}</div>
                            <div class="detail-row"><strong>L/C No.& Date</strong>: {doc.get('lc_date', '') or ''}</div>
                            <div class="detail-row"><strong>Port of Loading</strong>: {doc.get('port_of_loading', '') or ''}</div>
                            <div class="detail-row"><strong>Port of Discharge</strong>: {doc.get('port_of_discharge', '') or ''}</div>
                            <div class="detail-row"><strong>Port of Delivery</strong>: {doc.get('port_of_delivery', '') or ''}</div>
                            <div class="detail-row"><strong>Shipping Line</strong>: {doc.get('shipping_line', '') or ''}</div>
                        </td>
                        <td>
                            <div class="detail-row"><strong>M/Vsl. Name</strong>: {doc.get('mv', '') or ''}</div>
                            <div class="detail-row"><strong>Voyage</strong>: {doc.get('mv_voyage_no', '') or ''}</div>
                            <div class="detail-row"><strong>ETD</strong>: {doc.get('hbl_etd', '') or ''}</div>
                            <div class="detail-row"><strong>F/Vsl. Name</strong>: {doc.get('fv', '') or ''}</div>
                            <div class="detail-row"><strong>ETA</strong>: {doc.get('eta', '') or ''}</div>
                            <div class="detail-row"><strong>Inco Terms</strong>: {doc.get('inco_term', '') or ''}</div>
                            <div class="detail-row"><strong>Volume CBM</strong>: {doc.get('hbl_vol_cbm', '') or ''}</div>
                            <div class="detail-row"><strong>Total (CTN/PKG)</strong>: {doc.get('no_of_pkg_hbl', '') or ''}</div>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Container Table -->
            <table class="container-table">
                <thead>
                    <tr class="table-header">
                        <th class="table-cell">Container No.</th>
                        <th class="table-cell">Seal No.</th>
                        <th class="table-cell">Size</th>
                        <th class="table-cell">Mode</th>
                        <th class="table-cell">Weight</th>
                        <th class="table-cell">Goods Description</th>
                    </tr>
                </thead>
                <tbody>
                    {container_rows}
                </tbody>
            </table>

            <!-- Total Weight -->
            <div class="total-weight">
                <strong>Total Weight:</strong> {doc.get('gross_weight', '') or ''}
            </div>

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
                    PREPARED BY<br>
                    <div class="signature-line"></div>
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