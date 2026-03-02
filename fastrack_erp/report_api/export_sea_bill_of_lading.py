import frappe
from frappe.utils.pdf import get_pdf


def get_customer_address(customer_name):
    """Return a <br>-separated address + contact info string for a Customer, or '' if not found."""
    if not customer_name:
        return ''
    lines = []
    try:
        # --- Address ---
        addr_rows = frappe.db.sql("""
            SELECT addr.address_line1, addr.address_line2, addr.city, addr.state, addr.country
            FROM `tabAddress` addr
            INNER JOIN `tabDynamic Link` dl ON dl.parent = addr.name
            WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s
            ORDER BY addr.is_primary_address DESC
            LIMIT 1
        """, (customer_name,), as_dict=True)
        if addr_rows:
            addr = addr_rows[0]
            for p in [addr.address_line1, addr.address_line2, addr.city, addr.state, addr.country]:
                if p:
                    if p.strip() == '#':
                        break  # discard # and everything after
                    lines.append(p)

        # --- Contact (mobile & email) ---
        contact_rows = frappe.db.sql("""
            SELECT c.mobile_no, c.phone, c.email_id
            FROM `tabContact` c
            INNER JOIN `tabDynamic Link` dl ON dl.parent = c.name
            WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s
            ORDER BY c.is_primary_contact DESC
            LIMIT 1
        """, (customer_name,), as_dict=True)
        if contact_rows:
            contact = contact_rows[0]
            mobile = contact.mobile_no or contact.phone or ''
            email = contact.email_id or ''
            if mobile:
                lines.append(f'Mobile: {mobile}')
            if email:
                lines.append(f'Email: {email}')
    except Exception:
        pass
    return '<br>'.join(lines)


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

    # Footer title based on version
    footer_title = "ORIGINAL" if is_original else "DRAFT"

    # Get dynamic values with defaults
    hbl_shipper = doc.get('hbl_shipper', '') or ''
    hbl_shipper_address = get_customer_address(hbl_shipper)
    hbl_id = doc.get('hbl_id', '') or ''
    hbl_consignee = doc.get('hbl_consignee', '') or ''
    hbl_consignee_address = get_customer_address(hbl_consignee)
    notify_to = doc.get('notify_to', '') or ''
    notify_to_address = get_customer_address(notify_to)
    also_notify = doc.get('also_notify_party', '') or ''
    also_notify_address = get_customer_address(also_notify)
    delivery_apply_to = doc.get('delivery_agent', '') or ''
    delivery_apply_to_address = get_customer_address(delivery_apply_to)

    # Export references
    invoice_no = doc.get('inv_no', '') or ''
    invoice_date = doc.get('date_1', '') or ''  # INV Date
    exp_no = doc.get('exp_no', '') or ''
    exp_date = doc.get('date_2', '') or ''  # Exp Date
    sc_no = doc.get('sc_no', '') or ''
    sc_date = doc.get('date_3', '') or ''  # SC Date
    lc_no = doc.get('lc_no', '') or ''
    lc_date = doc.get('date_4', '') or ''  # LC Date

    # Vessel and routing
    fv = doc.get('fv', '') or ''
    fv_voyage_no = doc.get('fv__v_no', '') or ''
    pre_carriage_by = f"{fv} V. {fv_voyage_no}" if fv and fv_voyage_no else fv or fv_voyage_no
    mv = doc.get('mv', '') or ''
    mv_voyage_no = doc.get('mv_voyage_no', '') or ''
    vessel_voyage = f"{mv} V. {mv_voyage_no}" if mv and mv_voyage_no else mv or mv_voyage_no
    place_of_receipt = doc.get('port_of_receipt', '') or doc.get('port_of_loading', '') or ''
    port_of_loading = doc.get('port_of_loading', '') or ''
    port_of_discharge = doc.get('port_of_discharge', '') or ''
    port_of_delivery = doc.get('port_of_delivery', '') or ''

    # Cargo details
    shipping_marks = doc.get('shipping_marks', '') or ''
    inco_term = doc.get('inco_term', '') or ''
    mode = doc.get('mode', '') or ''
    _no_of_pkg_hbl_raw = doc.get('no_of_pkg_hbl') or 0
    no_of_pkg_hbl = int(_no_of_pkg_hbl_raw) if _no_of_pkg_hbl_raw == int(_no_of_pkg_hbl_raw) else _no_of_pkg_hbl_raw
    description_of_good = doc.get('description_of_good', '') or ''
    gross_weight = doc.get('gross_weight', '') or ''
    hbl_vol_cbm = doc.get('hbl_vol_cbm', '') or ''

    # Build container table HTML (done in Python to avoid nested f-string issues)
    container_info = doc.get('container_info', []) or []
    container_table_html = ''
    if container_info:
        def _fmt(v):
            """Strip trailing .0 from whole-number floats; return '' for empty."""
            if v is None or v == '':
                return ''
            try:
                f = float(v)
                return int(f) if f == int(f) else f
            except (TypeError, ValueError):
                return v

        cell_style = 'border: 1px solid transparent; padding: 2px 4px; text-align: center; vertical-align: middle; word-break: break-word; overflow: hidden;'
        rows_html = ''
        for c in container_info:
            rows_html += (
                f'<tr style="font-size: 8px;">'
                f'<td style="{cell_style}">{c.get("custom_container_no", "") or ""}</td>'
                f'<td style="{cell_style}">{c.get("seal_no", "") or ""}</td>'
                f'<td style="{cell_style}">{c.get("size", "") or ""}</td>'
                f'<td style="{cell_style}">{_fmt(c.get("no_of_pkg"))}</td>'
                f'<td style="{cell_style}">{c.get("weight", "") or ""} KGS</td>'
                f'<td style="{cell_style}">{c.get("cbm", "") or ""} CBM</td>'
                f'</tr>'
                f'<tr style="font-size: 8px; height:10px">'
                f'</tr>'
                f'<tr style="font-size: 8px; height:10px">'
                f'</tr>'
            )
        hdr_style = 'border: 1px solid transparent; padding: 2px 4px; text-align: center; vertical-align: middle; white-space: nowrap;'
        container_table_html = (
            '<table style="width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 8px; table-layout: fixed;">'
            '<colgroup>'
            '<col style="width: 23%;" />'
            '<col style="width: 20%;" />'
            '<col style="width: 9%;" />'
            '<col style="width: 12%;" />'
            '<col style="width: 20%;" />'
            '<col style="width: 16%;" />'
            '</colgroup>'
            '<tr style="font-size: 8px; font-weight: bold;">'
            f'<td style="{hdr_style}">Container No.</td>'
            f'<td style="{hdr_style}">|| Seal No.</td>'
            f'<td style="{hdr_style}">|| Type </td>'
            f'<td style="{hdr_style}">|| PKG</td>'
            f'<td style="{hdr_style}">|| Gross Wt.</td>'
            f'<td style="{hdr_style}">|| Volume</td>'
            '</tr>'
            + rows_html +
            '</table>'
        )

    # Pre-compute conditional HTML snippets for goods table
    inco_term_html = f'<div><strong>Inco Term</strong></div><div>{inco_term}</div>' if inco_term else ''
    mode_html = f"<div style='margin-top:4px;'><strong>Mode</strong></div><div>{mode}</div>" if mode else ''

    # Build goods table data rows.
    # When container_info exists, the container table spans both
    # "No. of Packages" and "Description" columns via colspan=2 in a second row.
    # Outer columns (Shipping Marks, Gross Weight, Volume) use rowspan=2.
    if container_info:
        goods_data_rows_html = (
            '<tr style="height: 160px;" >'
            f'<td rowspan="2" style="border: 1px solid transparent;  padding: 8px; vertical-align: top;">'
            f'<div style="display: flex; flex-direction: column;">'
            f'<div class="_text_center" style="flex: 1;"><strong>{shipping_marks}</strong></div>'
            f'<div style="margin-top: 8px; font-size: 9px;">{inco_term_html}{mode_html}</div>'
            f'</div></td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong style="font-size: 10px;">{no_of_pkg_hbl}</strong></td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">'
            f'{description_of_good}</td>'
            f'<td rowspan="2" style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong>{gross_weight} KG</strong></td>'
            f'<td rowspan="2" style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong>{hbl_vol_cbm} CBM</strong></td>'
            '</tr>'
            '<tr>'
            f'<td colspan="2" style="border: 1px solid transparent; padding: 4px 8px; vertical-align: top;">'
            f'{container_table_html}'
            '</td></tr>'
        )
    else:
        goods_data_rows_html = (
            '<tr>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">'
            f'<div style="display: flex; flex-direction: column; min-height: 250px;">'
            f'<div class="_text_center" style="flex: 1;"><strong>{shipping_marks}</strong></div>'
            f'<div style="margin-top: 8px; font-size: 9px;">{inco_term_html}{mode_html}</div>'
            f'</div></td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong style="font-size: 10px;">{no_of_pkg_hbl}</strong></td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">'
            f'{description_of_good}</td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong>{gross_weight} KG</strong></td>'
            f'<td style="border: 1px solid transparent; padding: 8px; vertical-align: top; text-align: center;">'
            f'<strong>{hbl_vol_cbm} CBM</strong></td>'
            '</tr>'
        )

    # Footer section
    freight_payable_at = doc.get('freight_payable_at', '') or 'AS Arranged'
    no_of_original_bl = str(doc.get('no_of_original_bl', '') or '3 (Three)').upper()
    total_no_of_cartons = doc.get('total_no_of_cartons', '') or no_of_pkg_hbl
    hbl_date = doc.get('hbl_date', '') or ''
    place_of_issue = doc.get('place_of_issue', '') or 'Bangladesh'
    place_and_date = f"Place and Date of Issue: {hbl_date}, {place_of_issue}" if hbl_date else f"Place and Date of Issue: {place_of_issue}"

    html_template = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Bill of Lading</title>
        <style>
          @page {{
            size: A4;
            margin: 5mm;
          }}
          body {{
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10px;
            -webkit-print-color-adjust: exact;
          }}
          * {{
            box-sizing: border-box;
          }}
          .page {{
            width: 100%;
            max-width: 200mm;
            background: white;
            margin: 0 auto;
            padding: 2mm 5mm;
            box-sizing: border-box;
            position: relative;
          }}
          @media print {{
            body {{
              background: none;
            }}
            .page {{
              margin: 0;
              padding: 0;
              border: none;
              box-shadow: none;
              max-width: 100%;
            }}
          }}
          p {{
            margin: 0;
            padding: 0;
          }}
          table {{
            border-collapse: collapse;
            table-layout: fixed;
            width: 100%;
            word-wrap: break-word;
            overflow-wrap: break-word;
          }}
          td, th {{
            word-wrap: break-word;
            overflow-wrap: break-word;
          }}
          .bold {{
            font-weight: bold;
          }}
          ._text_center {{
            text-align: center;
          }}
          ._header_title {{
            color: #7bbf24;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 5px;
          }}
          ._footer_title {{
            color: #7bbf24;
            font-size: 17px;
            font-weight: bold;
            text-align: center;
            margin-top: 5px;
          }}
          ._sub_header {{
            font-size: 10px;
            margin-bottom: 1px;
          }}
          ._container_label_text {{
            font-size: 9px;
            margin-bottom: 2px;
            display: block;
            color: #000000;
          }}
          ._container_content_text {{
            font-size: 9px;
            line-height: 1.3;
          }}
          ._text_normal {{
            font-size: 9px;
            line-height: 1.2;
          }}
          ._height_value_5 {{
            padding-top: 5px;
            padding-bottom: 5px;
            font-weight: bold;
          }}
        </style>
      </head>
      <body>
        <div class="page">
          <div class="_header_title">BILL OF LADING</div>

          <table style="width: 100%; margin-bottom: 1px; table-layout: fixed;">
            <tr>
              <td style="font-size: 10px; width: 50%;">(COMBINED TRANSPORT BILL OF LADING OR PORT TO PORT)</td>
              <td style="font-size: 10px; text-align: right; width: 50%;">(NOT NEGOTIABLE UNLESS CONSIGNED TO ORDER)</td>
            </tr>
          </table>

          <!-- Main Content Table -->
          <table style="width: 100%; border: 1px solid black; border-left: none; border-right: none; border-collapse: collapse; table-layout: fixed;">
            <!-- ROW 1: Shipper & Carrier Info -->
            <tr>
              <td style="width: 47%; border: 1px solid black; border-top: none; border-left: none; padding: 3px; vertical-align: top;">
                <span class="_container_label_text">Shipper / Exporter:</span>
                <div class="_container_content_text" style="padding-left: 5px;">
                  <strong>{hbl_shipper}</strong>
                  {"<br>" + hbl_shipper_address if hbl_shipper_address else ""}
                </div>
              </td>
              <td style="width: 53%; border-bottom: 1px solid black; padding: 0; vertical-align: top;">
                <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr>
                    <td style="width: 45%; text-align: center; vertical-align: middle; padding: 5px;">
                      <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" style="max-width: 100%; height: auto; max-height: 100px;" />
                    </td>
                    <td style="width: 55%; border-left: 1px solid black; vertical-align: top;">
                      <div style="border-bottom: 1px solid black; padding: 3px;">
                        <span class="_container_label_text">Bill of Lading No.:</span>
                        <div class="_container_content_text bold _text_center" style="margin-top: 3px; padding: 2px 0;">
                          {hbl_id}
                        </div>
                      </div>
                      <div style="padding: 3px; overflow: hidden;">
                        <span style="font-size: 11px; font-weight: bold; color: #7bbf24;">Fasttrack Cargo Solutions Ltd.</span>
                        <table style="margin-top: 2px; table-layout: auto; width: 100%;">
                          <tr>
                            <td class="_text_normal" style="white-space: nowrap;">Tel</td>
                            <td class="_text_normal" style="width: 8px;">:</td>
                            <td class="_text_normal">+880-2-8836368</td>
                          </tr>
                          <tr>
                            <td class="_text_normal" style="white-space: nowrap;">Fax</td>
                            <td class="_text_normal">:</td>
                            <td class="_text_normal">+880-2-8836374</td>
                          </tr>
                          <tr>
                            <td class="_text_normal" style="white-space: nowrap;">Email</td>
                            <td class="_text_normal">:</td>
                            <td class="_text_normal" style="word-break: break-all;">sales@fastrackcargo.com.bd</td>
                          </tr>
                        </table>
                        <table style="margin-top: 2px; table-layout: auto; width: 100%;">
                          <tr>
                            <td class="_text_normal" style="white-space: nowrap;">Customs License No</td>
                            <td class="_text_normal" style="width: 8px;">:</td>
                            <td class="_text_normal">101-16-3-0841</td>
                          </tr>
                        </table>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- ROW 2: Consignee & Export References -->
            <tr>
              <td style="border: 1px solid black; border-top: none; border-left: none; padding: 3px; vertical-align: top;">
                <span class="_container_label_text">Consignee (if 'To Order' so indicate):</span>
                <div class="_container_content_text" style="padding-left: 5px;">
                  <strong>{hbl_consignee}</strong>
                  {"<br>" + hbl_consignee_address if hbl_consignee_address else ""}
                </div>
              </td>
              <td style="border-bottom: 1px solid black; padding: 3px; vertical-align: top; overflow: hidden;">
                <span class="_container_label_text">Export References:</span>
                <div style="margin-top: 5px;">
                  <strong>
                    <table style="width: 100%; table-layout: fixed;">
                      <tr>
                        <td class="_text_normal" style="width: 60%;">INV No.: {invoice_no}</td>
                        <td class="_text_normal" style="text-align: right; width: 40%;">Date: {invoice_date}</td>
                      </tr>
                      <tr>
                        <td class="_text_normal">EXP No.: {exp_no}</td>
                        <td class="_text_normal" style="text-align: right;">Date: {exp_date}</td>
                      </tr>
                      <tr>
                        <td class="_text_normal">S/C No.: {sc_no}</td>
                        <td class="_text_normal" style="text-align: right;">Date: {sc_date}</td>
                      </tr>
                      <tr>
                        <td class="_text_normal">LC No.: {lc_no}</td>
                        <td class="_text_normal" style="text-align: right;">Date: {lc_date}</td>
                      </tr>
                    </table>
                  </strong>
                </div>
              </td>
            </tr>

            <!-- ROW 3: Notify Party, Also Notify, For Delivery -->
            <tr style="">
              <td style="height: 100%; border: 1px solid black; border-top: none; border-left: none; padding: 0; vertical-align: top;">
                <table style="height: 100%;  width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr style="height: 80px;">
                    <td colspan="2" style="height: 60px; vertical-align: top; ">
                      <span class="_container_label_text">Notify Party (No claim shall attach for failure to notify):</span>
                      <div class="_container_content_text" style="padding-left: 5px; word-wrap: break-word;">
                        <strong>{notify_to}</strong>
                        {"<br>" + notify_to_address if notify_to_address else ""}
                      </div>
                    </td>
                  </tr>
                  <tr style="height: 70px;">
                    <td style="width: 50%;  border-right: 1px solid black; border-top: 1px solid black; padding: 3px; text-align: center; vertical-align: top;">
                      <strong>Pre-carriage by</strong>
                      <div class="_height_value_5" style="word-wrap: break-word;">{pre_carriage_by}</div>
                    </td>
                    <td style="width: 50%; border-top: 1px solid black; border-left: 1px solid black; padding: 3px; text-align: center; vertical-align: top;">
                      <strong>Place of Receipt</strong>
                      <div class="_height_value_5" style="word-wrap: break-word;">{place_of_receipt}</div>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="border-bottom: 1px solid black; padding: 0; vertical-align: top; overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr style="height: 70px;">
                    <td style="border-bottom: 1px solid black; padding: 3px; vertical-align: top;">
                      <span class="_container_label_text">Also Notify:</span>
                      <div class="_container_content_text" style="padding-left: 5px; word-wrap: break-word;">
                        <strong>{also_notify}</strong>
                        {"<br>" + also_notify_address if also_notify_address else ""}
                      </div>
                    </td>
                  </tr>
                  <tr style="height: 80px;">
                    <td style="padding: 3px; vertical-align: top;">
                      <span class="_container_label_text">For delivery please apply to:</span>
                      <div class="_container_content_text" style="padding-left: 5px; word-wrap: break-word;">
                        <strong>{delivery_apply_to}</strong>
                        {"<br>" + delivery_apply_to_address if delivery_apply_to_address else ""}
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- ROW 4: Vessel, Port of Loading, Port of Discharge, Place of Delivery -->
            <tr>
              <td style="border-bottom: 1px solid black; border-top: none; border-left: none; padding: 0; vertical-align: top;">
                <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr>
                    <td style="width: 50%; padding: 3px; vertical-align: top;">
                      <span class="_container_label_text">Vessel / Voyage:</span>
                      <div class="_height_value_5 _text_center" style="word-wrap: break-word;">{vessel_voyage}</div>
                    </td>
                    <td style="width: 50%; border-left: 1px solid black; padding: 3px; text-align: center; vertical-align: top;">
                      <strong>Port of Loading</strong>
                      <div class="_height_value_5" style="word-wrap: break-word;">{port_of_loading}</div>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="padding: 0; vertical-align: top; overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr>
                    <td style="width: 50%; padding: 3px; text-align: center; vertical-align: top;">
                      <strong>Port of Discharge</strong>
                      <div class="_height_value_5" style="word-wrap: break-word;">{port_of_discharge}</div>
                    </td>
                    <td style="width: 50%; border-left: 1px solid black; padding: 3px; text-align: center; vertical-align: top;">
                      <strong>Place of Delivery</strong>
                      <div class="_height_value_5" style="word-wrap: break-word;">{port_of_delivery}</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <!-- Goods Table -->
          <table style="border-left: none; width: 100%;   margin-top: 0; table-layout: fixed;">
            <tr style="font-size: 9px; ">
              <th style="border-right: 1px solid black; border-bottom: 1px solid black; width: 20%; padding: 8px;">Shipping Marks</th>
              <th style="border-right: 1px solid black; border-bottom: 1px solid black; width: 15%; padding: 8px;">No. of Packages<br/>or Shipping Units</th>
              <th style="border-right: 1px solid black; border-bottom: 1px solid black; width: 35%; padding: 8px;">Description of Packages or Goods</th>
              <th style="border-right: 1px solid black; border-bottom: 1px solid black; width: 15%; padding: 8px;">Gross Weight</th>
              <th style=" border-bottom: 1px solid black; width: 15%; padding: 8px;">Measurement<br/>(Volume)</th>
            </tr>
            {goods_data_rows_html}
          </table>
          

          <!-- Freight Payable Row -->
          <table style="border-left: none !; border-right: none; width: 100%; border-top: 1px solid black; border-bottom: 1px solid black; border-collapse: collapse; table-layout: fixed;">
            <tr>
              <td style="width: 50%; border-right: 1px solid black; padding: 3px; height: 30px; vertical-align: middle;">
                <table style="width: 100%; table-layout: fixed;">
                  <tr>
                    <td style="width: 50%;">Freight Payable at:</td>
                    <td style="width: 50%; text-align: center;"><strong>{freight_payable_at}</strong></td>
                  </tr>
                </table>
              </td>
              <td style="width: 50%; padding: 3px; text-align: center; vertical-align: middle; word-wrap: break-word;">
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Officia, autem.
              </td>
            </tr>
          </table>

          <!-- Terms and Conditions -->
          <div style="font-size:8px; padding: 8px; border-bottom: 1px solid black; border-top: none;">
            <p style="margin-bottom: 2px;">
              <strong>RECEIVED</strong> by the Carrier the Goods as specified above in apparent good order and condition unless otherwise stated, to be transported to such place as agreed, authorized or permitted herein and subject to all the terms and conditions appearing on the front and reverse of this Bill of Lading to which the Merchant agrees by accepting this Bill of Lading, any local privileges and customs notwithstanding.
            </p>
            <p style="margin-bottom: 2px;">
              <strong>THE PARTICULARS GIVEN ABOVE AS DECLARED BY THE SHIPPER</strong> and the weight, measure, quantity, condition, contents and value of the Goods are unknown to the Carrier.
            </p>
            <p>
              <strong>IN WITNESS</strong> whereof one (1) original Bill of Lading has been signed if not otherwise stated above, the same being accomplished the other(s), if any, to be void. If required by the Carrier, one (1) original Bill of Lading must be surrendered duly endorsed in exchange for the Goods or delivery order.
            </p>
          </div>

          <!-- Footer Section -->
          <table style="border-bottom: 1px solid black; table-layout: fixed;">
            <tr>
              <td style="width: 50%; border-right: 1px solid black; padding: 0; vertical-align: top;">
                <table style=" width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr>
                    <td style="padding: 3px; height: 30px; vertical-align: middle;">
                      <table style="width: 100%; table-layout: fixed;">
                        <tr>
                          <td style="width: 60%;">Number of Original Bill of Lading:</td>
                          <td style="width: 40%; text-align: center;"><strong>{no_of_original_bl}</strong></td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  <tr>
                    <td style="border-top: 1px solid black; padding: 3px; height: 30px; vertical-align: middle;">
                      <table style="width: 100%; table-layout: fixed;">
                        <tr>
                          <td style="width: 60%;">Total Number of Cartons:</td>
                          <td style="width: 40%; text-align: center;"><strong>{total_no_of_cartons} CTN</strong></td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
              <td style="width: 50%; padding: 0; vertical-align: top; overflow: hidden;">
                <table style=" width: 100%; border-collapse: collapse; table-layout: fixed;">
                  <tr>
                    <td style="padding: 3px; height: 30px; vertical-align: middle;">
                      <div style="font-size: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        <strong>{place_and_date}</strong>
                      </div>
                    </td>
                  </tr>
                  <tr >
                    <td style="padding: 8px;">
                      <table style="width: 100%; table-layout: fixed;">
                        <tr>
                          <td style="width: 50%; vertical-align: top;">Signed on behalf of By</td>
                          <td style="width: 50%; text-align: right; vertical-align: bottom; padding-top: 40px;">
                            Authorized Signatory
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <div class="_footer_title">{footer_title}</div>
        </div>
      </body>
    </html>
    """

    return html_template
