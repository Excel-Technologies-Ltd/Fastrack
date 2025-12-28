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

    # Footer text based on version
    footer_text = "(ORIGINAL)" if is_original else "(COPY - NOT NEGOTIABLE)"

    # Stamp/seal for original version - purple "FIRST ORIGINAL" stamp
    original_stamp = """
    <div style="position: absolute; right: 50px; top: 420px; border: 3px solid #6B46C1; color: #6B46C1; padding: 8px 15px; font-weight: bold; font-size: 14px; transform: rotate(0deg);">
        FIRST ORIGINAL
    </div>
    """ if is_original else ""

    # Build container detail table rows
    container_detail_rows = ""
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            container_detail_rows += f"""
            <tr>
                <td class="table-cell">{container.get('custom_container_no', '') or ''}</td>
                <td class="table-cell">{container.get('seal_no', '') or ''}</td>
                <td class="table-cell">{container.get('size', '') or ''}</td>
                <td class="table-cell">{container.get('no_of_pkg', '') or ''}</td>
                <td class="table-cell">{container.get('weight', '') or ''} KGS</td>
                <td class="table-cell">{doc.get('hbl_vol_cbm', '') or ''} CBM</td>
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
            .section-title {{ font-weight: bold; font-size: 8px; margin-bottom: 3px; }}
            .field-value {{
                font-size: 10px;
                border-bottom: 1px solid #333;
                min-height: 20px;
                padding-bottom: 2px;
            }}
            .field-value-no-line {{ font-size: 10px; }}
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

            <!-- Title and Header Section -->
            <table class="border">
                <tr>
                    <td style="width: 50%; padding: 8px; border-right: 1px solid #000; vertical-align: top;">
                        <div class="small-text text-center" style="margin-bottom: 8px;">(COMBINED TRANSPORT BILL OF LADING OR PORT TO PORT)</div>

                        <!-- Shipper and Bill of Lading No in same row -->
                        <table style="width: 100%; margin-bottom: 8px;">
                            <tr>
                                <td style="width: 60%; vertical-align: top; padding-right: 5px;">
                                    <div class="section-title">Shipper / Exporter:</div>
                                    <div class="field-value" style="min-height: 35px;">{doc.get('hbl_shipper', '') or ''}</div>
                                </td>
                                <td style="width: 40%; vertical-align: top;">
                                    <div class="section-title">Bill of Lading No.:</div>
                                    <div class="field-value text-bold">{doc.get('hbl_id', '') or ''}</div>
                                </td>
                            </tr>
                        </table>

                        <!-- Consignee and Export Reference in same row -->
                        <table style="width: 100%; margin-bottom: 8px;">
                            <tr>
                                <td style="width: 60%; vertical-align: top; padding-right: 5px;">
                                    <div class="section-title">Consignee (If 'to Order', so indicate):</div>
                                    <div class="field-value" style="min-height: 35px;">{doc.get('hbl_consignee', '') or ''}</div>
                                </td>
                                <td style="width: 40%; vertical-align: top;">
                                    <div class="section-title">Export Reference:</div>
                                    <div class="field-value" style="font-size: 8px;">
                                        INV No.: {doc.get('invoice_no', '') or ''}<br>
                                        EXP No.: {doc.get('exp_no', '') or ''}<br>
                                        S/C No.: {doc.get('sc_no', '') or ''}<br>
                                        Date: {doc.get('hbl_date', '') or ''}
                                    </div>
                                </td>
                            </tr>
                        </table>

                        <!-- Notify Party and Also Notify in same row -->
                        <table style="width: 100%; margin-bottom: 8px;">
                            <tr>
                                <td style="width: 60%; vertical-align: top; padding-right: 5px;">
                                    <div class="section-title">Notify Party (No claim shall attach for failure to notify):</div>
                                    <div class="field-value" style="min-height: 35px;">{doc.get('notify_to', '') or ''}</div>
                                </td>
                                <td style="width: 40%; vertical-align: top;">
                                    <div class="section-title">Also Notify:</div>
                                    <div class="field-value" style="min-height: 35px;"></div>
                                </td>
                            </tr>
                        </table>

                        <div style="margin-bottom: 5px;">
                            <div class="tiny-text">For delivery please apply to:</div>
                            <div class="field-value" style="min-height: 20px;"></div>
                        </div>
                    </td>
                    <td style="width: 50%; padding: 8px; vertical-align: top; position: relative;">
                        {original_stamp}
                        <div class="text-center" style="margin-bottom: 8px;">
                            <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" style="height: 45px;" />
                        </div>

                        <div class="text-center text-bold" style="font-size: 16px; margin: 8px 0;">BILL OF LADING</div>
                        <div class="text-center small-text" style="margin-bottom: 8px;">(NOT NEGOTIABLE UNLESS CONSIGNED TO ORDER)</div>

                        <div class="border" style="padding: 3px; margin-bottom: 5px; min-height: 50px;">
                            <div class="text-bold" style="font-size: 7px;">Fasttrack Cargo Solutions, Ltd.</div>
                            <div class="tiny-text" style="margin-top: 2px;">
                                Tel: +880-2-48336368<br>
                                Fax: +880-2-48336374<br>
                                Email: support@fasttrackbd.com.bd<br>
                                Customs License No.: 101-163-04841
                            </div>
                        </div>
                    </td>
                </tr>
            </table>

            <!-- Transport Details -->
            <table>
                <tr>
                    <!-- Pre-carriage by and Place of Receipt in left side (50%) -->
                    <td class="border" style="width: 50%; padding: 0; border-top: none;">
                        <table style="width: 100%;">
                            <tr>
                                <td style="width: 50%; padding: 5px; border-right: 1px solid #000;">
                                    <div class="section-title">Pre-carriage by</div>
                                    <div class="field-value" style="min-height: 20px;"></div>
                                </td>
                                <td style="width: 50%; padding: 5px;">
                                    <div class="section-title">Place of Receipt</div>
                                    <div class="field-value" style="min-height: 20px;"></div>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <!-- Right side empty (50%) -->
                    <td class="border" style="width: 50%; padding: 5px; border-top: none; border-left: none;">
                    </td>
                </tr>
                <tr>
                    <td class="border" style="width: 25%; padding: 5px; border-top: none;">
                        <div class="section-title">Vessel / Voyage</div>
                        <div class="field-value">{doc.get('mv', '') or ''} / {doc.get('mv_voyage_no', '') or ''}</div>
                    </td>
                    <td class="border" style="width: 25%; padding: 5px; border-top: none; border-left: none;">
                        <div class="section-title">Port of Loading</div>
                        <div class="field-value">{doc.get('port_of_loading', '') or ''}</div>
                    </td>
                    <td class="border" style="width: 25%; padding: 5px; border-top: none; border-left: none;">
                        <div class="section-title">Port of Discharge</div>
                        <div class="field-value">{doc.get('port_of_discharge', '') or ''}</div>
                    </td>
                    <td class="border" style="width: 25%; padding: 5px; border-top: none; border-left: none;">
                        <div class="section-title">Place of Delivery</div>
                        <div class="field-value">{doc.get('port_of_delivery', '') or ''}</div>
                    </td>
                </tr>
            </table>

            <!-- Main Cargo Table -->
            <table>
                <tr>
                    <th class="border" style="padding: 5px; font-size: 9px; border-top: none; width: 12%;">Shipping Marks</th>
                    <th class="border" style="padding: 5px; font-size: 9px; border-top: none; border-left: none; width: 12%;">No. of Packages<br>or Shipping Unit</th>
                    <th class="border" style="padding: 5px; font-size: 9px; border-top: none; border-left: none; width: 40%;">Description of Packages or Goods</th>
                    <th class="border" style="padding: 5px; font-size: 9px; border-top: none; border-left: none; width: 18%;">Gross Weight</th>
                    <th class="border" style="padding: 5px; font-size: 9px; border-top: none; border-left: none; width: 18%;">Measurement<br>(Volume)</th>
                </tr>
                <tr>
                    <td rowspan="4" class="border" style="padding: 6px; border-top: none; vertical-align: top;">
                        <div class="field-value-no-line" style="font-size: 10px;">{doc.get('no_of_pkg_hbl', '') or ''}</div>
                    </td>
                    <td rowspan="4" class="border" style="padding: 6px; border-top: none; border-left: none; vertical-align: top;">
                        <div class="text-bold" style="font-size: 9px;">SHIPPING MARKS</div>
                        <div class="text-bold" style="font-size: 9px; margin-top: 5px;">AS PER COMMERCIAL</div>
                        <div style="font-size: 9px;">INVOICE & PACKING LIST</div>
                    </td>
                    <td class="border" style="padding: 6px; border-top: none; border-left: none; vertical-align: top;">
                        <div class="text-bold" style="font-size: 9px; margin-bottom: 5px;">DESCRIPTION OF GOODS</div>
                        <div style="font-size: 10px;">{doc.get('description_of_good', '') or ''}</div>
                        <div style="margin-top: 8px; font-size: 9px;">HS CODE: {doc.get('hs_code', '') or ''}</div>
                    </td>
                    <td rowspan="4" class="border" style="padding: 6px; border-top: none; border-left: none; text-align: center; vertical-align: middle;">
                        <div class="text-bold" style="font-size: 11px;">{doc.get('gross_weight', '') or ''} KG</div>
                    </td>
                    <td rowspan="4" class="border" style="padding: 6px; border-top: none; border-left: none; text-align: center; vertical-align: middle;">
                        <div class="text-bold" style="font-size: 11px;">{doc.get('hbl_vol_cbm', '') or ''} CBM</div>
                    </td>
                </tr>
                <tr>
                    <td class="border" style="padding: 5px; border-top: none; border-left: none; font-size: 9px; min-height: 30px;">
                        <!-- Additional description space -->
                    </td>
                </tr>
                <tr>
                    <td class="border" style="padding: 0; border-top: none; border-left: none;">
                        <table style="width: 100%;">
                            <tr>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; width: 16.66%;">CONTAINER No.</th>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; border-left: 1px solid #000; width: 16.66%;">SEAL No.</th>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; border-left: 1px solid #000; width: 16.66%;">TYPE</th>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; border-left: 1px solid #000; width: 16.66%;">PKG</th>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; border-left: 1px solid #000; width: 16.66%;">GROSS WEIGHT</th>
                                <th class="border" style="padding: 2px; font-size: 6px; border: none; border-bottom: 1px solid #000; border-left: 1px solid #000; width: 16.66%;">VOLUME</th>
                            </tr>
                            {container_detail_rows}
                        </table>
                    </td>
                </tr>
                <tr>
                    <td class="border" style="padding: 5px; border-top: none; border-left: none; font-size: 9px;">
                        <div class="text-bold">FREIGHT COLLECT</div>
                        <div>Mode: CFS/CY</div>
                    </td>
                </tr>
            </table>

            <!-- Freight and Declaration Section -->
            <table>
                <tr>
                    <td class="border" style="width: 50%; padding: 6px; border-top: none; vertical-align: top;">
                        <div class="section-title">Freight payable at:</div>
                        <div class="field-value" style="min-height: 35px;">AS ARRANGED</div>
                    </td>
                    <td class="border" style="width: 50%; padding: 6px; border-top: none; border-left: none; vertical-align: top; text-align: center;">
                        <div style="font-size: 8px; margin-bottom: 3px;">Excess Value Declaration: Refer to Clause 6 (4) (B)+(C) on reverse side</div>
                        <div style="margin-top: 10px;">
                            <!-- Signature/stamp placeholder -->
                        </div>
                    </td>
                </tr>
            </table>

            <!-- Terms and Conditions -->
            <div style="margin: 8px 0; line-height: 1.4; font-size: 8px;">
                <p style="margin: 3px 0;"><strong>RECEIVED</strong> by the Carrier the Goods as specified above in apparent good order and condition unless otherwise stated, to be transported to such place as agreed, authorized or permitted herein and subject to all the terms and conditions appearing on the front and reverse of this Bill of Lading to which the Merchant agrees by accepting this Bill of Lading, any local privileges and customs notwithstanding.</p>

                <p style="margin: 3px 0;"><strong>THE PARTICULARS GIVEN ABOVE AS DECLARED BY THE SHIPPER</strong> and the weight, measure, quantity, condition, contents and value unknown.</p>

                <p style="margin: 3px 0;"><strong>IN WITNESS</strong> whereof one (1) original Bill of Lading has been signed if not otherwise stated above, the same being accomplished the other(s), if any, to be void. If required by the Carrier, one (1) original Bill of Lading must be surrendered duly endorsed in exchange for the Goods or delivery order.</p>
            </div>

            <!-- Bottom Signature Section -->
            <table>
                <tr>
                    <td class="border" style="width: 33%; padding: 5px; border-top: none;">
                        <div class="section-title">Number of Original Bill of Lading:</div>
                        <div class="field-value">THREE (3)</div>
                    </td>
                    <td class="border" style="width: 33%; padding: 5px; border-top: none; border-left: none;">
                        <div class="section-title">Place and date of issue</div>
                        <div class="field-value">SHIPPED ON BOARD: {doc.get('hbl_date', '') or ''}</div>
                    </td>
                    <td class="border" style="width: 34%; padding: 5px; border-top: none; border-left: none; position: relative; min-height: 50px;">
                        <div class="section-title">Signed on behalf of By</div>
                        <div class="field-value" style="margin-top: 20px; border-bottom: none;">
                            <!-- Signature/stamp area -->
                        </div>
                    </td>
                </tr>
                <tr>
                    <td class="border" style="padding: 5px; border-top: none;">
                        <div class="section-title">Total Number of Carton:</div>
                        <div class="field-value">{doc.get('no_of_pkg_hbl', '') or ''} CTN</div>
                    </td>
                    <td colspan="2" class="border" style="padding: 5px; border-top: none; border-left: none;">
                    </td>
                </tr>
            </table>

            <!-- Footer Text -->
            <div class="text-center text-bold" style="margin-top: 5px; color: #90EE90; font-size: 14px;">
                {footer_text}
            </div>
        </div>
    </body>
    </html>
    """

    return html_template
