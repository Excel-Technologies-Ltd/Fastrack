import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, format_date, today
from fastrack_erp.report_api.report_helpers import (
    FASTTRACK_PDF_MAIN_CSS,
    get_fc_shipping_html,
    merge_fastrack_wkhtml_pdf_options,
)


def _download_fc_style_certificate_pdf(
    doc_name,
    parent_doctype,
    banner_title,
    html_title,
    filename_stem,
):
    doc = frappe.get_doc(parent_doctype, doc_name)
    customer_name = ""
    customer_address = ""
    if doc.invoice_list and len(doc.invoice_list) > 0:
        customer = doc.invoice_list[0].customer
        if customer:
            try:
                customer_doc = frappe.get_doc("Customer", customer)
                customer_name = customer_doc.customer_name or customer
                customer_address = customer_doc.primary_address or ""
            except Exception:
                customer_name = customer
                customer_address = ""
    html_content = get_to_whom_concern_html(
        doc,
        customer_name,
        customer_address,
        banner_title=banner_title,
        html_title=html_title,
    )
    pdf_content = get_pdf(
        html_content,
        options=merge_fastrack_wkhtml_pdf_options(),
    )
    safe_stem = filename_stem.replace(" ", "_")
    filename = f"{safe_stem}_{doc_name}.pdf"
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "download"


