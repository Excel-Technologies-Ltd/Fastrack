import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url
from fastrack_erp.report_api.invoice_list_bridge import (
    resolve_invoice_list_for_hbl_pdf,
)
from fastrack_erp.report_api.report_helpers import (
    FASTTRACK_PDF_MAIN_CSS,
    get_invoice_usd_shipping_html,
    merge_fastrack_wkhtml_pdf_options,
)


def download_invoice_usd_pdf(
    doc_name,
    invoice_ids,
    parent_doctype,
    heading,
    html_title,
    filename_prefix,
):
    """Build Sea/Air/D2D-style sales invoice USD PDF for any supported HBL doctype."""
    try:
        doc = frappe.get_doc(parent_doctype, doc_name)
        resolve_invoice_list_for_hbl_pdf(doc, parent_doctype, invoice_ids)
        customer_address = ""
        if doc.invoice_list and len(doc.invoice_list) > 0:
            customer = doc.invoice_list[0].customer
            if customer:
                try:
                    customer_doc = frappe.get_doc("Customer", customer)
                    customer_address = customer_doc.primary_address or ""
                except Exception:
                    customer_address = ""
        html_content = get_import_invoice_usd_html(
            doc, customer_address, heading=heading, html_title=html_title
        )
        pdf_content = get_pdf(
            html_content,
            options=merge_fastrack_wkhtml_pdf_options(),
        )
        safe_stem = filename_prefix.replace(" ", "_")
        filename = f"{safe_stem}_{doc_name}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_sea_import_invoice_usd_pdf(doc_name, invoice_ids=None):
    """Download Sea Import Invoice USD as PDF using HTML template"""
    download_invoice_usd_pdf(
        doc_name,
        invoice_ids,
        parent_doctype="Import Sea House Bill",
        heading="SEA IMPORT INVOICE",
        html_title="Sea Import Invoice USD",
        filename_prefix="Sea_Import_Invoice_USD",
    )


@frappe.whitelist()
def download_sea_import_invoice_from_mbl_usd_pdf(doc_name, invoice_ids=None):
    """Portal builds may still call this dotted path; delegates to MBL module."""
    from fastrack_erp.report_api.import_sea_invoice_from_mbl_usd import (
        download_sea_import_invoice_from_mbl_usd_pdf as _mbl_pdf,
    )

    return _mbl_pdf(doc_name, invoice_ids)


def get_import_invoice_usd_html(
    doc,
    customer_address,
    heading="SEA IMPORT INVOICE",
    html_title="Sea Import Invoice USD",
):
    """Generate HTML content for import/export-style Invoice USD."""
    
    # Get customer info
    customer_name = ""
    if doc.invoice_list and len(doc.invoice_list) > 0:
        customer_name = doc.invoice_list[0].customer or ""

    inv_date = doc.get('hbl_date') or doc.get('mbl_date') or ''

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
                container_numbers.append((container_no, size))  # store as tuple

    if len(container_numbers) > 5:
        # Group by size
        size_count = {}
        for _, size in container_numbers:
            size_count[size] = size_count.get(size, 0) + 1
        
        # Create grouped string like "20ft: 3, 40ft: 2"
        grouped = [f"{size}/ {qty}" for size, qty in size_count.items()]
        container_numbers_str = "" + ", </br>".join(grouped)
    else:
        # List individually
        container_numbers_str = ", </br>".join(f"{no}/{size}" for no, size in container_numbers)
    
    # Get invoice items
    invoice_rows = ""
    total_amount = 0
    if hasattr(doc, 'invoice_list') and doc.invoice_list:
        for idx, item in enumerate(doc.invoice_list):
            rate = round(float(item.get('rate', 0) or 0), 2)
            total_price = round(float(item.get('total_price', 0) or 0), 2)
            total_amount += float(total_price) if total_price else 0
            
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
        </tr>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html_title}</title>
        <style>
            {FASTTRACK_PDF_MAIN_CSS}
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
                width: 32%;
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
        </style>
    </head>
    <body>
        <div class="container ft-pdf-main">
          
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
                        <h3 style="margin:0;">{heading}</h3>
                    </td>

                    <!-- Right: Empty (for balance) -->
                    <td style="width:25%;"></td>
                </tr>
            </table>

            <!-- Header Section: TO (left) | Invoice details (right) -->
            <table style="width:100%; border-collapse:collapse; margin-bottom:12px;">
                <tr>
                    <td style="width:60%; vertical-align:top;">
                        <p style="margin:0;"><strong>TO:</strong> {customer_name}</p>
                        <p style="margin:0;">{customer_address.split('#')[0] if customer_address else ''}</p>
                    </td>
                    <td style="width:40%; vertical-align:top;">
                        <table style="width:100%; border-collapse:collapse; font-size:12px;">
                            <tr>
                                <td style="width:40%; padding:2px 4px; text-align:left;"><strong>Invoice No</strong></td>
                                <td style="width:5%; text-align:center;"><strong>:</strong></td>
                                <td style="width:55%; padding:2px 4px; text-align:right;">{doc.get('invoice_uid', '') or ''}</td>
                            </tr>
                            <tr>
                                <td style="padding:2px 4px; text-align:left;"><strong>Date</strong></td>
                                <td style="text-align:center;"><strong>:</strong></td>
                                <td style="padding:2px 4px; text-align:right;">{inv_date}</td>
                            </tr>
                            <tr>
                                <td style="padding:2px 4px; text-align:left;"><strong>Currency</strong></td>
                                <td style="text-align:center;"><strong>:</strong></td>
                                <td style="padding:2px 4px; text-align:right;">USD</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <hr>

            <!-- Shipping Details -->
            <h4>Shipping Details:</h4>
            {get_invoice_usd_shipping_html(doc)}

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
                    </tr>
                </thead>
                <tbody>
                    {invoice_rows}
                    <tr>
                        <td colspan="5" class="total-row">
                            <strong>Total:</strong>
                        </td>
                        <td style="border: 1px solid black; padding: 5px;">
                            <strong>{total_amount:.2f}</strong>
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
        </div>
    </body>
    </html>
    """
    
    return html_template


@frappe.whitelist()
def get_sea_import_invoice_preview(doc_name):
    """Get HTML preview of Sea Import Invoice USD (for testing)"""
    
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
        html_content = get_import_invoice_usd_html(doc, customer_address)
        return {"html": html_content}
        
    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")