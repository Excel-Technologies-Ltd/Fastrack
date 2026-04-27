import html

import frappe
from frappe.utils import getdate
from frappe.utils.pdf import get_pdf
from fastrack_erp.report_api.report_helpers import (
    FASTTRACK_PDF_MAIN_CSS,
    get_arrival_notice_shipping_html,
    merge_fastrack_wkhtml_pdf_options,
)


def _igm_escape(val):
    if val is None or val == '':
        return ''
    return html.escape(str(val), quote=False)


def _igm_customer_display(link_name):
    if not link_name:
        return ''
    name = frappe.db.get_value('Customer', link_name, 'customer_name')
    return _igm_escape(name or link_name)


def _igm_year(doc):
    for fld in ('eta', 'hbl_etd', 'mbl_date', 'hbl_date'):
        v = doc.get(fld)
        if v:
            try:
                return str(getdate(v).year)
            except Exception:
                continue
    return ''


def _igm_format_qty(val):
    if val is None or val == '':
        return ''
    try:
        return f'{int(val):,}'
    except (TypeError, ValueError):
        return _igm_escape(val)


def _igm_format_gross(val):
    if val is None or val == '':
        return ''
    try:
        return _igm_escape(f'{float(val):,.2f} KGS')
    except (TypeError, ValueError):
        return _igm_escape(str(val))


def _igm_container_lines(doc):
    lines = []
    rows = getattr(doc, 'container_info', None) or doc.get('container_info') or []
    for c in rows:
        c = c if isinstance(c, dict) else c.as_dict()
        cno = (c.get('custom_container_no') or '').strip()
        seal = (c.get('seal_no') or '').strip()
        size = c.get('size')
        if size and not isinstance(size, str):
            size = getattr(size, 'name', None) or str(size)
        size = (size or '').strip()
        line = cno
        if size:
            line += f' /{size}'
        if seal:
            line += f' SN: {seal}'
        line = line.strip()
        if line:
            lines.append(_igm_escape(line))
    return '<br/>'.join(lines)


def _igm_date_field(doc, fieldname):
    v = doc.get(fieldname)
    if not v:
        return ''
    try:
        return _igm_escape(getdate(v).strftime('%d-%m-%Y'))
    except Exception:
        return _igm_escape(str(v))


