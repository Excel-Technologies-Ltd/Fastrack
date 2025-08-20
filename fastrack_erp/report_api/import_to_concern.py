import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, format_date, today


@frappe.whitelist()
def download_to_whom_concern_pdf(doc_name):
    """Download To Whom It May Concern certificate as PDF using HTML template"""
    
    try:
        # Get the document
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Get customer info
        customer_name = ""
        customer_address = ""
        if doc.invoice_list and len(doc.invoice_list) > 0:
            customer = doc.invoice_list[0].customer
            if customer:
                try:
                    customer_doc = frappe.get_doc("Customer", customer)
                    customer_name = customer_doc.customer_name or customer
                    customer_address = customer_doc.primary_address or ""
                except:
                    customer_name = customer
                    customer_address = ""
        
        # Generate HTML content
        html_content = get_to_whom_concern_html(doc, customer_name, customer_address)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set filename
        filename = f"To_Whom_Concern_{doc_name}.pdf"
        
        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_to_whom_concern_html(doc, customer_name, customer_address):
    """Generate HTML content for To Whom It May Concern certificate"""
    
    # Get container volume
    container_volume_list = []
    if hasattr(doc, 'container_cost_info') and doc.container_cost_info:
        for container in doc.container_cost_info:
            qty = container.get('qty', '') or ''
            size = container.get('size', '') or ''
            if qty and size:
                container_volume_list.append(f"{qty}x{size}")
    container_volume = ", ".join(container_volume_list)
    
    
    # Get ocean freight rate
    ocean_freight_rate = doc.get('total')
    ocean_freight_total = doc.get('total')

    
    # Format current date
    current_date = format_date(today(), "dd-MMM-yyyy")
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>To Whom It May Concern</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                margin: 0;
                padding: 20px;
                background: white;
                color: black;
                line-height: 1.4;
            }}
            .container {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .title-box {{
                border: 2px solid black;
                padding: 8px;
                margin: 20px auto;
                width: 300px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
            }}
            .details-section {{
                margin: 20px 0;
            }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                margin-bottom: 15px;
            }}
            .details-table td {{
                padding: 3px 8px;
                vertical-align: top;
            }}
            .details-table td:first-child {{
                width: 25%;
                font-weight: bold;
            }}
            .details-table td:nth-child(2) {{
                width: 5%;
                text-align: center;
            }}
            .details-table td:nth-child(3) {{
                width: 25%;
            }}
            .details-table td:nth-child(4) {{
                width: 20%;
                font-weight: bold;
            }}
            .details-table td:nth-child(5) {{
                width: 5%;
                text-align: center;
            }}
            .details-table td:last-child {{
                width: 20%;
            }}
            .content-section {{
                margin: 25px 0;
                text-align: justify;
            }}
            .signature-section {{
                margin-top: 80px;
                text-align: center;
            }}
            .stamp-area {{
                width: 150px;
                height: 150px;
                border: 1px dashed #ccc;
                margin: 20px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                background-image: url('https://ftcl-portal.arcapps.org/files/fastrack_stamp.png');
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
            }}
            .to-section {{
                margin: 20px 0;
            }}
            .date-section {{
                text-align: right;
                margin: 10px 0;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Logo -->
            <div class="header">
                <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 60px;" />
            </div>
            
            <!-- Title Box -->
            <div class="title-box">
                TO WHOM IT MAY CONCERN
            </div>

            <!-- TO Section -->
            <div class="to-section">
                <p><strong>TO:</strong> &nbsp;&nbsp;{customer_name.upper()}</p>
                <p style="margin-left: 40px;">{customer_address}</p>
            </div>

            <!-- Date -->
            <div class="date-section">
                <strong>Date :</strong> {current_date}
            </div>

            <!-- Shipping Details -->
            <div class="details-section">
                <p><strong>Shipping Details:</strong></p>
                <table class="details-table">
                    <tr>
                        <td><strong>Shipper</strong></td>
                        <td>:</td>
                        <td>{doc.get('hbl_shipper', '') or ''}</td>
                        <td><strong>M/Vsl. Name</strong></td>
                        <td>:</td>
                        <td>{doc.get('m_vsl_name', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>HBL No</strong></td>
                        <td>:</td>
                        <td>{doc.get('hbl_id', '') or ''}</td>
                        <td><strong>Voyage</strong></td>
                        <td>:</td>
                        <td>{doc.get('mv_voyage_no', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>HBL Date</strong></td>
                        <td>:</td>
                        <td>{format_date(doc.get('hbl_date'), 'dd-MMM-yyyy') if doc.get('hbl_date') else ''}</td>
                        <td><strong>ETD</strong></td>
                        <td>:</td>
                        <td>{format_date(doc.get('hbl_etd'), 'dd-MMM-yyyy') if doc.get('hbl_etd') else ''}</td>
                    </tr>
                    <tr>
                        <td><strong>MBL No</strong></td>
                        <td>:</td>
                        <td>{doc.get('mbl_no', '') or ''}</td>
                        <td><strong>F/Vsl. Name</strong></td>
                        <td>:</td>
                        <td>{doc.get('fv', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>MBL Date</strong></td>
                        <td>:</td>
                        <td>{format_date(doc.get('mbl_date'), 'dd-MMM-yyyy') if doc.get('mbl_date') else ''}</td>
                        <td><strong>ETA</strong></td>
                        <td>:</td>
                        <td>{format_date(doc.get('eta'), 'dd-MMM-yyyy') if doc.get('eta') else ''}</td>
                    </tr>
                    <tr>
                        <td><strong>Consignee</strong></td>
                        <td>:</td>
                        <td>{doc.get('consignee', '') or ''}</td>
                        <td><strong>Inco Terms</strong></td>
                        <td>:</td>
                        <td>{doc.get('inco_term', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>L/C No.& Date</strong></td>
                        <td>:</td>
                        <td>{doc.get('lc_date', '') or ''}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td><strong>Port of Loading</strong></td>
                        <td>:</td>
                        <td>{doc.get('port_of_loading', '') or ''}</td>
                        <td><strong>Volume CBM</strong></td>
                        <td>:</td>
                        <td>{doc.get('hbl_vol_cbm', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>Port of Discharge</strong></td>
                        <td>:</td>
                        <td>{doc.get('port_of_discharge', '') or ''}</td>
                        <td><strong>Total (CTN/PKG)</strong></td>
                        <td>:</td>
                        <td>{doc.get('no_of_pkg_hbl', '') or ''}</td>
                    </tr>
                    <tr>
                        <td><strong>Port of Delivery</strong></td>
                        <td>:</td>
                        <td>{doc.get('port_of_delivery', '') or ''}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td><strong>Shipping Line</strong></td>
                        <td>:</td>
                        <td>{doc.get('shipping_line', '') or ''}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </table>

                <p><strong>Total Weight:</strong>  <strong>{doc.get('hbl_weight')} KG</strong></p>
                <p style="margin: 8px 0;">This is to certify that the Ocean Freight of the above mentioned shipment is as under:</p>
                 <p style="margin: 5px 0;"><strong>Ocean Freight </strong>  :  <strong> (US$){ocean_freight_rate}</strong></p>
                <p style="margin: 5px 0;"><strong>Total Container</strong>  : <strong>{container_volume}</strong></p>
                <p style="margin: 5px 0;"><strong>So, Total Ocean Freight is</strong>  : <strong> (US$){ocean_freight_total}</strong></p>
                <p style="margin: 5px 0;"><strong>Goods Description</strong> : <strong>{doc.get('description_of_good', '')}</strong></p>
            </div>

            <!-- Closing and Signature Section Combined -->
            <div style="margin: 15px 0;">
                <p style="margin: 5px 0;">Thanks and Best Regards,</p>
                <p style="margin: 5px 0;">Sincerely Yours,</p>
                
                <div style="margin: 15px 0; display: table; width: 100%;">
                    <div style="display: table-cell; width: 60%; vertical-align: top;">
                        <p style="margin: 5px 0;"><strong>For, Fastrack Cargo Solutions Ltd.</strong></p>
                        <p style="margin: 5px 0;"><strong>As Agent</strong></p>
                    </div>
                </div>
            </div>

            <!-- Footer -->
        </div>
    </body>
    </html>
    """
    
    return html_template


@frappe.whitelist()
def get_to_whom_concern_preview(doc_name):
    """Get HTML preview of To Whom It May Concern certificate (for testing)"""
    
    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Get customer info
        customer_name = ""
        customer_address = ""
        if doc.invoice_list and len(doc.invoice_list) > 0:
            customer = doc.invoice_list[0].customer
            if customer:
                try:
                    customer_doc = frappe.get_doc("Customer", customer)
                    customer_name = customer_doc.customer_name or customer
                    customer_address = customer_doc.primary_address or ""
                except:
                    customer_name = customer
                    customer_address = ""
        
        # Generate and return HTML content
        html_content = get_to_whom_concern_html(doc, customer_name, customer_address)
        return {"html": html_content}
        
    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")