import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, format_date, today
from fastrack_erp.report_api.report_helpers import get_fc_shipping_html


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
    ocean_freight_rate = 0
    ocean_freight_total = 0
    ocean_freight_total_bdt = 0
    if hasattr(doc, 'container_cost_info') and doc.container_cost_info:
        for container in doc.container_cost_info:
            qty = container.get('qty', '') or ''
            size = container.get('size', '') or ''
            ocean_freight_rate += container.get('amount', 0) or 0
            if qty and size:
                container_volume_list.append(f"{qty}x{size}")
                ocean_freight_total += ocean_freight_rate * int(qty)
            if container.get('amountbdt') and int(qty):
                ocean_freight_total_bdt += int(container.get('amountbdt')) * int(qty)
                
    container_volume = ", ".join(container_volume_list)
    
    # amountbdt
    
    
    # Get ocean freight rate
    # ocean_freight_rate = doc.get('total')
    # ocean_freight_total = doc.get('total')

    
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
                padding-bottom: 80px;
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
            .footer {{
                font-size: 8px;
                line-height: 1.4;
                text-align: center;
                color: black;
                border-top: 1px solid black;
                padding-top: 10px;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                padding-left: 20px;
                padding-right: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header: Logo left, Title center -->
            <table style="width:100%; border-collapse:collapse; margin-bottom: 5px;">
                <tr>
                    <td style="width:25%; vertical-align:middle;">
                        <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg"
                            alt="Fasttrack Logo"
                            style="height:55px;">
                    </td>
                    <td style="width:50%; text-align:center; vertical-align:middle;">
                        <div style="border: 2px solid black; padding: 8px; display: inline-block; font-weight: bold; font-size: 14px;">
                            TO WHOM IT MAY CONCERN
                        </div>
                    </td>
                    <td style="width:25%;"></td>
                </tr>
            </table>

            <!-- TO Section -->
            <div class="to-section">
                <p><strong>TO:</strong> &nbsp;&nbsp;{customer_name.upper()}</p>
                <p style="margin-left: 40px;"> {customer_address.split('#')[0] if customer_address else ''} </p>
            </div>

            <!-- Date -->
            <div class="date-section">
                <strong>Date :</strong> {current_date}
            </div>

            <!-- Shipping Details -->
            <div class="details-section">
                <p><strong>Shipping Details:</strong></p>
                {get_fc_shipping_html(doc, format_date_fn=format_date)}

                <p><strong>Total Weight:</strong>  <strong>{doc.get('hbl_weight')} KG</strong></p> </br>
                <p style="margin: 8px 0;">This is to certify that the Ocean Freight of the above mentioned shipment is as under:</p>
                 <p style="margin: 5px 0;"><strong>Ocean Freight </strong>  :  <strong> (US$){ocean_freight_rate}</strong></p>
                <p style="margin: 5px 0;"><strong>Total Container</strong>  : <strong>{container_volume}</strong></p>
                <p style="margin: 5px 0;"><strong>So, Total Ocean Freight is</strong>  : <strong> (US$) {ocean_freight_total}{f' and BDT is {ocean_freight_total_bdt}' if ocean_freight_total_bdt else ''}</strong></p>
                
                <p style="margin: 5px 0;"><strong>Goods Description</strong> : <strong>{doc.get('description_of_good', '')}</strong></p>
            </div>

            <!-- Closing and Signature Section Combined -->
            <div style="margin: 15px 0;">
                <p style="margin: 5px 0;">Thanks and Best Regards,</p>
                <p style="margin: 5px 0;">Sincerely Yours,</p> </br></br>
                
                <div style="margin: 15px 0; display: table; width: 100%;">
                    <div style="display: table-cell; width: 60%; vertical-align: top;">
                        <p style="margin: 5px 0;"><strong>For, Fastrack Cargo Solutions Ltd.</strong></p>
                        <p style="margin: 5px 0;"><strong>As Agent</strong></p>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p style="margin: 4px 0;">
                    <strong>DHAKA OFFICE :</strong> 7th Floor, House: 11, Road: 4, Block : F, Banani, Dhaka 1213 Tel: +880-2-8836386, Fax: +880-2-8836374
                </p>
                <p style="margin: 4px 0;">
                    <strong>CHITTAGONG OFFICE :</strong> JAHAN CHAMBER(2ND FLOOR), 3048/4255 HALISHAHAR ROAD, CHOUMUHONI, AGRABAD C/A, CHATTOGRAM Tel: +880-31-2527634
                </p>
            </div>
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