import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url, format_date, today
from fastrack_erp.report_api.invoice_list_bridge import (
    resolve_invoice_list_for_hbl_pdf,
)
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
    invoice_ids=None,
):
    doc = frappe.get_doc(parent_doctype, doc_name)
    resolve_invoice_list_for_hbl_pdf(doc, parent_doctype, invoice_ids)
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
def download_export_fc_export_pdf(doc_name, invoice_ids=None):
    """Download FC Export certificate (export sea HBL) as PDF."""
    try:
        doc = frappe.get_doc("Export Sea House Bill", doc_name)
        resolve_invoice_list_for_hbl_pdf(doc, "Export Sea House Bill", invoice_ids)

        # Normalize Export field names to match the shared FC template
        doc.hbl_etd = doc.get('etd') or ''
        doc.total_container_hbl = doc.get('total_container') or 0
        doc.hbl_weight = doc.get('gross_weight') or ''
        doc.lc = doc.get('lc_no') or ''
        doc.lc_date = doc.get('date_4') or ''

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
            banner_title="TO WHOM IT MAY CONCERN",
            html_title="TO WHOM IT MAY CONCERN",
        )
        pdf_content = get_pdf(html_content, options=merge_fastrack_wkhtml_pdf_options())
        frappe.local.response.filename = f"FC_Export_{doc_name}.pdf"
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_shipping_order_pdf(doc_name):
    """Download Shipping Order PDF directly from the Shipping Order doctype."""
    try:
        doc = frappe.get_doc("Shipping Order", doc_name)
        html_content = get_shipping_order_from_so_html(doc)
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
        frappe.local.response.filename = f"Shipping_Order_{doc_name}.pdf"
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_shipping_order_from_so_html(doc):
    """Generate landscape Shipping Order HTML from a Shipping Order document."""
    company_name = 'FASTRACK CARGO SOLUTIONS LTD.'
    company_addr1 = 'JAHAN CHAMBER (2ND FLOOR), 3048/4255, HALISHAHAR ROAD, CHOUMOHARI,'
    company_addr2 = 'Agrabad C/A, Chittagong. Bangladesh'
    company_cell = 'Cell: +880 1708544568 (DHK) / +880 1640753506 (CTG)'
    company_email1 = 'Email: sales@fastrackcargo.com.bd'
    company_email2 = 'Email: import.crm01@fastrackcargo.com.bd'
    ain = '301-16-0475'

    shipper = doc.shipper or ''
    cnf_agent = doc.cnf_agent or ''
    notify = doc.consignee or ''
    place_of_receipt = doc.place_of_receipt or ''
    destination = doc.destination or ''
    stuffing_date = format_date(doc.stuffing_date or today(), 'dd.MM.yyyy')
    vessel_voyage = doc.forworder or ''
    carrier = doc.carieer or ''
    booking_no = doc.booking_no or ''
    cfs = doc.cfs or ''
    hbl_no = doc.hbl_number or ''
    invoice_no = doc.invoice_no or ''
    po_no = doc.po_no or ''
    commodity = doc.commodity or ''
    net_weight = doc.net_weight or ''
    gross_weight = doc.gr_weight or ''
    cbm = doc.cbm or ''
    carton_qty = doc.carton_qty or ''
    total_pcs = doc.total_pcs or ''
    equipment = doc.equipment or ''

    from fastrack_erp.report_api.report_helpers import FASTTRACK_PDF_MAIN_CSS
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
            .so-page {{ width: 100%; }}
            .so-head {{ width: 100%; border-collapse: collapse; margin-bottom: 6px; }}
            .so-head td {{ vertical-align: top; }}
            .logo {{ height: 55px; }}
            .title {{ text-align: center; font-size: 22px; font-weight: bold; letter-spacing: 1px; }}
            .right-head-table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
            .right-head-table td {{ padding: 1px 3px; vertical-align: top; white-space: nowrap; }}
            .rh-label {{ font-weight: bold; width: 1%; white-space: nowrap; }}
            .rh-colon {{ width: 1%; text-align: center; }}
            .rh-value {{ white-space: normal; }}
            .item-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .item-table th, .item-table td {{
                border: 1px solid #000; padding: 5px 4px;
                text-align: center; font-size: 11px;
            }}
            .item-table th {{ font-weight: bold; background-color: #f9f9f9; text-decoration: underline; }}
            .sign-header {{ width: 100%; border-collapse: collapse; margin-top: 18px; }}
            .sign-header td {{ padding: 2px 0; font-size: 11px; }}
            .sign-row {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
            .sign-row td {{ width: 33.33%; vertical-align: bottom; padding-top: 6px; }}
            .stamp {{
                width: 90px; height: 90px;
                background-image: url('https://ftcl-portal.arcapps.org/files/fastrack_stamp.png');
                background-size: contain; background-repeat: no-repeat;
                background-position: center; margin: 0 auto;
            }}
            .right-meta {{ text-align: right; line-height: 1.8; }}
            .right-meta table {{ margin-left: auto; border-collapse: collapse; }}
            .right-meta td {{ padding: 0 2px; text-align: left; }}
            .right-meta .ml {{ font-weight: bold; white-space: nowrap; }}
        </style>
    </head>
    <body>
        <div class='so-page ft-pdf-main'>
            <table class='so-head'>
                <tr>
                    <td style='width:30%; vertical-align:middle;'>
                        <img class='logo'
                            src='https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg'
                            alt='Fastrack'>
                    </td>
                    <td style='width:40%; text-align:center; vertical-align:middle;'>
                        <div class='title'>SHIPPING ORDER</div>
                    </td>
                    <td style='width:30%;'></td>
                </tr>
                <tr>
                    <td style='vertical-align:top; padding-top:4px;'>
                        <div><strong>{company_name}</strong></div>
                        <div>{company_addr1}</div>
                        <div>{company_addr2}</div>
                        <div>{company_cell}</div>
                        <div>{company_email1}</div>
                        <div>{company_email2}</div>
                        <div style='margin-top:4px;'><strong>AIN NO: {ain}</strong></div>
                    </td>
                    <td></td>
                    <td style='vertical-align:top; padding-top:4px;'>
                        <table class='right-head-table'>
                            <tr>
                                <td class='rh-label'>Shipper</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{shipper}</td>
                            </tr>
                            <tr>
                                <td class='rh-label'>C&amp;F Agent</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{cnf_agent}</td>
                            </tr>
                            <tr>
                                <td class='rh-label'>Notify</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{notify}</td>
                            </tr>
                            <tr>
                                <td class='rh-label' style='white-space:nowrap;'>Place of Receipt</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>
                                    {place_of_receipt}
                                    &nbsp;&nbsp;&nbsp;
                                    <strong>Destination:</strong>&nbsp;{destination}
                                </td>
                            </tr>
                            <tr>
                                <td class='rh-label'>Stuffing Date</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{stuffing_date}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <table class='item-table'>
                <thead>
                    <tr>
                        <th>Invoice No.</th>
                        <th>P.O No</th>
                        <th>Commodity:</th>
                        <th>Equipment:</th>
                        <th>Carton Qty:</th>
                        <th>Total PCS:</th>
                        <th>Net Weight:</th>
                        <th>G. Weight:</th>
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
                        <td colspan='4' style='text-align:right; font-weight:bold; border:1px solid #000; padding:5px 8px;'>
                            TOTAL:
                        </td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{carton_qty}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{total_pcs}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{net_weight}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{gross_weight}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{cbm}</strong></td>
                    </tr>
                </tbody>
            </table>

            <table class='sign-header'>
                <tr>
                    <td style='width:50%;'>To be field by Office</td>
                    <td style='width:50%; text-align:right;'>Signature of Shipper/C&amp;F Agent</td>
                </tr>
            </table>

            <table class='sign-row'>
                <tr>
                    <td style='vertical-align:bottom;'></td>
                    <td style='text-align:center; vertical-align:bottom;'>
                        <div class='stamp'></div>
                    </td>
                    <td style='vertical-align:bottom;'>
                        <div class='right-meta'>
                            <table>
                                <tr>
                                    <td class='ml'>Vessel/Voyage</td>
                                    <td style='padding-left:6px;'>{vessel_voyage}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>Carrier</td>
                                    <td style='padding-left:6px;'>: {carrier}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>Booking No</td>
                                    <td style='padding-left:6px;'>: {booking_no}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>CFS</td>
                                    <td style='padding-left:6px;'>: {cfs}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>HBL No</td>
                                    <td style='padding-left:6px;'>: {hbl_no}</td>
                                </tr>
                            </table>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan='3' style='padding-top:6px;'>
                        <strong>Authorized</strong>
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """


@frappe.whitelist()
def download_export_shipping_pdf(doc_name, invoice_ids=None):
    """Download Shipping Order certificate (export sea HBL) as PDF."""
    try:
        doc = frappe.get_doc("Export Sea House Bill", doc_name)
        resolve_invoice_list_for_hbl_pdf(
            doc,
            'Export Sea House Bill',
            invoice_ids,
        )
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
    company_name = 'FASTRACK CARGO SOLUTIONS LTD.'
    company_addr1 = 'JAHAN CHAMBER (2ND FLOOR), 3048/4255, HALISHAHAR ROAD, CHOUMOHARI,'
    company_addr2 = 'Agrabad C/A, Chittagong. Bangladesh'
    company_cell = 'Cell: +880 1708544568 (DHK) / +880 1640753506 (CTG)'
    company_email1 = 'Email: sales@fastrackcargo.com.bd'
    company_email2 = 'Email: import.crm01@fastrackcargo.com.bd'
    ain = '301-16-0475'

    shipper = doc.get('hbl_shipper') or doc.get('shipper_name') or doc.get('customer') or ''
    cnf_agent = doc.get('cf_agent') or doc.get('cnf_agent') or ''
    notify = doc.get('notify_to') or doc.get('notify') or ''
    place_of_receipt = doc.get('port_of_receipt') or doc.get('place_of_receipt') or ''
    destination = doc.get('port_of_discharge') or doc.get('port_of_delivery') or doc.get('destination') or ''
    stuffing_date = format_date(
        doc.get('stuffing_date') or doc.get('etd') or today(),
        'dd.MM.yyyy',
    )

    vessel_voyage = (f"{doc.get('mv') or ''} {doc.get('mv_voyage_no') or ''}").strip()
    projected = (f"{doc.get('fv') or ''} {doc.get('fv__v_no') or ''}").strip()
    carrier = doc.get('shipping_line') or doc.get('carrier') or ''
    booking_no = doc.get('booking_no') or doc.get('mbl_no') or ''
    cfs = doc.get('cfs') or ''
    hbl_no = doc.get('hbl_no') or doc.get('hbl_id') or doc.get('name') or ''

    invoice_no = doc.get('inv_no') or doc.get('invoice_no') or ''
    po_no = doc.get('po_no') or doc.get('sc_no') or ''
    commodity = doc.get('description_of_good') or ''
    net_weight = doc.get('hbl_weight') or doc.get('net_weight') or ''
    gross_weight = doc.get('gross_weight') or ''
    cbm = doc.get('hbl_vol_cbm') or doc.get('cbm') or ''
    carton_qty = doc.get('no_of_pkg_hbl') or ''
    total_pcs = doc.get('total_pcs') or doc.get('no_of_pcs') or doc.get('total_no_of_cartons') or ''

    # Build equipment string from container_info
    equipment_parts = []
    container_info = doc.get('container_info') or []
    for c in container_info:
        qty = c.get('no_of_pkg') or ''
        size = c.get('size') or ''
        if qty and size:
            equipment_parts.append(f"{qty}X{size}")
    equipment = ', '.join(equipment_parts) or doc.get('container_type') or ''

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
                margin-bottom: 6px;
            }}
            .so-head td {{
                vertical-align: top;
            }}
            .logo {{
                height: 55px;
            }}
            .title {{
                text-align: center;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            .right-head-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11px;
            }}
            .right-head-table td {{
                padding: 1px 3px;
                vertical-align: top;
                white-space: nowrap;
            }}
            .rh-label {{
                font-weight: bold;
                width: 1%;
                white-space: nowrap;
            }}
            .rh-colon {{
                width: 1%;
                text-align: center;
            }}
            .rh-value {{
                white-space: normal;
            }}
            .item-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .item-table th,
            .item-table td {{
                border: 1px solid #000;
                padding: 5px 4px;
                text-align: center;
                font-size: 11px;
            }}
            .item-table th {{
                font-weight: bold;
                background-color: #f9f9f9;
                text-decoration: underline;
            }}
            .sign-header {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 18px;
            }}
            .sign-header td {{
                padding: 2px 0;
                font-size: 11px;
            }}
            .sign-row {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
            }}
            .sign-row td {{
                width: 33.33%;
                vertical-align: bottom;
                padding-top: 6px;
            }}
            .stamp {{
                width: 90px;
                height: 90px;
                background-image: url('https://ftcl-portal.arcapps.org/files/fastrack_stamp.png');
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                margin: 0 auto;
            }}
            .right-meta {{
                text-align: right;
                line-height: 1.8;
            }}
            .right-meta table {{
                margin-left: auto;
                border-collapse: collapse;
            }}
            .right-meta td {{
                padding: 0 2px;
                text-align: left;
            }}
            .right-meta .ml {{
                font-weight: bold;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class='so-page ft-pdf-main'>

            <!-- ===== HEADER ===== -->
            <table class='so-head'>
                <tr>
                    <td style='width:30%; vertical-align:middle;'>
                        <img class='logo'
                            src='https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg'
                            alt='Fastrack'>
                    </td>
                    <td style='width:40%; text-align:center; vertical-align:middle;'>
                        <div class='title'>SHIPPING ORDER</div>
                    </td>
                    <td style='width:30%;'></td>
                </tr>
                <tr>
                    <td style='vertical-align:top; padding-top:4px;'>
                        <div><strong>{company_name}</strong></div>
                        <div>{company_addr1}</div>
                        <div>{company_addr2}</div>
                        <div>{company_cell}</div>
                        <div>{company_email1}</div>
                        <div>{company_email2}</div>
                        <div style='margin-top:4px;'><strong>AIN NO: {ain}</strong></div>
                    </td>
                    <td></td>
                    <td style='vertical-align:top; padding-top:4px;'>
                        <table class='right-head-table'>
                            <tr>
                                <td class='rh-label'>Shipper</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{shipper}</td>
                            </tr>
                            <tr>
                                <td class='rh-label'>C&amp;F Agent</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{cnf_agent}</td>
                            </tr>
                            <tr>
                                <td class='rh-label'>Notify</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{notify}</td>
                            </tr>
                            <tr>
                                <td class='rh-label' style='white-space:nowrap;'>Place of Receipt</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>
                                    {place_of_receipt}
                                    &nbsp;&nbsp;&nbsp;
                                    <strong>Destination:</strong>&nbsp;{destination}
                                </td>
                            </tr>
                            <tr>
                                <td class='rh-label'>Stuffing Date</td>
                                <td class='rh-colon'>:</td>
                                <td class='rh-value'>{stuffing_date}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <!-- ===== ITEM TABLE ===== -->
            <table class='item-table'>
                <thead>
                    <tr>
                        <th>Invoice No.</th>
                        <th>P.O No</th>
                        <th>Commodity:</th>
                        <th>Equipment:</th>
                        <th>Carton Qty:</th>
                        <th>Total PCS:</th>
                        <th>Net Weight:</th>
                        <th>G. Weight:</th>
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
                        <td colspan='4' style='text-align:right; font-weight:bold; border:1px solid #000; padding:5px 8px;'>
                            TOTAL:
                        </td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{carton_qty}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{total_pcs}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{net_weight}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{gross_weight}</strong></td>
                        <td style='border:1px solid #000; padding:5px 4px;'><strong>{cbm}</strong></td>
                    </tr>
                </tbody>
            </table>

            <!-- ===== SIGNATURE SECTION ===== -->
            <table class='sign-header'>
                <tr>
                    <td style='width:50%;'>To be field by Office</td>
                    <td style='width:50%; text-align:right;'>Signature of Shipper/C&amp;F Agent</td>
                </tr>
            </table>

            <table class='sign-row'>
                <tr>
                    <td style='vertical-align:bottom;'>
                        <!-- authorized signature line placeholder -->
                    </td>
                    <td style='text-align:center; vertical-align:bottom;'>
                        <div class='stamp'></div>
                    </td>
                    <td style='vertical-align:bottom;'>
                        <div class='right-meta'>
                            <table>
                                <tr>
                                    <td class='ml'>Vessel/Voyage</td>
                                    <td style='padding-left:6px;'>{vessel_voyage}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>Projected MVSL</td>
                                    <td style='padding-left:6px;'>{projected}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>Carrier</td>
                                    <td style='padding-left:6px;'>: {carrier}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>Booking No</td>
                                    <td style='padding-left:6px;'>: {booking_no}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>CFS</td>
                                    <td style='padding-left:6px;'>: {cfs}</td>
                                </tr>
                                <tr>
                                    <td class='ml'>HBL No</td>
                                    <td style='padding-left:6px;'>: {hbl_no}</td>
                                </tr>
                            </table>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan='3' style='padding-top:6px;'>
                        <strong>Authorized</strong>
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
    
    # Get container volume and ocean freight details
    container_volume_list = []
    ocean_freight_parts = []
    ocean_freight_total = 0
    ocean_freight_total_bdt = 0
    exchange_rate = 0

    if hasattr(doc, 'container_cost_info') and doc.container_cost_info:
        for container in doc.container_cost_info:
            qty = container.get('qty', '') or ''
            size = container.get('size', '') or ''
            amount = container.get('amount', 0) or 0
            exchange_rate = container.get('ex_rate', 0) or 0
            if size:
                ocean_freight_parts.append(f"{amount}/{size}")
            if qty and size:
                container_volume_list.append(f"{qty}x{size}")
            try:
                if qty:
                    ocean_freight_total += float(amount) * int(qty)
            except (ValueError, TypeError):
                pass
            try:
                amountbdt = container.get('amountbdt', 0) or 0
                if amountbdt and qty:
                    ocean_freight_total_bdt += float(amountbdt)
            except (ValueError, TypeError):
                pass

    container_volume = ", ".join(container_volume_list)
    ocean_freight_rate = ", ".join(ocean_freight_parts)
    
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
                <p style="margin: 5px 0;"><strong>Exchange Rate</strong>  : <strong>{exchange_rate}</strong></p>

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