@frappe.whitelist()
def download_to_whom_concern_pdf(doc_name):
    """Download To Whom It May Concern certificate as PDF using HTML template"""
    try:
        _download_fc_style_certificate_pdf(
            doc_name,
            parent_doctype="Import Sea House Bill",
            banner_title="TO WHOM IT MAY CONCERN",
            html_title="To Whom It May Concern",
            filename_stem="To_Whom_Concern",
        )
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_export_fc_export_pdf(doc_name):
    """Download FC Export certificate (export sea HBL) as PDF."""
    try:
        _download_fc_style_certificate_pdf(
            doc_name,
            parent_doctype="Export Sea House Bill",
            banner_title="FC EXPORT",
            html_title="FC Export",
            filename_stem="FC_Export",
        )
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_export_shipping_pdf(doc_name):
    """Download Shipping Order certificate (export sea HBL) as PDF."""
    try:
        doc = frappe.get_doc("Export Sea House Bill", doc_name)
        html_content = get_export_shipping_order_html(doc)
        pdf_content = get_pdf(
            html_content,
            options=merge_fastrack_wkhtml_pdf_options(
                {
                    'orientation': 'Landscape',
                    'margin-left': '8mm',
                    'margin-right': '8mm',
                    'margin-top': '8mm',
                },
            ),
        )
        filename = f"Shipping_Order_{doc_name}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_export_shipping_order_html(doc):
    """Generate landscape Shipping Order HTML matching paper layout."""
    company_name = 'FASTRACK CARGO SOLUTIONS LTD'
    company_address = (
        'Anderkilla, Chatteshwari Road, Choumuhani, Agrabad C/A, '
        'Chittagong, Bangladesh'
    )
    company_contacts = (
        'Mobile: +880 1649255506, +880 1649755506  '
        'Email: sales@fastrackcargo.com'
    )
    company_email2 = 'import.cmf01@fastrackcargo.com.bd'
    ain = '30-15-6745'

    shipper = (
        doc.get('shipper_name')
        or doc.get('customer')
        or doc.get('consignor')
        or ''
    )
    cnf_agent = doc.get('cnf_agent') or doc.get('consignee_name') or ''
    place_of_receipt = doc.get('place_of_receipt') or ''
    stuffing_date = format_date(
        doc.get('stuffing_date') or today(),
        'dd-MM-yyyy',
    )
    vessel_voyage = (
        f"{doc.get('mv') or ''} {doc.get('mv_voyage_no') or ''}"
    ).strip()
    carrier = (
        doc.get('shipping_line')
        or doc.get('carrier')
        or doc.get('mbl_carrier')
        or 'SITC CONTAINER LINES CO.LTD'
    )
    booking_no = doc.get('booking_no') or doc.get('mbl') or ''
    hbl_no = doc.get('name') or 'FTCSCGP2601109'

    invoice_no = doc.get('invoice_no') or ''
    po_no = doc.get('po_no') or ''
    commodity = doc.get('description_of_good') or ''
    equipment = doc.get('container_type') or ''
    carton_qty = doc.get('no_of_pkg_hbl') or ''
    total_pcs = doc.get('no_of_pkg_hbl') or ''
    net_weight = doc.get('hbl_weight') or ''
    gross_weight = doc.get('gross_weight') or ''
    cbm = doc.get('cbm') or ''

    return f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Shipping Order</title>
        <style>
            {FASTTRACK_PDF_MAIN_CSS}
            @page {{
                size: A4 landscape;
                margin: 8mm;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 11px;
                margin: 0;
                color: #000;
            }}
            .so-page {{
                width: 100%;
            }}
            .so-head {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 8px;
            }}
            .so-head td {{
                vertical-align: top;
            }}
            .logo {{
                width: 120px;
            }}
            .title {{
                text-align: center;
                font-size: 30px;
                letter-spacing: 1px;
                margin-top: 28px;
            }}
            .line {{
                margin: 2px 0;
                white-space: nowrap;
            }}
            .label {{
                display: inline-block;
                width: 130px;
            }}
            .right-head {{
                text-align: left;
                padding-left: 20px;
                padding-top: 0;
            }}
            .item-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
            }}
            .item-table th,
            .item-table td {{
                border: 1px solid #000;
                padding: 6px 4px;
                text-align: center;
                font-size: 11px;
            }}
            .item-table th {{
                font-weight: bold;
            }}
            .sign-row {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 28px;
            }}
            .sign-row td {{
                width: 33.33%;
                vertical-align: bottom;
            }}
            .stamp {{
                width: 95px;
                height: 95px;
                background-image: url(
                    'https://ftcl-portal.arcapps.org/files/fastrack_stamp.png'
                );
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                margin: 0 auto;
            }}
            .right-sign {{
                text-align: right;
            }}
            .right-meta {{
                text-align: right;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class='so-page ft-pdf-main'>
            <table class='so-head'>
                <tr>
                    <td style='width: 42%;'>
                        <img class='logo'
                            src='https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg'
                            alt='Fastrack'>
                    </td>
                    <td style='width: 26%;'>
                        <div class='title'>SHIPPING ORDER</div>
                    </td>
                    <td style='width: 32%;'></td>
                </tr>
                <tr>
                    <td>
                        <div><strong>{company_name}</strong></div>
                        <div>{company_address}</div>
                        <div>{company_contacts}</div>
                        <div>{company_email2}</div>
                        <div style='margin-top: 4px;'>
                            <strong>AIN NO:</strong> {ain}
                        </div>
                    </td>
                    <td></td>
                    <td class='right-head'>
                        <div class='line'>
                            <span class='label'>Shipper:</span>{shipper}
                        </div>
                        <div class='line'>
                            <span class='label'>C&amp;F Agent:</span>{cnf_agent}
                        </div>
                        <div class='line'>
                            <span class='label'>Place of Receipt:</span>
                            {place_of_receipt}
                        </div>
                        <div class='line'>
                            <span class='label'>Stuffing Date:</span>
                            {stuffing_date}
                        </div>
                    </td>
                </tr>
            </table>

            <table class='item-table'>
                <thead>
                    <tr>
                        <th>Com Inv No.</th>
                        <th>P.O No</th>
                        <th>Commodity</th>
                        <th>Equipment</th>
                        <th>Carton Qty</th>
                        <th>Total PCS.</th>
                        <th>Net Weight</th>
                        <th>G. Weight</th>
                        <th>CBM</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{invoice_no}</td>
                        <td>{po_no}</td>
                        <td>{commodity}</td>
                        <td>{equipment}</td>
                        <td>{carton_qty}</td>
                        <td>{total_pcs}</td>
                        <td>{net_weight}</td>
                        <td>{gross_weight}</td>
                        <td>{cbm}</td>
                    </tr>
                    <tr>
                        <td colspan='9' style='text-align: center;'>
                            TOTAL:
                        </td>
                    </tr>
                </tbody>
            </table>

            <table class='sign-row'>
                <tr>
                    <td>
                        <div>Authorized</div>
                    </td>
                    <td style='text-align: center;'>
                        <div class='stamp'></div>
                    </td>
                    <td class='right-sign'>
                        <div class='right-meta'>
                            <div>Vessel/Voyage: {vessel_voyage}</div>
                            <div>Carrier: {carrier}</div>
                            <div>Booking No: {booking_no}</div>
                            <div>HBL No: {hbl_no}</div>
                        </div>
                        <div style='margin-top: 4px;'>
                            Signature of Shipper/C&amp;F Agent
                        </div>
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """


def get_to_whom_concern_html(
    doc,
    customer_name,
    customer_address,
    banner_title="TO WHOM IT MAY CONCERN",
    html_title="To Whom It May Concern",
):
    """Generate HTML content for FC-style certificate (import or export)."""
    
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
        <div class="container ft-pdf-main">
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
                            {banner_title}
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
                        <p style="margin: 5px 0; margin-left: 50px; margin-top: 30px;"><strong>As Agent</strong></p>
                    </div>
                </div>
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