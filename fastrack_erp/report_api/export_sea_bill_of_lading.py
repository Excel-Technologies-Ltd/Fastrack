import frappe
from frappe.utils.pdf import get_pdf


@frappe.whitelist()
def download_sea_bill_of_lading_draft_pdf(doc_name):
    """Download Sea Bill of Lading Draft as PDF"""

    try:
        # Get the document
        doc = frappe.get_doc("Export Sea House Bill", doc_name)

        # Generate HTML content for draft
        html_content = get_sea_bill_of_lading_html(doc, is_original=False)

        # Generate PDF
        pdf_content = get_pdf(html_content)

        # Set filename
        filename = f"Sea_Bill_of_Lading_Draft_{doc_name}.pdf"

        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"

    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


@frappe.whitelist()
def download_sea_bill_of_lading_original_pdf(doc_name):
    """Download Sea Bill of Lading Original as PDF"""

    try:
        # Get the document
        doc = frappe.get_doc("Export Sea House Bill", doc_name)

        # Generate HTML content for original
        html_content = get_sea_bill_of_lading_html(doc, is_original=True)

        # Generate PDF
        pdf_content = get_pdf(html_content)

        # Set filename
        filename = f"Sea_Bill_of_Lading_Original_{doc_name}.pdf"

        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"

    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_sea_bill_of_lading_html(doc, is_original=False):
    """Generate HTML content for Sea Bill of Lading matching the exact reference format"""

    # Page title based on version
    page_title = "BILL OF LADING - ORIGINAL" if is_original else "BILL OF LADING - DRAFT"

    # Build container detail table rows
    container_detail_rows = ""
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            container_detail_rows += f"""
            <tr>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; text-align: center;">{container.get('custom_container_no', '') or ''}</td>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; border-left: none; text-align: center;">{container.get('seal_no', '') or ''}</td>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; border-left: none; text-align: center;">{container.get('size', '') or ''}</td>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; border-left: none; text-align: center;">{container.get('no_of_pkg', '') or ''}</td>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; border-left: none; text-align: center;">{container.get('weight', '') or ''} KGS</td>
                <td style="padding: 3px; font-size: 7px; border: 1px solid #000; border-top: none; border-left: none; text-align: center;">{container.get('volume', '') or ''} CBM</td>
            </tr>
            """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{page_title}</title>
        <style>
            @page {{ size: A4; margin: 8mm; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 10px;
                line-height: 1.3;
                position: relative;
            }}
            .container {{
                position: relative;
            }}
            .page-title {{
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #000;
            }}
            table {{ width: 100%; border-collapse: collapse; }}
            .border {{ border: 1px solid #000; }}
            .border-top {{ border-top: 1px solid #000; }}
            .border-bottom {{ border-bottom: 1px solid #000; }}
            .border-left {{ border-left: 1px solid #000; }}
            .border-right {{ border-right: 1px solid #000; }}
            .no-border-top {{ border-top: none; }}
            .table-cell {{
                border: 1px solid #000;
                padding: 3px;
                font-size: 9px;
                text-align: center;
                border-top: none;
            }}
            .section-title {{ font-weight: normal; font-size: 9px; margin-bottom: 2px; }}
            .field-value {{
                font-size: 10px;
                min-height: 20px;
                padding: 3px 0;
            }}
            .text-center {{ text-align: center; }}
            .text-bold {{ font-weight: bold; }}
            .small-text {{ font-size: 8px; }}
            .tiny-text {{ font-size: 7px; line-height: 1.3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Page Title -->
            <div class="page-title">{page_title}</div>

            <!-- Main Table -->
            <table style="width: 100%; border: 1px solid #000; border-collapse: collapse;">
                <!-- Header Row -->
                <tr>
                    <td colspan="2" style="padding: 5px; font-size: 8px; text-align: center; border-bottom: 1px solid #000;">
                        (COMBINED TRANSPORT BILL OF LADING OR PORT TO PORT)
                    </td>
                    <td colspan="2" style="padding: 5px; font-size: 8px; text-align: right; border-bottom: 1px solid #000; border-left: 1px solid #000;">
                        (NOT NEGOTIABLE UNLESS CONSIGNED TO ORDER)
                    </td>
                </tr>

                <!-- Shipper Row -->
                <tr>
                    <td colspan="2" style="width: 50%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Shipper / Exporter:</div>
                        <div class="field-value">{doc.get('hbl_shipper', '') or ''}</div>
                    </td>
                    <td colspan="2" style="width: 50%; padding: 0; border-bottom: 1px solid #000; border-left: 1px solid #000;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="width: 30%; padding: 5px; text-align: center; border-right: 1px solid #000; vertical-align: middle;">
                                    <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" style="max-width: 100%; height: auto; max-height: 60px;" />
                                </td>
                                <td style="width: 70%; padding: 5px; vertical-align: top;">
                                    <div class="section-title">Bill of Lading No.:</div>
                                    <div class="field-value text-bold">{doc.get('hbl_id', '') or ''}</div>
                                    <div style="margin-top: 5px; font-weight: bold; font-size: 9px; color: #7CB342;">Fastrack Cargo Solutions, Ltd.</div>
                                    <div style="font-size: 7px; margin-top: 2px;">
                                        Tel: +880-2-48336368<br>
                                        Fax: +880-2-48336374<br>
                                        Email: sales@fastrackcargo.com.bd<br>
                                        Customs License No.: 101-163-04841
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Consignee and Export Reference Row -->
                <tr>
                    <td colspan="2" style="padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Consignee (if 'To Order' so indicate):</div>
                        <div class="field-value">{doc.get('hbl_consignee', '') or ''}</div>
                    </td>
                    <td colspan="2" style="padding: 5px; border-bottom: 1px solid #000; border-left: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Export Reference:</div>
                        <div class="field-value" style="font-size: 8px;">
                            INV No.: {doc.get('invoice_no', '') or ''}<br>
                            EXP No.: {doc.get('exp_no', '') or ''}<br>
                            S/C No.: {doc.get('sc_no', '') or ''}<br>
                            Date: {doc.get('hbl_date', '') or ''}
                        </div>
                    </td>
                </tr>

                <!-- Notify Party Row -->
                <tr>
                    <td colspan="4" style="padding: 5px; border-bottom: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Notify Party (No claim shall attach for failure to notify):</div>
                        <div class="field-value">{doc.get('notify_to', '') or ''}</div>
                    </td>
                </tr>

                <!-- Also Notify and For Delivery Row -->
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Also Notify:</div>
                        <div class="field-value"></div>
                    </td>
                    <td colspan="3" style="padding: 5px; border-bottom: 1px solid #000; border-left: 1px solid #000; vertical-align: top;">
                        <div class="section-title">For delivery please apply to:</div>
                        <div class="field-value"></div>
                    </td>
                </tr>

                <!-- Pre-carriage and Place of Receipt Row -->
                <tr>
                    <td style="width: 17.5%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Pre-carriage by</div>
                        <div class="field-value"></div>
                    </td>
                    <td style="width: 17.5%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Place of Receipt</div>
                        <div class="field-value"></div>
                    </td>
                    <td colspan="2" style="padding: 5px; border-bottom: 1px solid #000; border-left: 1px solid #000; vertical-align: top;">
                    </td>
                </tr>

                <!-- Vessel, Port of Loading, Port of Discharge, Place of Delivery Row -->
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Vessel / Voyage</div>
                        <div class="field-value">{doc.get('mv', '') or ''} / {doc.get('mv_voyage_no', '') or ''}</div>
                    </td>
                    <td style="padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Port of Loading</div>
                        <div class="field-value">{doc.get('port_of_loading', '') or ''}</div>
                    </td>
                    <td style="width: 32.5%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; border-left: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Port of Discharge</div>
                        <div class="field-value">{doc.get('port_of_discharge', '') or ''}</div>
                    </td>
                    <td style="width: 32.5%; padding: 5px; border-bottom: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Place of Delivery</div>
                        <div class="field-value">{doc.get('port_of_delivery', '') or ''}</div>
                    </td>
                </tr>

                <!-- Cargo Details Headers -->
                <tr>
                    <td style="width: 15%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; text-align: center; font-size: 8px; font-weight: normal;">
                        Shipping Marks
                    </td>
                    <td style="width: 15%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; text-align: center; font-size: 8px; font-weight: normal;">
                        No. of Packages<br>or Shipping Units
                    </td>
                    <td style="width: 40%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; border-left: 1px solid #000; text-align: center; font-size: 8px; font-weight: normal;">
                        Description of Packages or Goods
                    </td>
                    <td style="width: 15%; padding: 5px; border-bottom: 1px solid #000; border-right: 1px solid #000; text-align: center; font-size: 8px; font-weight: normal;">
                        Gross Weight
                    </td>
                    <td style="width: 15%; padding: 5px; border-bottom: 1px solid #000; text-align: center; font-size: 8px; font-weight: normal;">
                        Measurement<br>(Volume)
                    </td>
                </tr>

                <!-- Cargo Details Content -->
                <tr>
                    <td style="padding: 8px; border-right: 1px solid #000; border-bottom: 1px solid #000; vertical-align: top; min-height: 200px;">
                        <div style="font-size: 9px;">{doc.get('shipping_marks', '') or ''}</div>
                    </td>
                    <td style="padding: 8px; border-right: 1px solid #000; border-bottom: 1px solid #000; vertical-align: top; text-align: center;">
                        <div style="font-size: 9px;">{doc.get('no_of_pkg_hbl', '') or ''}</div>
                    </td>
                    <td style="padding: 8px; border-right: 1px solid #000; border-left: 1px solid #000; border-bottom: 1px solid #000; vertical-align: top;">
                        <div style="font-size: 9px;">{doc.get('description_of_good', '') or ''}</div>
                    </td>
                    <td style="padding: 8px; border-right: 1px solid #000; border-bottom: 1px solid #000; vertical-align: top; text-align: center;">
                        <div style="font-size: 10px; font-weight: bold;">{doc.get('gross_weight', '') or ''} KG</div>
                    </td>
                    <td style="padding: 8px; border-bottom: 1px solid #000; vertical-align: top; text-align: center;">
                        <div style="font-size: 10px; font-weight: bold;">{doc.get('hbl_vol_cbm', '') or ''} CBM</div>
                    </td>
                </tr>

                <!-- Blank Gap Row -->
                <tr>
                    <td colspan="5" style="padding: 100px 5px; border-top: none; border-left: none; border-right: none; border-bottom: none; position: relative;">
                        <!-- Empty gap space with watermark logo -->
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.1; text-align: center;">
                            <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" style="max-width: 200px; height: auto;" />
                        </div>
                    </td>
                </tr>

                <!-- Footer Section -->
                <tr>
                    <td colspan="2" style="padding: 5px; border-top: 1px solid #000; border-left: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Freight payable at:</div>
                        <div class="field-value"></div>
                    </td>
                    <td colspan="3" style="padding: 5px; border-top: 1px solid #000; border-right: 1px solid #000; vertical-align: top; text-align: center;">
                        <div style="font-size: 7px;">Excess Value Declaration: Refer to Clause 6 (4) (B)+(C) on reverse side</div>
                    </td>
                </tr>

                <!-- Terms and Conditions -->
                <tr>
                    <td colspan="5" style="padding: 8px; border-top: 1px solid #000; border-left: 1px solid #000; border-right: 1px solid #000; font-size: 7px; line-height: 1.4;">
                        <p style="margin: 0 0 5px 0;"><strong>RECEIVED</strong> by the Carrier the Goods as specified above in apparent good order and condition unless otherwise stated, to be transported to such place as agreed, authorized or permitted herein and subject to all the terms and conditions appearing on the front and reverse of this Bill of Lading to which the Merchant agrees by accepting this Bill of Lading, any local privileges and customs notwithstanding.</p>
                        <p style="margin: 0 0 5px 0;"><strong>THE PARTICULARS GIVEN ABOVE AS DECLARED BY THE SHIPPER</strong> and the weight, measure, quantity, condition, contents and value of the Goods are unknown to the Carrier.</p>
                        <p style="margin: 0;"><strong>IN WITNESS</strong> whereof one (1) original Bill of Lading has been signed if not otherwise stated above, the same being accomplished the other(s), if any, to be void. If required by the Carrier, one (1) original Bill of Lading must be surrendered duly endorsed in exchange for the Goods or delivery order.</p>
                    </td>
                </tr>

                <!-- Signature Section -->
                <tr>
                    <td style="width: 20%; padding: 5px; border-top: 1px solid #000; border-left: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Number of Original Bill of Lading:</div>
                        <div class="field-value"></div>
                    </td>
                    <td style="width: 20%; padding: 5px; border-top: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Place and date of issue</div>
                        <div class="field-value"></div>
                    </td>
                    <td colspan="3" style="width: 60%; padding: 5px; border-top: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Signed on behalf of By</div>
                        <div class="field-value"></div>
                    </td>
                </tr>

                <!-- Total Number of Carton -->
                <tr>
                    <td colspan="5" style="padding: 5px; border-top: 1px solid #000; border-left: 1px solid #000; border-right: 1px solid #000; vertical-align: top;">
                        <div class="section-title">Total Number of Carton:</div>
                        <div class="field-value"></div>
                    </td>
                </tr>

                <!-- Footer Text -->
                <tr>
                    <td colspan="5" style="padding: 8px; border-top: 1px solid #000; border-left: 1px solid #000; border-right: 1px solid #000; border-bottom: 1px solid #000; text-align: center;">
                        <div style="font-size: 14px; font-weight: bold; color: #7CB342;">(ORIGINAL)</div>
                    </td>
                </tr>
            </table>

        </div>
    </body>
    </html>
    """

    return html_template