def get_igm_html(doc, _customer_name=''):
    """Import General Manifest Sup (IGM) layout — wide manifest table + summary."""

    mbl_display = _igm_escape(str(doc.get('mbl_no') or ''))
    bl_number = _igm_escape((doc.get('bl_no') or doc.get('hbl_id') or '').strip())
    master_line = _igm_escape(str(doc.get('line_no') or '').strip())
    line_no = _igm_escape(str(doc.get('hbl_line_no') or '').strip())
    pkg_desc = _igm_escape(str(doc.get('pkg_name') or '').strip())
    marks = _igm_escape(str(doc.get('marks_and_numbers') or '').strip())
    goods = _igm_escape(str(doc.get('description_of_good') or '').strip())
    consignee = _igm_customer_display(doc.get('hbl_consignee'))
    notify = _igm_customer_display(doc.get('notify_to'))
    status = _igm_escape(
        str(doc.get('container_type') or doc.get('container_mode') or doc.get('status') or '').strip()
    )
    perishable = _igm_escape(str(doc.get('dg_status') or '').strip())
    remark = _igm_escape(
        str(doc.get('remarks') or doc.get('hbl_remarks') or '').strip()
    )
    net_wt = ''
    nw = doc.get('hbl_weight')
    if nw not in (None, '', 0):
        try:
            net_wt = _igm_escape(f'{float(nw):,.2f} KGS')
        except (TypeError, ValueError):
            net_wt = _igm_escape(str(nw))

    rotation = _igm_escape(str(doc.get('rotation') or '').strip())
    sailed_year = _igm_escape(_igm_year(doc) or '')
    vessel = _igm_escape(str(doc.get('mv') or '').strip())
    voyage = _igm_escape(str(doc.get('mv_voyage_no') or '').strip())

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Import General Manifest Sup (IGM)</title>
        <style>
            {FASTTRACK_PDF_MAIN_CSS}
            @page {{
                size: A4 landscape;
                margin: 8mm 10mm 8mm 10mm;
            }}
            html, body {{
                height: 100%;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 8px;
                color: #000;
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            .igm-wrap {{
                width: 100%;
                box-sizing: border-box;
                padding-bottom: 4mm;
            }}
            .igm-title {{
                font-size: 13px;
                font-weight: bold;
                text-align: left;
                margin: 0 0 8px 0;
            }}
            .igm-summary-wrap {{
                width: 30%;
                max-width: 30%;
                margin-bottom: 12px;
            }}
            .igm-summary {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            .igm-summary th,
            .igm-summary td {{
                border: 1px solid #000;
                padding: 6px 8px;
                vertical-align: middle;
            }}
            .igm-summary th {{
                font-weight: bold;
                font-size: 8px;
                text-align: center;
            }}
            .igm-summary td {{
                text-align: left;
                font-size: 9px;
            }}
            .igm-main {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                margin-bottom: 6mm;
            }}
            .igm-main th {{
                border: 1px solid #000;
                padding: 7px 4px;
                font-size: 7px;
                font-weight: bold;
                text-align: center;
                vertical-align: middle;
                text-transform: uppercase;
                line-height: 1.25;
            }}
            .igm-main td {{
                border: 1px solid #000;
                padding: 10px 6px;
                font-size: 7.5px;
                line-height: 1.45;
                vertical-align: top;
                text-align: left;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="igm-wrap">
            <div class="igm-title">Import General Manifest Sup (IGM)</div>
            <div class="igm-summary-wrap">
                <table class="igm-summary">
                    <thead>
                        <tr>
                            <th>Sailed Year</th>
                            <th>Ship&apos;s Name</th>
                            <th>Voy. No</th>
                            <th>Import Rot No.</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{sailed_year}</td>
                            <td>{vessel}</td>
                            <td>{voyage}</td>
                            <td>{rotation}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <table class="igm-main">
                <thead>
                    <tr>
                        <th style="width:3.5%;">Master<br/>Line</th>
                        <th style="width:6%;">MBL<br/>No</th>
                        <th style="width:3.5%;">Line<br/>No</th>
                        <th style="width:7%;">BL<br/>Number</th>
                        <th style="width:5%;">Number of<br/>Quantity</th>
                        <th style="width:5%;">Description</th>
                        <th style="width:9%;">Mark &amp;<br/>Number</th>
                        <th style="width:11%;">Description<br/>of Goods</th>
                        <th style="width:5%;">Date of<br/>Entry</th>
                        <th style="width:5%;">Conts<br/>Licence</th>
                        <th style="width:8%;">Consignee</th>
                        <th style="width:8%;">Notify<br/>Party</th>
                        <th style="width:6%;">Gross<br/>Weight</th>
                        <th style="width:5%;">Net<br/>Weight</th>
                        <th style="width:8%;">Container</th>
                        <th style="width:4%;">Status</th>
                        <th style="width:5.5%;">PERISH<br/>ABLE</th>
                        <th style="width:5.5%;">RE<br/>MARK</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{master_line}</td>
                        <td>{mbl_display}</td>
                        <td>{line_no}</td>
                        <td>{bl_number}</td>
                        <td>{_igm_format_qty(doc.get('no_of_pkg_hbl'))}</td>
                        <td>{pkg_desc}</td>
                        <td>{marks}</td>
                        <td>{goods}</td>
                        <td>{_igm_date_field(doc, 'bill_of_entry_date')}</td>
                        <td>{_igm_escape(str(doc.get('bill_of_entry') or '').strip())}</td>
                        <td>{consignee}</td>
                        <td>{notify}</td>
                        <td>{_igm_format_gross(doc.get('gross_weight'))}</td>
                        <td>{net_wt}</td>
                        <td>{_igm_container_lines(doc)}</td>
                        <td>{status}</td>
                        <td>{perishable}</td>
                        <td>{remark}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """


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
        pdf_content = get_pdf(
            html_content,
            options=merge_fastrack_wkhtml_pdf_options(),
        )

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
        html_content = get_igm_html(doc, customer_name)
        pdf_content = get_pdf(
            html_content,
            options=merge_fastrack_wkhtml_pdf_options(
                {'orientation': 'Landscape'},
            ),
        )
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
    """Generate HTML content for Arrival Notice."""
    
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
            {FASTTRACK_PDF_MAIN_CSS}
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
                margin-top: 12px;
            }}
            .footer-note {{
                font-size: 10px;
                font-weight: bold;
            }}
            .signature-section {{
                margin-top: 12px;
                margin-bottom: 6px;
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
            .center {{
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="document-container ft-pdf-main">
        

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
                    <div style="text-align: left;" class="signature-line"></div>
                    PREPARED BY</br>
                </div>
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