import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url


@frappe.whitelist()
def download_sea_import_invoice_bdt_pdf(doc_name, invoice_ids=None):
    print(doc_name, invoice_ids)
    """Download Sea Import Invoice BDT as PDF using HTML template"""
    
    try:
        # Get the document
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        invoice_list = doc.invoice_list
        # filter if invoice_ids is not None
        print(invoice_list)
        if invoice_ids:
            # make array of invoice_ids
            invoice_ids = invoice_ids.split(",")
            print(invoice_ids)
            invoice_list = [invoice for invoice in invoice_list if invoice.name in invoice_ids]
            print(invoice_list)
        doc.invoice_list = invoice_list
        print(doc.invoice_list)
        
        # Get customer address
        customer_address = ""
        if doc.invoice_list and len(doc.invoice_list) > 0:
            customer = doc.invoice_list[0].customer
            if customer:
                try:
                    customer_doc = frappe.get_doc("Customer", customer)
                    customer_address = customer_doc.primary_address or ""
                except:
                    customer_address = ""
        
        # Generate HTML content
        html_content = get_sea_import_invoice_bdt_html(doc, customer_address)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set filename
        filename = f"Sea_Import_Invoice_BDT_{doc_name}.pdf"
        
        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_sea_import_invoice_bdt_html(doc, customer_address):
    """Generate HTML content for Sea Import Invoice BDT"""
    
    # Get customer info
    customer_name = ""
    if doc.invoice_list and len(doc.invoice_list) > 0:
        customer_name = doc.invoice_list[0].customer or ""
    
    # Get container volume
    container_volume_list = []
    if hasattr(doc, 'container_cost_info') and doc.container_cost_info:
        for container in doc.container_cost_info:
            qty = container.get('qty', '') or ''
            size = container.get('size', '') or ''
            if qty and size:
                container_volume_list.append(f"{qty}x{size}")
    container_volume = ", ".join(container_volume_list)
    
    # Get container numbers
    container_numbers = []
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            container_no = container.get('custom_container_no', '') or ''
            size = container.get('size', '') or ''
            if container_no:
                container_numbers.append(f"{container_no}/{size}")
    if len(container_numbers) > 6:
        container_numbers_str = "Qty: " + str(len(container_numbers))
    else:
        container_numbers_str = ", ".join(container_numbers)
    
    # Get invoice items
    invoice_rows = ""
    total_amount_bdt = 0
    if hasattr(doc, 'invoice_list') and doc.invoice_list:
        for idx, item in enumerate(doc.invoice_list):
            rate = item.get('rate', 0) or 0
            total_price = item.get('total_price', 0) or 0
            exchange_rate = item.get('exchange_rate', 0) or 0
            base_net_amount = item.get('base_net_amount', 0) or 0
            total_amount_bdt += float(base_net_amount) if base_net_amount else 0
            
            if idx == 0:  # First row with rowspan for container number
                invoice_rows += f"""
                <tr>
                    <td rowspan="{len(doc.invoice_list)}" style="border: 1px solid black; padding: 5px; text-align: center; vertical-align: middle;">
                        {container_numbers_str}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('item_code', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('qty', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {rate}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('currency', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {total_price}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {exchange_rate}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {base_net_amount}
                    </td>
                </tr>
                """
            else:  # Subsequent rows without container number column
                invoice_rows += f"""
                <tr>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('item_code', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('qty', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {rate}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {item.get('currency', '') or ''}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {total_price}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {exchange_rate}
                    </td>
                    <td style="border: 1px solid black; padding: 5px;">
                        {base_net_amount}
                    </td>
                </tr>
                """
    else:
        # Default empty row if no invoice data
        invoice_rows = """
        <tr>
            <td style="border: 1px solid black; padding: 5px; text-align: center;">-</td>
            <td style="border: 1px solid black; padding: 5px;">-</td>
            <td style="border: 1px solid black; padding: 5px;">-</td>
            <td style="border: 1px solid black; padding: 5px;">-</td>
            <td style="border: 1px solid black; padding: 5px;">-</td>
            <td style="border: 1px solid black; padding: 5px;">-</td>
        </tr>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sea Import Invoice BDT</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                margin: 0;
                padding: 20px;
                background: white;
                color: black;
            }}
            .container {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }}
            .header-section {{
                display: table;
                width: 100%;
                margin-bottom: 12px;
            }}
            .header-left {{
                display: table-cell;
                width: 60%;
                vertical-align: top;
            }}
            .header-right {{
                display: table-cell;
                width: 38%;
                text-align: right;
                vertical-align: top;
            }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                margin-bottom: 20px;
            }}
            .details-table td {{
                padding: 3px 5px;
                vertical-align: top;
            }}
            .charges-table {{
                width: 100%;
                border-collapse: collapse;
                text-align: center;
                font-size: 12px;
                border: 1px solid black;
            }}
            .charges-table th,
            .charges-table td {{
                border: 1px solid black;
                padding: 5px;
            }}
            .charges-table th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .total-row {{
                text-align: right;
                font-weight: bold;
            }}
            hr {{
                border: none;
                border-top: 1px solid black;
                margin: 12px 0;
            }}
            h3, h4 {{
                margin: 10px 0;
            }}
            p {{
                margin: 2px 0;
                line-height: 1.4;
            }}
            ol {{
                margin-top: 4px;
                padding-left: 16px;
            }}
            li {{
                margin-bottom: 4px;
            }}
            .footer {{
                font-size: 11px;
                line-height: 1.4;
                text-align: center;
                color: black;
                margin-top: 40px;
                border-top: 1px solid black;
                padding-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Logo -->
            <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 55px;" />
            
            <!-- Title -->
            <div style="text-align: center; margin-bottom: 10px;">
                <h3 style="margin: 0;">SEA IMPORT INVOICE</h3>
            </div>

            <!-- Header Section -->
            <div class="header-section">
                <div class="header-left">
                    <p style="margin: 0;"><strong>TO:</strong> {customer_name}</p>
                    <p style="margin: 0;">{customer_address}</p>
                </div>
                <div class="header-right">
                    <p style="margin: 0;"><strong>Invoice No:</strong> {doc.get('hbl_id', '') or ''}</p>
                    <p style="margin: 0;"><strong>Date:</strong> {doc.get('hbl_date', '') or ''}</p>
                    <p style="margin: 0;"><strong>Currency:</strong> BDT</p>
                </div>
            </div>

            <hr>

            <!-- Shipping Details -->
            <h4>Shipping Details:</h4>
            <table class="details-table">
                <tr>
                    <td style="width: 20%;"><strong>Shipper:</strong></td>
                    <td style="width: 30%;">{doc.get('hbl_shipper', '') or ''}</td>
                    <td style="width: 20%;"><strong>M/Vsl. Name:</strong></td>
                    <td style="width: 30%;">{doc.get('m_vsl_name', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>HBL No:</strong></td>
                    <td>{doc.get('hbl_id', '') or ''}</td>
                    <td><strong>Voyage:</strong></td>
                    <td>{doc.get('mv_voyage_no', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>HBL Date:</strong></td>
                    <td>{doc.get('hbl_date', '') or ''}</td>
                    <td><strong>ETD:</strong></td>
                    <td>{doc.get('hbl_etd', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>MBL No:</strong></td>
                    <td>{doc.get('mbl_no', '') or ''}</td>
                    <td><strong>F/Vsl. Name:</strong></td>
                    <td>{doc.get('fv', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>MBL Date:</strong></td>
                    <td>{doc.get('mbl_date', '') or ''}</td>
                    <td><strong>ETA:</strong></td>
                    <td>{doc.get('eta', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>Bank:</strong></td>
                    <td>MODHUMOTI BANK LIMITED</td>
                    <td><strong>Inco Terms:</strong></td>
                    <td>{doc.get('inco_term', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>L/C No & Date:</strong></td>
                    <td>{doc.get('lc_date', '') or ''}</td>
                    <td><strong>Container Volume:</strong></td>
                    <td>{container_volume}</td>
                </tr>
                <tr>
                    <td><strong>Port of Loading:</strong></td>
                    <td>{doc.get('port_of_loading', '') or ''}</td>
                    <td><strong>Volume CBM:</strong></td>
                    <td>{doc.get('vol_cbm', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>Port of Discharge:</strong></td>
                    <td>{doc.get('port_of_discharge', '') or ''}</td>
                    <td><strong>Quantity:</strong></td>
                    <td>{doc.get('no_of_pkg_hbl', '') or ''}</td>
                </tr>
                <tr>
                    <td><strong>Port of Delivery:</strong></td>
                    <td>{doc.get('port_of_delivery', '') or ''}</td>
                    <td><strong>Shipping Line:</strong></td>
                    <td>{doc.get('shipping_line', '') or ''}</td>
                </tr>
            </table>

            <!-- Charges Table -->
            <h4 style="margin-top: 20px;">Charges</h4>
            <table class="charges-table">
                <thead>
                    <tr>
                        <th>Container Number</th>
                        <th>Particulars</th>
                        <th>Qty</th>
                        <th>Rate $</th>
                        <th>Currency</th>
                        <th>Total Price $</th>
                        <th>Ex. Rate</th>
                        <th>Total Price BDT</th>
                    </tr>
                </thead>
                <tbody>
                    {invoice_rows}
                    <tr>
                        <td colspan="7" class="total-row">
                            <strong>Total:</strong>
                        </td>
                        <td style="border: 1px solid black; padding: 5px;">
                            <strong>{total_amount_bdt:.2f}</strong>
                        </td>
                    </tr>
                </tbody>
            </table>

            <!-- Terms -->
            <p style="margin-top: 20px;"><strong>Terms:</strong></p>
            <ol>
                <li>We accept Pay Order / Cash Only.</li>
                <li>Payable in favor of FASTRACK CARGO SOLUTIONS LTD.</li>
                <li>All transactions are subject to FASTRACK CARGO SOLUTIONS LTD. terms and conditions, available upon request.</li>
                <li>If any dispute, please notify in written within 03 days upon receipt of this Invoice.</li>
            </ol>

            <!-- Footer -->
            <div class="footer">
                <p style="margin: 4px 0;">
                    <strong>DHAKA OFFICE :</strong> HOUSE # 14 (2nd Floor), ROAD#13/C, BLOCK # E, BANANI, DHAKA-1213, BANGLADESH<br />
                    Tel: +880-2-8836386, Fax: +880-2-8836374
                </p>
                <p style="margin: 4px 0;">
                    <strong>CHITTAGONG OFFICE :</strong> 259/A, HARUN BHABON (1st Floor), BADAMTOLI, SK.MUJIB ROAD, AGRABAD C/A, CHATTOGRAM<br />
                    Tel: +880-31-2527634
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


@frappe.whitelist()
def get_sea_import_invoice_bdt_preview(doc_name):
    """Get HTML preview of Sea Import Invoice BDT (for testing)"""
    
    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Get customer address
        customer_address = ""
        if doc.invoice_list and len(doc.invoice_list) > 0:
            customer = doc.invoice_list[0].customer
            if customer:
                try:
                    customer_doc = frappe.get_doc("Customer", customer)
                    customer_address = customer_doc.primary_address or ""
                except:
                    customer_address = ""
        
        # Generate and return HTML content
        html_content = get_sea_import_invoice_bdt_html(doc, customer_address)
        return {"html": html_content}
        
    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")