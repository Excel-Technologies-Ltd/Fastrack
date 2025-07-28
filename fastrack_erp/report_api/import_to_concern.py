import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url


@frappe.whitelist()
def download_to_whom_it_may_concern_pdf(doc_name="SHBL-00000064"):
    """Download TO WHOM IT MAY CONCERN report as PDF using HTML template"""
    
    try:
        # Get the document
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Generate HTML content
        html_content = get_to_whom_it_may_concern_html(doc)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set filename
        filename = f"To_Whom_It_May_Concern_{doc_name}.pdf"
        
        # Prepare response
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.throw(f"Error generating PDF: {str(e)}")


def get_to_whom_it_may_concern_html(doc):
    """Generate HTML content for TO WHOM IT MAY CONCERN report"""
    
    # Get container information for the table
    container_rows = ""
    total_weight = 0
    if hasattr(doc, 'container_info') and doc.container_info:
        for container in doc.container_info:
            weight = container.get('weight', 0) or 0
            if weight:
                total_weight += float(weight)
            
            container_rows += f"""
            <tr>
                <td style="border: 1px solid black; padding: 4px; text-align: center;">{container.get('custom_container_no', '') or ''}</td>
                <td style="border: 1px solid black; padding: 4px; text-align: center;">{container.get('seal_no', '') or ''}</td>
                <td style="border: 1px solid black; padding: 4px; text-align: center;">{container.get('size', '') or ''}</td>
                <td style="border: 1px solid black; padding: 4px; text-align: center;">{doc.get('nature', '') or 'FCL'}</td>
                <td style="border: 1px solid black; padding: 4px; text-align: center;">{weight}</td>
            </tr>
            """
    else:
        # Default empty row if no container data
        container_rows = """
        <tr>
            <td style="border: 1px solid black; padding: 4px; text-align: center;">-</td>
            <td style="border: 1px solid black; padding: 4px; text-align: center;">-</td>
            <td style="border: 1px solid black; padding: 4px; text-align: center;">-</td>
            <td style="border: 1px solid black; padding: 4px; text-align: center;">FCL</td>
            <td style="border: 1px solid black; padding: 4px; text-align: center;">0</td>
        </tr>
        """
    
    # Calculate ocean freight details
    ocean_freight_rate = doc.get('ocean_freight_rate', '1275/CNTR') or '1275/CNTR'
    total_containers = len(doc.container_info) if hasattr(doc, 'container_info') and doc.container_info else 0
    container_size = doc.container_info[0].get('size', '20" GP') if hasattr(doc, 'container_info') and doc.container_info else '20" GP'
    total_container_desc = f"{total_containers}x{container_size} CNTR" if total_containers > 0 else "0x20 GP CNTR"
    
    ex_rate = doc.get('exchange_rate', 123.00) or 123.00
    ocean_freight_usd = doc.get('ocean_freight_usd', 5100.00) or 5100.00
    ocean_freight_bdt = ocean_freight_usd * ex_rate
    taka_amount = doc.get('taka_amount', 627300.00) or 627300.00
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TO WHOM IT MAY CONCERN</title>
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
                display: table;
                width: 100%;
                margin-bottom: 20px;
            }}
            .header-left {{
                display: table-cell;
                width: 70%;
                vertical-align: top;
            }}
            .header-right {{
                display: table-cell;
                width: 30%;
                text-align: right;
                vertical-align: top;
            }}
            .title-box {{
                border: 2px solid black;
                text-align: center;
                padding: 8px;
                margin: 20px auto;
                width: 300px;
                font-weight: bold;
                font-size: 14px;
            }}
            .details-section {{
                margin-bottom: 20px;
            }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            .details-table td {{
                padding: 3px 5px;
                vertical-align: top;
            }}
            .details-table .label {{
                width: 150px;
                font-weight: bold;
            }}
            .details-table .colon {{
                width: 10px;
            }}
            .container-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            .container-table th,
            .container-table td {{
                border: 1px solid black;
                padding: 4px;
                text-align: center;
            }}
            .container-table th {{
                background-color: #f5f5f5;
                font-weight: bold;
            }}
            .freight-section {{
                margin: 20px 0;
            }}
            .freight-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .freight-table td {{
                padding: 3px 0;
                vertical-align: top;
            }}
            .freight-table .label {{
                width: 200px;
                font-weight: bold;
            }}
            .freight-table .colon {{
                width: 10px;
            }}
            .signature-section {{
                margin-top: 40px;
                position: relative;
            }}
            .signature-left {{
                float: left;
                width: 50%;
            }}
            .signature-right {{
                float: right;
                width: 50%;
                text-align: right;
            }}
            .status-highlight {{
                color: red;
                font-weight: bold;
            }}
            .notify-party {{
                color: red;
                font-size: 10px;
            }}
            .eta-highlight {{
                color: red;
                font-weight: bold;
            }}
            .fc-total {{
                color: red;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <div class="header-left">
                    <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fastrack Logo" style="height: 55px;" />
                </div>
                <div class="header-right">
                    <!-- Logo space if needed -->
                </div>
            </div>

            <!-- Title -->
            <div class="title-box">
                TO WHOM IT MAY CONCERN
            </div>

            <!-- Customer and Date Info -->
            <div class="header">
                <div class="header-left">
                    <p style="margin: 0;"><strong>TO:</strong> <span class="notify-party">Notify party</span></p>
                    <p style="margin: 0; font-weight: bold;">{doc.get('notify_to', 'MINISTER HI-TECH PARK ELECTRONICS LTD.') or 'MINISTER HI-TECH PARK ELECTRONICS LTD.'}</p>
                    <p style="margin: 0;">{doc.get('notify_address', '337, NARAYANPUR, P.O.-KASHIGANJ, THANA-TRISHAL, MYMENSINGH') or '337, NARAYANPUR, P.O.-KASHIGANJ, THANA-TRISHAL, MYMENSINGH'}</p>
                </div>
                <div class="header-right">
                    <p style="margin: 0;"><strong>Date:</strong> {doc.get('hbl_date', '26-Jun-2025') or '26-Jun-2025'} <span class="eta-highlight">ETA</span></p>
                </div>
            </div>

            <!-- Shipping Details -->
            <div class="details-section">
                <p style="font-weight: bold; margin: 15px 0 10px 0;">Shipping Details:</p>
                
                <table class="details-table">
                    <tr>
                        <td class="label">Shipper</td>
                        <td class="colon">:</td>
                        <td>{doc.get('hbl_shipper', 'NANJING HUIKANG INDUSTRIAL CO., LIMITED') or 'NANJING HUIKANG INDUSTRIAL CO., LIMITED'}</td>
                        <td class="label" style="padding-left: 30px;">M/Vsl. Name</td>
                        <td class="colon">:</td>
                        <td>{doc.get('mv', 'SAN PEDRO') or 'SAN PEDRO'}</td>
                    </tr>
                    <tr>
                        <td class="label">HBL No</td>
                        <td class="colon">:</td>
                        <td>{doc.get('hbl_id', 'DKD250-220') or 'DKD250-220'}</td>
                        <td class="label" style="padding-left: 30px;">Voyage</td>
                        <td class="colon">:</td>
                        <td>{doc.get('mv_voyage_no', '25005W') or '25005W'}</td>
                    </tr>
                    <tr>
                        <td class="label">HBL Date</td>
                        <td class="colon">:</td>
                        <td>{doc.get('hbl_date', '21-Jun-2025') or '21-Jun-2025'}</td>
                        <td class="label" style="padding-left: 30px;">ETD</td>
                        <td class="colon">:</td>
                        <td>{doc.get('hbl_etd', '12-Jun-2025') or '12-Jun-2025'}</td>
                    </tr>
                    <tr>
                        <td class="label">MBL No</td>
                        <td class="colon">:</td>
                        <td>{doc.get('mbl_no', 'A56FX15520') or 'A56FX15520'}</td>
                        <td class="label" style="padding-left: 30px;">F/Vsl. Name</td>
                        <td class="colon">:</td>
                        <td>{doc.get('fv', 'SAN PEDRO') or 'SAN PEDRO'}</td>
                    </tr>
                    <tr>
                        <td class="label">MBL Date</td>
                        <td class="colon">:</td>
                        <td>{doc.get('mbl_date', '12-Jun-2025') or '12-Jun-2025'}</td>
                        <td class="label" style="padding-left: 30px;">ETA</td>
                        <td class="colon">:</td>
                        <td>{doc.get('eta', '26-Jun-2025') or '26-Jun-2025'}</td>
                    </tr>
                    <tr>
                        <td class="label">Consignee</td>
                        <td class="colon">:</td>
                        <td>{doc.get('consignee', 'AL-ARAFAH ISLAMI BANK LTD') or 'AL-ARAFAH ISLAMI BANK LTD'}</td>
                        <td class="label" style="padding-left: 30px;">Inco Terms</td>
                        <td class="colon">:</td>
                        <td>{doc.get('inco_term', 'Prepaid') or 'Prepaid'}</td>
                    </tr>
                    <tr>
                        <td class="label">L/C No.& Date</td>
                        <td class="colon">:</td>
                        <td>{doc.get('lc_date', '10742501036G / 12-Aug-2025') or '10742501036G / 12-Aug-2025'}</td>
                        <td style="padding-left: 30px;"></td>
                        <td></td>
                        <td></td>
                    </tr>
                </table>

                <table class="details-table">
                    <tr>
                        <td class="label">Port of Loading</td>
                        <td class="colon">:</td>
                        <td>{doc.get('port_of_loading', 'SHANGHAI') or 'SHANGHAI'}</td>
                        <td class="label" style="padding-left: 30px;">Volume CBM</td>
                        <td class="colon">:</td>
                        <td>{doc.get('hbl_vol_cbm', '41.46') or '41.46'}</td>
                    </tr>
                    <tr>
                        <td class="label">Port of Discharge</td>
                        <td class="colon">:</td>
                        <td>{doc.get('port_of_discharge', 'CHATTOGRAM') or 'CHATTOGRAM'}</td>
                        <td class="label" style="padding-left: 30px;">Total (CTN/PKG)</td>
                        <td class="colon">:</td>
                        <td>{doc.get('no_of_pkg_hbl', '66,447.76') or '66,447.76'}</td>
                    </tr>
                    <tr>
                        <td class="label">Port of Delivery</td>
                        <td class="colon">:</td>
                        <td>{doc.get('port_of_delivery', 'CHATTOGRAM') or 'CHATTOGRAM'}</td>
                        <td style="padding-left: 30px;"></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td class="label">Shipping Line</td>
                        <td class="colon">:</td>
                        <td>{doc.get('shipping_line', 'BS CARGO AGENCY LTD.') or 'BS CARGO AGENCY LTD.'}</td>
                        <td class="label" style="padding-left: 30px; color: red;">Status</td>
                        <td class="colon" style="color: red;">:</td>
                        <td style="color: red;"></td>
                    </tr>
                </table>
            </div>

            <!-- Container Table -->
            <table class="container-table">
                <thead>
                    <tr>
                        <th>Container No.</th>
                        <th>Seal No.</th>
                        <th>Size</th>
                        <th>Mode</th>
                        <th>Weight</th>
                    </tr>
                </thead>
                <tbody>
                    {container_rows}
                </tbody>
            </table>

            <p style="margin: 5px 0;"><strong>Total Weight:</strong> {total_weight:,.2f}</p>
            <p style="color: red; margin: 5px 0;">Container table</p>

            <!-- Ocean Freight Details -->
            <div class="freight-section">
                <p style="margin-bottom: 10px;">This is to certify that the Ocean Freight of the above mentioned shipment is as under:</p>
                
                <table class="freight-table">
                    <tr>
                        <td class="label">Ocean Freight (US$)</td>
                        <td class="colon">:</td>
                        <td>{ocean_freight_rate} <span class="fc-total">FC total</span></td>
                    </tr>
                    <tr>
                        <td class="label">Total Container</td>
                        <td class="colon">:</td>
                        <td>{total_container_desc}</td>
                    </tr>
                    <tr>
                        <td class="label">Ex. Rate</td>
                        <td class="colon">:</td>
                        <td>{ex_rate}</td>
                    </tr>
                    <tr>
                        <td class="label">So, Total Ocean Freight is</td>
                        <td class="colon">:</td>
                        <td>US$ {ocean_freight_usd:,.2f} And BDT. Taka is {taka_amount:,.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Goods Description</td>
                        <td class="colon">:</td>
                        <td>{doc.get('description_of_good', 'TEMPERED GLASS FOR REFRIGERATOR') or 'TEMPERED GLASS FOR REFRIGERATOR'}</td>
                    </tr>
                </table>
            </div>

            <!-- Signature Section -->
            <div class="signature-section">
                <div class="signature-left">
                    <p>Thanks and Best Regards,</p>
                    <p>Sincerely Yours,</p>
                    <p style="margin-top: 20px;">For, Fastrack Cargo Solutions Ltd.</p>
                </div>
                <div class="signature-right">
                    <div style="margin-top: 40px;">
                        <img src="https://via.placeholder.com/80x80/0066cc/ffffff?text=SEAL" alt="Company Seal" style="width: 80px; height: 80px;" />
                    </div>
                </div>
                <div style="clear: both;"></div>
                <p style="text-align: center; margin-top: 20px;">As Agent</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


@frappe.whitelist()
def get_to_whom_it_may_concern_preview(doc_name):
    """Get HTML preview of TO WHOM IT MAY CONCERN report (for testing)"""
    
    try:
        doctype = "Import Sea House Bill"
        doc = frappe.get_doc(doctype, doc_name)
        
        # Generate and return HTML content
        html_content = get_to_whom_it_may_concern_html(doc)
        return {"html": html_content}
        
    except Exception as e:
        frappe.throw(f"Error generating preview: {str(e)}")