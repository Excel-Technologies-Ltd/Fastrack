import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url


@frappe.whitelist()
def download_delivery_order_pdf(doc_name="SHBL-00000064"):
    """Download Delivery Order as PDF using HTML template"""

    try:
        # Get the document
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)

        # Generate HTML content
        html_content = get_delivery_order_html(doc)

        # Generate PDF
        pdf_content = get_pdf(html_content)

        # Set filename
        filename = f"Delivery_Order_{doc_name}.pdf"

        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"

    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_delivery_order_html(doc):
    """Generate HTML content for Delivery Order"""

    # 1. Calculate Container Volume (Restored)
    container_volume_list = []
    if hasattr(doc, "container_cost_info") and doc.container_cost_info:
        for container in doc.container_cost_info:
            qty = container.get("qty", "") or ""
            size = container.get("size", "") or ""
            if qty and size:
                container_volume_list.append(f"{qty}x{size}")

    container_volume = ", ".join(container_volume_list)

    # 2. Generate Container Rows with Rowspan
    container_rows = ""
    goods_description = doc.get("description_of_good", "") or ""
    
    if hasattr(doc, "container_info") and doc.container_info:
        containers = list(doc.container_info)
        total_containers = len(containers)
        
        for idx, container in enumerate(containers):
            # Only generate the Goods Description cell on the very first row
            # and set its rowspan to the total number of containers.
            if idx == 0:
                gd_cell = f'<td rowspan="{total_containers}" style="border: 1px solid #000; padding: 4px; vertical-align: middle; text-align: center;">{goods_description}</td>'
            else:
                gd_cell = "" # Leave it empty for subsequent rows so it doesn't break the table
                
            container_rows += f"""
            <tr>
                <td style="border: 1px solid #000; padding: 4px;">{container.get("custom_container_no", "") or ""}</td>
                <td style="border: 1px solid #000; padding: 4px;">{container.get("seal_no", "") or ""}</td>
                <td style="border: 1px solid #000; padding: 4px;">{container.get("size", "") or ""}</td>
                <td style="border: 1px solid #000; padding: 4px;">{container.get("status", "") or ""}</td>
                {gd_cell}
            </tr>
            """
    else:
        container_rows = """
        <tr>
            <td style="border: 1px solid #000; padding: 4px;">-</td>
            <td style="border: 1px solid #000; padding: 4px;">-</td>
            <td style="border: 1px solid #000; padding: 4px;">-</td>
            <td style="border: 1px solid #000; padding: 4px;">-</td>
            <td style="border: 1px solid #000; padding: 4px;">-</td>
        </tr>
        """

    # 3. HTML Template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delivery Order</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                margin: 0;
                padding: 20px;
                background: white;
            }}
            .container {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }}
            .text-center {{
                text-align: center;
                margin-bottom: 15px;
            }}
            .text-right {{
                text-align: right;
            }}
            .mt-3 {{
                margin-top: 1.2rem;
            }}
            .mt-5 {{
                margin-top: 3rem;
            }}
            .mb-3 {{
                margin-bottom: 1rem;
            }}
            .row {{
                display: table;
                width: 100%;
                margin-bottom: 20px;
            }}
            .col-6 {{
                display: table-cell;
                width: 50%;
                vertical-align: top;
                padding-right: 15px;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .table th,
            .table td {{
                border: 1px solid #000;
                padding: 4px;
                vertical-align: top;
                font-size: 12px;
            }}
            .table th {{
                background-color: #f8f9fa;
                font-weight: bold;
                text-align: center;
            }}
            hr {{
                border: none;
                border-top: 1px solid #000;
                margin: 10px 0;
            }}
            h5 {{
                display: inline-block;
                border: 1px solid #000;
                padding: 4px 12px;
                font-weight: bold;
                margin: 0;
            }}
            p {{
                margin: 5px 0;
                line-height: 1.4;
            }}
            
            @media print {{
                body {{
                    font-size: 12px;
                }}
                .table th, 
                .table td {{
                    vertical-align: top;
                    font-size: 12px;
                    border: 1px solid #000 !important;
                }}
                .text-right {{
                    text-align: right;
                }}
                .mt-3 {{
                    margin-top: 1.2rem;
                }}
                .mt-5 {{
                    margin-top: 3rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="text-center">
                <h5>DELIVERY ORDER</h5>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="width: 40%; vertical-align: top; padding-right: 15px;">
                        <p style="margin-top: 0;"><strong>TO:</strong> Deputy Traffic Manager, <br>CHATTOGRAM</p>
                    </td>
                    
                    <td style="width: 60%; vertical-align: top;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="width: 35%; font-weight: bold; padding: 2px 0;">Date:</td>
                                <td style="padding: 2px 0;">{frappe.utils.today()}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">F/Vsl. Name:</td>
                                <td style="padding: 2px 0;">{doc.get("vessel_name", "") or "CNC NEPTUNE, V-0HJ8RS1NC"}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Rotation No.:</td>
                                <td style="padding: 2px 0;">{doc.get("rotation", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Line No.:</td>
                                <td style="padding: 2px 0;">{doc.get("line_no", "") or doc.get("hbl_line_no", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">From:</td>
                                <td style="padding: 2px 0;">{doc.get("port_of_loading", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">HBL No:</td>
                                <td style="padding: 2px 0;">{doc.get("hbl_id", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Bill of Entry:</td>
                                <td style="padding: 2px 0;">{doc.get("bill_of_entry", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Date:</td>
                                <td style="padding: 2px 0;">{doc.get("bill_of_entry_date", "") or ""}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Volume:</td>
                                <td style="padding: 2px 0;">{container_volume}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0;">Total Quantity:</td>
                                <td style="padding: 2px 0;">{int(doc.get("no_of_pkg_hbl", "") or 0)}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 2px 0; vertical-align: top;">Marks And<br>Number:</td>
                                <td style="padding: 2px 0;">{doc.get("marks_and_numbers", "") or ""}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <p><strong>Dear Sir,</strong></p>
            <p style="margin-top: -8px;">Please Deliver to M/S <strong>{doc.get("cf_agent", "S.F. TRADERS") or "S.F. TRADERS"}</strong> the following Goods:</p>

            <table class="table">
                <thead>
                    <tr>
                        <th>Container No.</th>
                        <th>Seal No.</th>
                        <th>Size</th>
                        <th>Mode</th>
                        <th>Goods Description</th>
                    </tr>
                </thead>
                <tbody>
                    {container_rows}
                </tbody>
            </table>

            <p class="text-right mt-3"><strong>Total Weight :</strong> {doc.get("gross_weight", "") or ""}</p>
            <p class="text-right"><strong>THIS DELIVERY ORDER IS VALID UP TO :</strong> {doc.get("do_validity", "") or ""}</p>

            <div class="text-right mt-5" style="margin-top:250px;">
                <p><strong>For, Fastrack Cargo Solutions Ltd.</strong></p>
                <p>As Agents</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_template

@frappe.whitelist()
def get_delivery_order_preview(doc_name):
    """Get HTML preview of Delivery Order (for testing)"""

    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)

        # Generate and return HTML content
        html_content = get_delivery_order_html(doc)
        return {"html": html_content}

    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")
