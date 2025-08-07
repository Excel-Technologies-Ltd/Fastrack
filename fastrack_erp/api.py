import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None,hbl_id=None):
    def set_missing_values(source, target):
        hbl_info=get_first_uncreated_hbl_info(source.name,"Import Sea Master Bill")
        # 4 array
        target.mbl_link=source.name
        target.hbl_doc_name=hbl_info.name
        target.mbl_doctype=hbl_info.parenttype    
        target.hbl_id=hbl_info.hbl_no
        target.mbl_no=source.mbl_no
        target.carrier=source.consignee
        target.agent=source.agent
        target.hbl_etd=source.etd
        target.fv__v_no=source.fv_voyage_no
        target.port_of_discharge=source.port_of_discharge
        target.mv_voyage_no=source.mv_voyage_no
        target.mbl_date=source.mbl_date
        target.port_of_delivery=source.port_of_delivery
        target.fv_etd=source.fv_etd
        
    doclist = get_mapped_doc("Import Sea Master Bill", source_name, {
        "Import Sea Master Bill": {
            "doctype": "Import Sea House Bill",
        },
    }, target_doc, set_missing_values)
  
    return doclist
@frappe.whitelist()
def make_air_house_bill(source_name, target_doc=None):
    def set_missing_values(source, target):
        hbl_info=get_first_uncreated_hbl_info(source.name,"Import Air Master Bill")
        # 4 array
        target.mbl_no=source.name
        target.hbl_no=hbl_info.hbl_no
        target.carrier=source.consignee
        target.agent=source.agent
        target.hbl_doc_name=hbl_info.name
        target.mbl_doctype=hbl_info.parenttype
    doclist = get_mapped_doc("Import Air Master Bill", source_name, {
        "Import Air Master Bill": {
            "doctype": "Import Air House Bill",
        },
    }, target_doc, set_missing_values)
  
    return doclist

# @frappe.whitelist()
# def make_payment_entry(source_name, target_doc=None):
    
#     doclist = get_mapped_doc("Import Air Master Bill", source_name, {
#         "Import Air Master Bill": {
#             "doctype": "Payment Entry",
#         },
#     }, target_doc,)
  
#     return doclist

@frappe.whitelist()
def make_sales_invoice_from_hbl(source_name, target_doc=None):
    def set_missing_values(source, target):
        
        target.custom_hbl_type="Import Sea House Bill"
        target.custom_hbl_sea_link=source.name
        target.customer=""
        target.customer_name=""
        target.customer_address=""
        
    doclist = get_mapped_doc("Import Sea House Bill", source_name, {
        "Import Sea House Bill": {
            "doctype": "Sales Invoice",
        },
    }, target_doc, set_missing_values)
    return doclist
@frappe.whitelist()
def make_purchase_invoice_from_hbl(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.custom_shbl_id=source.name
        target.custom_hbl_type="Import Sea House Bill"
    doclist = get_mapped_doc("Import Sea House Bill", source_name, {
        "Import Sea House Bill": {
            "doctype": "Purchase Invoice",
        },
    }, target_doc, set_missing_values)
    return doclist
@frappe.whitelist()
def make_journal_entry_from_hbl(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.custom_shbl_id=source.name
        target.custom_hbl_type="Import Sea House Bill"
    doclist = get_mapped_doc("Import Sea House Bill", source_name, {
        "Import Sea House Bill": {
            "doctype": "Journal Entry",
        },
    }, target_doc, set_missing_values)
    return doclist


@frappe.whitelist()
def get_containner_items_with_existing_house_bill(master_bill_no):
    
    doc = frappe.get_doc("Master Bill", master_bill_no)
    return doc.container_items



def get_house_container_items_by_master_bill_no(master_bill_no):
    
    house_doc_list = frappe.db.get_list("House Bill", {"master_bill_no": master_bill_no},['name'])
    housee_bill_array= [house_doc.name for house_doc in house_doc_list]
    
    # get fastrac items
    frappe.db.sql(f"""
    SELECT 
        item_code,
        SUM(qty) as qty
    FROM `tabFastrack Item`
    WHERE parenttype = 'House Bill'
    AND parent IN ({','.join(housee_bill_array)})
    GROUP BY item_code
    """)
    
    return housee_bill_array






# import frappe
# from dicttoxml import dicttoxml
# from xml.dom.minidom import parseString

# def sanitize_dict(data):
#     """Recursively clean None and datetime values."""
#     if isinstance(data, dict):
#         return {k: sanitize_dict(v) for k, v in data.items()}
#     elif isinstance(data, list):
#         return [sanitize_dict(item) for item in data]
#     elif hasattr(data, 'isoformat'):
#         return data.isoformat()
#     elif data is None:
#         return ""
#     else:
#         return data

# @frappe.whitelist()
# def download_xml_file(doctype, docname):
#     doc = frappe.get_doc(doctype, docname)
#     clean_dict = sanitize_dict(doc.as_dict())

#     # Convert to XML and pretty-print
#     xml_bytes = dicttoxml(clean_dict, custom_root=doctype.replace(" ", "_"), attr_type=False)
#     parsed = parseString(xml_bytes)
#     pretty_xml = parsed.toprettyxml(indent="  ")

#     # Return as downloadable file
#     frappe.response["type"] = "binary"
#     frappe.response["filename"] = f"{docname}.xml"
#     frappe.response["filecontent"] = pretty_xml.encode("utf-8")
#     frappe.response["headers"] = {
#         "Content-Type": "application/xml; charset=utf-8",
#         "Content-Disposition": f"attachment; filename={docname}.xml"
#     }



import frappe
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from frappe.utils.pdf import get_pdf
from frappe.utils import escape_html
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

def sanitize_dict(data):
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    elif hasattr(data, 'isoformat'):
        return data.isoformat()
    elif data is None:
        return ""
    else:
        return data

def dict_to_xml_without_item_tags(data, root_name):
    """
    Convert a dictionary to XML without adding 'item' tags for arrays.
    """
    def _to_xml(data, parent):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    # For lists, add child elements directly to parent without 'item' wrapper
                    for item in value:
                        child = SubElement(parent, key)
                        _to_xml(item, child)
                else:
                    child = SubElement(parent, key)
                    _to_xml(value, child)
        elif isinstance(data, list):
            # This handles lists that might be nested more deeply
            for item in data:
                _to_xml(item, parent)
        else:
            # Handle None values
            parent.text = str(data) if data is not None else ""
    
    root = Element(root_name)
    _to_xml(data, root)
    return root

@frappe.whitelist()
def download_xml_as_pdf(doctype="Import Sea Master Bill", docname="MBL-2025-05-0000015"):
    # check exist hbl
    hbl_dict = get_sea_master_bill_dict_for_xml(docname)
    if not hbl_dict:
        frappe.msgprint("No House Bill found for the Master Bill. Please create House Bill first.This is required to generate XML.")
        return
    clean_dict = sanitize_dict(get_sea_master_bill_dict_for_xml(docname)).get("Awbolds")

    # Convert to XML without item tags
    root_element = dict_to_xml_without_item_tags(clean_dict, "Awbolds")
    xml_string = tostring(root_element, encoding='utf-8').decode('utf-8')
    
    # Pretty print
    parsed = parseString(xml_string)
    pretty_xml = parsed.toprettyxml(indent="  ")
    last_id=docname.split("-")[-1]
    mbl_doc=frappe.get_doc("Import Sea Master Bill",docname)
    carrier_code=frappe.db.get_value("Supplier",mbl_doc.consignee,"custom_ain_no")
    
    # Remove XML declaration if needed
    if pretty_xml.startswith('<?xml'):
        pretty_xml = '\n'.join(pretty_xml.split('\n')[1:])

    html = f"""
    <html>
      <head>
        <style>
          pre {{
            font-family: monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #f4f4f4;
            padding: 10px;
            border: 1px solid #ddd;
            font-size: 12px;
          }}
        </style>
      </head>
      <body>
        <h3>{doctype}: {docname}</h3>
        <pre>{escape_html(pretty_xml)}</pre>
      </body>
    </html>
    """

    # Remove output_filename — it's not supported in Frappe v14
    pdf_content = get_pdf(html, options={"page-size": "A4"})

    frappe.response["type"] = "binary"
    frappe.response["filename"] = f"DEG{carrier_code}-{last_id}.xml"
    frappe.response["filecontent"] = pretty_xml.encode("utf-8")
    frappe.response["headers"] = {
        "Content-Type": "application/xml",
        "Content-Disposition": f"attachment; filename={docname}.xml"
    }

@frappe.whitelist()
def get_first_uncreated_hbl_info(master_bill_no="MBL-2025-05-00008",doctype="Import Sea Master Bill"):
    """Get the first HBLInfo row where is_create=0 for a given master bill"""
    doc = frappe.get_doc(doctype, master_bill_no)
    
    # Find the first HBLInfo row where is_create=0
    for hbl_info in doc.hbl_info:
        if not hbl_info.is_create:
            return hbl_info
            
    return None



def get_sea_master_bill_dict_for_xml(master_bill_no="MBL-2025-05-00015"):
    doc = frappe.get_doc("Import Sea Master Bill", master_bill_no)
    first_row=doc.hbl_info[0]
    # check exits
    if not frappe.db.exists("Import Sea House Bill", first_row.hbl_link) or len(doc.hbl_info)==0:
        return None
    first_row_doc=frappe.get_doc("Import Sea House Bill", first_row.hbl_link)
    return {
        "Awbolds":{
            "Master_bol":{
                "Custom_office_code":first_row_doc.office_code if first_row_doc.office_code else "",
                "Voyage_number":doc.fv_voyage_no,
                "Date_of_departure":doc.fv_etd,
                "Reference_number":doc.mbl_no
            },
            # convert dict to list
            "Bol_segment":get_sea_hbl_list_for_xml(master_bill_no)
        }
    }

def get_sea_hbl_list_for_xml(master_bill_no="MBL-2025-05-00015"):
    doc = frappe.get_doc("Import Sea Master Bill", master_bill_no)
    consolidated_cargo=1 if len(doc.hbl_info) > 1 else 0
    hbl_list = []
    if len(doc.hbl_info) > 0:
        for hbl_info in doc.hbl_info:
            if hbl_info.is_create:
                hbl_doc = frappe.get_doc("Import Sea House Bill", hbl_info.hbl_link)
                hbl_dict_for_xml= {
                    "Bol_id":{
                        "Bol_reference":hbl_doc.hbl_id,
                        "Line_number":hbl_doc.hbl_line_no,
                        "Bol_nature":hbl_doc.nature,
                        "Bol_type_code":hbl_doc.hbl_type_code,
                        "DG_status":hbl_doc.dg_status
                    },
                    "Consolidated_Cargo": 0 if hbl_doc.container_type == "FCL" else 1,
                    "Load_unload_place":{
                        "Port_of_origin_code":hbl_doc.port_of_origin_code,
                        "Port_of_unloading_code":hbl_doc.pod_code
                    },
                    "Traders_segment":{
                        "Carrier":{
                            "Carrier_code":frappe.db.get_value("Supplier",hbl_doc.carrier,"custom_ain_no"),
                            "Carrier_name":frappe.db.get_value("Supplier",hbl_doc.carrier,"supplier_name"),
                            "Carrier_address":clean_address(frappe.get_value("Supplier",hbl_doc.carrier,"primary_address")) if frappe.get_value("Supplier",hbl_doc.carrier,"primary_address") else ""
                        },
                        "Shipping_agent":{
                            # "Shipping_agent_name":frappe.db.get_value("Supplier",hbl_doc.shipping_line,"supplier_name"),
                            # "Shipping_agent_address": clean_address(frappe.get_value("Supplier",hbl_doc.shipping_line,"primary_address")) if frappe.get_value("Supplier",hbl_doc.shipping_line,"primary_address") else ""
                            "Shipping_agent_name":"",
                            "Shipping_agent_address":""
                        },
                        "Exporter":{
                           
                            "Exporter_name":frappe.db.get_value("Supplier",hbl_doc.hbl_shipper,"supplier_name"),
                            "Exporter_address":clean_address(frappe.get_value("Supplier",hbl_doc.hbl_shipper,"primary_address")) if frappe.get_value("Supplier",hbl_doc.hbl_shipper,"primary_address") else ""
                        },
                        "Notify":{
                            "Notify_code":frappe.db.get_value("Customer",hbl_doc.notify_to,"custom_bin_no"),
                            "Notify_name":frappe.db.get_value("Customer",hbl_doc.notify_to,"customer_name"),
                            "Notify_address": clean_address(frappe.get_value("Customer",hbl_doc.notify_to,"primary_address")) if frappe.get_value("Customer",hbl_doc.notify_to,"primary_address") else ""
                        },
                        "Consignee":{
                            "Consignee_code":frappe.db.get_value("Customer",hbl_doc.hbl_consignee,"custom_bin_no"),
                            "Consignee_name":frappe.db.get_value("Customer",hbl_doc.hbl_consignee,"customer_name"),
                            "Consignee_address": clean_address(frappe.get_value("Customer",hbl_doc.hbl_consignee,"primary_address")) if frappe.get_value("Customer",hbl_doc.hbl_consignee,"primary_address") else ""
                        }
                    },
                    "ctn_segment":get_container_info_for_xml(hbl_doc.container_info),
                    "Goods_segment": {
                            "Number_of_packages": smart_number(sum(item.no_of_pkg for item in hbl_doc.container_info)),
                            "Package_type_code": hbl_doc.pkg_code,
                            "Gross_mass": smart_number(hbl_doc.hbl_weight),
                            "Shipping_marks": hbl_doc.marks_and_numbers,
                            "Goods_description": hbl_doc.description_of_good,
                            "Volume_in_cubic_meters": smart_number(hbl_doc.hbl_vol_cbm),
                            "Num_of_ctn_for_this_bol": len(hbl_doc.container_info),
                            "Remarks": hbl_doc.remarks
                        },
                        "Value_segment": {
                           "Freight_segment": {
                            "Freight_value": 0,
                            "Freight_currency": "BDT"
                           }
                        }
                }
                hbl_list.append(hbl_dict_for_xml)
    return hbl_list



def get_container_info_for_xml(container_info_list=["ACC-PINV-2025-00002"]):
    container_info_list_for_xml=[]
    for container_info in container_info_list:
        container_info_list_for_xml.append({
                "Ctn_reference": container_info.custom_container_no,
                "Number_of_packages": smart_number(container_info.no_of_pkg),
                "Type_of_container": container_info.con_type,
                "Status": container_info.status,
                "Seal_number": container_info.seal_no,
                "IMCO": container_info.imco,
                "UN": container_info.un,
                "Ctn_location": container_info.ctn_location,
                "Commidity_code": container_info.commodity_code,
                "Gross_weight": smart_number(container_info.weight)
        })
    return container_info_list_for_xml








import html
def clean_address(raw_html):
    # Decode HTML entities like &lt;br&gt; -> <br>
    decoded = html.unescape(raw_html)
    
    # Replace <br> tags with commas, and strip whitespace
    cleaned = decoded.replace('<br>', ',').replace('\n', '')
    
    # Remove extra commas and whitespace
    parts = [part.strip() for part in cleaned.split(',') if part.strip()]
    return ','.join(parts)

def smart_number(value):
    return int(value) if value == int(value) else float(value)










import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist(allow_guest=True)
def download_purchase_invoice_pdf(invoice_ids,doctype_name):
    print(invoice_ids,doctype_name)
    try:
        # Convert string to list
        if isinstance(invoice_ids, str):
            invoice_ids = invoice_ids.split(',')
        print(invoice_ids)
        # Build HTML content without Jinja
        html_content = build_purchase_invoice_html(invoice_ids,doctype_name)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set response for download
        filename = f"purchase_invoices_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.log_error(f"PDF generation error: {str(e)}")
        frappe.throw(f"Error generating PDF: {str(e)}")

def build_purchase_invoice_html(invoice_ids, doctype_name):
    print ("doctype_name",doctype_name)
    print ("invoice_ids",invoice_ids)
    child_doctype_name = "Fastrack Purchase Invoice"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Purchase Invoices</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1 {{
                text-align: center;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 12px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                font-size: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f0f0f0;
            }}
            .text-right {{
                text-align: right;
            }}
            .no-data {{
                text-align: center;
                padding: 20px;
                font-style: italic;
                color: #777;
            }}
        </style>
    </head>
    <body>
    <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 55px;" />
        <h1>Expenses</h1>
        <p>Generated on: {frappe.utils.now_datetime().strftime('%Y-%m-%d %I:%M:%S %p')}</p>

    """

    rows = []
    grand_total = 0
    currency = "BDT"
    purchase_invoice_list=[]

    for invoice_id in invoice_ids:
        invoice_id = invoice_id.strip()
        print("invoice_id", invoice_id)
        print("frappe.db.exists(child_doctype_name, invoice_id)",frappe.db.exists(child_doctype_name, invoice_id))
        if not frappe.db.exists(child_doctype_name, invoice_id):
            continue
        try:
            invoice = frappe.get_doc(child_doctype_name, {"name": invoice_id, "parent": doctype_name})
            print(invoice)
            purchase_invoice_list.append(invoice.invoice_link)
            currency = invoice.currency or "BDT"
            grand_total += frappe.utils.flt(invoice.total_price or 0)

            date_str = frappe.format(invoice.date, dict(fieldtype="Date")) if invoice.date else ""

            rows.append(f"""
                <tr>
                    <td>{escape_html(invoice.invoice_link or '')}<br>{escape_html(date_str)}</td>
                    <td>{escape_html(invoice.item_code or '')}</td>
                    <td>{escape_html(invoice.supplier or '')}</td>
                    <td class="text-right">{invoice.qty}</td>
                    <td class="text-right">{str(frappe.utils.flt(invoice.rate))}</td>
                    <td class="text-right">{str(frappe.utils.flt(invoice.amount))}</td>
                    <td class="text-right">{ str(frappe.utils.flt(invoice.exchange_rate or 0))}</td>
                    <td class="text-right">{ str(frappe.utils.flt(invoice.total_price or 0))}</td>
                </tr>
            """)
        except Exception as e:
            frappe.log_error(f"Invoice error: {invoice_id} - {str(e)}")
            rows.append(f"""
                <tr>
                    <td colspan="8" class="no-data">Error loading invoice {invoice_id}: {escape_html(str(e))}</td>
                </tr>
            """)

    if rows:
        paid_amount=0
        # remove duplicate invoice_id
        if len(purchase_invoice_list)>0:
            purchase_invoice_list=list(set(purchase_invoice_list))
            print(purchase_invoice_list)
            paid_amount=get_paid_amount_on_purchase_invoice(purchase_invoice_list)
        paid_amount = frappe.utils.flt(paid_amount or 0)
        html += f"""
        <table>
            <thead>
                <tr>
                    <th>Invoice</th>
                    <th>Item Code</th>
                    <th>Supplier</th>
                    <th>Qty</th>
                    <th>Rate ({currency})</th>
                    <th>Amount ({currency})</th>
                    <th>Exchange Rate</th>
                    <th>Total (BDT)</th> 
                </tr>
            </thead>
            <tbody>
        """ + ''.join(rows) + f"""
                <tr>
                    <td colspan="7" class="text-right"><strong>Grand Total</strong></td>
                    <td class="text-right"><strong>{str(frappe.utils.flt(grand_total))}</strong></td>
                </tr>
                <tr>
                    <td colspan="7" class="text-right"><strong>Paid Amount</strong></td>
                    <td class="text-right"><strong>{str(frappe.utils.flt(paid_amount))}</strong></td>
                </tr>
                <tr>
                    <td colspan="7" class="text-right"><strong>Due Amount</strong></td>
                    <td class="text-right"><strong>{str(frappe.utils.flt(grand_total - paid_amount))}</strong></td>
                </tr>
            </tbody>
        </table>
        """
    else:
        html += """
        <div class="no-data">
            No valid invoices found.
        </div>
        """

    html += "</body></html>"
    return html




@frappe.whitelist(allow_guest=True)
def download_profit_share_pdf(journal_ids,doctype_name):
    try:
        # Convert string to list
        if isinstance(journal_ids, str):
            journal_ids = journal_ids.split(',')
        
        # Build HTML content without Jinja
        html_content = build_profit_share_html(journal_ids,doctype_name)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set response for download
        filename = f"purchase_invoices_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.log_error(f"PDF generation error: {str(e)}")
        frappe.throw(f"Error generating PDF: {str(e)}")

def build_profit_share_html(journal_ids,doctype_name):
    child_doctype_name = "Fastrack Journal Entry"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Profit Share</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1 {{
                text-align: center;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 12px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                font-size: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f0f0f0;
            }}
            .text-right {{
                text-align: right;
            }}
            .no-data {{
                text-align: center;
                padding: 20px;
                font-style: italic;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 55px;" />
        <h1>Profit Share</h1>
        <p>Generated on: {frappe.utils.now_datetime().strftime('%Y-%m-%d %I:%M:%S %p')}</p>

    """

    rows = []
    grand_total = 0
    currency = "BDT"

    for journal_id in journal_ids:
        journal_id = journal_id.strip()
        if not frappe.db.exists(child_doctype_name, journal_id):
            continue
        try:
            journal_entry = frappe.get_doc(child_doctype_name, {"name": journal_id, "parent": doctype_name})
          
            grand_total += frappe.utils.flt(journal_entry.amount or 0)

            rows.append(f"""
                <tr>
                    <td>{escape_html(journal_entry.journal_id or '')}</td>
                    <td>{escape_html(journal_entry.party_type or '')}</td>
                    <td>{escape_html(journal_entry.party or '')}</td>
                    <td class="text-right">{journal_entry.account_name}</td>
                    <td class="text-right">{str(frappe.utils.flt(journal_entry.credit))}</td>
                    <td class="text-right">{str(frappe.utils.flt(journal_entry.debit))}</td>
                </tr>
            """)
        except Exception as e:
            frappe.log_error(f"Journal Entry error: {journal_id} - {str(e)}")
            rows.append(f"""
                <tr>
                    <td colspan="8" class="no-data">Error loading journal entry {journal_id}: {escape_html(str(e))}</td>
                </tr>
            """)

    if rows:
        html += f"""
        <table>
            <thead>
                <tr>
                    <th>Journal ID</th>
                    <th>Party Type</th>
                    <th>Party</th>
                    <th>Account</th>
                    <th>Credit</th>
                    <th>Debit</th>
                    
                </tr>
            </thead>
            <tbody>
        """ + ''.join(rows) + f"""
                <tr>
                    <td colspan="5" class="text-right"><strong>Grand Total</strong></td>
                    <td class="text-right"><strong>{str(frappe.utils.flt(grand_total))}</strong></td>
                </tr>
            </tbody>
        </table>
        """
    else:
        html += """
        <div class="no-data">
            No valid journal entries found.
        </div>
        """

    html += "</body></html>"
    return html



# sales invoice pdf
@frappe.whitelist(allow_guest=True)
def download_sales_invoice_pdf(invoice_ids,doctype_name):
    try:
        # Convert string to list
        if isinstance(invoice_ids, str):
            invoice_ids = invoice_ids.split(',')
        
        # Build HTML content without Jinja
        html_content = build_sales_invoice_html(invoice_ids,doctype_name)
        
        # Generate PDF
        pdf_content = get_pdf(html_content)
        
        # Set response for download
        filename = f"sales_invoices_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.pdf"
        frappe.local.response.filename = filename
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.log_error(f"PDF generation error: {str(e)}")
        frappe.throw(f"Error generating PDF: {str(e)}")
    
def build_sales_invoice_html(invoice_ids, doctype_name):
    child_doctype_name = "Fastrack Sales Invoice"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Profit Share</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1 {{
                text-align: center;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 12px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
                font-size: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f0f0f0;
            }}
            .text-right {{
                text-align: right;
            }}
            .no-data {{
                text-align: center;
                padding: 20px;
                font-style: italic;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <img src="https://ftcl-portal.arcapps.org/files/Fastrack-AI.jpg" alt="Fasttrack Logo" style="height: 55px;" />
        <h1>Sales Invoice</h1>
        <p>Generated on: {frappe.utils.now_datetime().strftime('%Y-%m-%d %I:%M:%S %p')}</p>

    """

    rows = []
    grand_total = 0
    currency = "BDT"

    for invoice_id in invoice_ids:
        invoice_id = invoice_id.strip()
        if not frappe.db.exists(child_doctype_name, invoice_id):
            continue
        try:
            invoice = frappe.get_doc(child_doctype_name, {"name": invoice_id, "parent": doctype_name})
          
            grand_total += frappe.utils.flt(invoice.total_price or 0)

            rows.append(f"""
                <tr>
                    <td>{escape_html(invoice.invoice_link or '')}</td>
                    <td>{escape_html(invoice.customer or '')}</td>
                    <td class="text-right">{invoice.item_code}</td>
                    <td class="text-right">{invoice.qty}</td>
                    <td class="text-right">{str(frappe.utils.flt(invoice.rate))}</td>
                    <td class="text-right">{str(frappe.utils.flt(invoice.total_price or 0))}</td>
                </tr>
            """)
        except Exception as e:
            frappe.log_error(f"Sales Invoice error: {invoice_id} - {str(e)}")
            rows.append(f"""
                <tr>
                    <td colspan="8" class="no-data">Error loading sales invoice {invoice_id}: {escape_html(str(e))}</td>
                </tr>
            """)

    if rows:
        html += f"""
        <table>
            <thead>
                <tr>
                    <th>Invoice Id</th>
                    <th>Customer</th>
                    <th>Item Code</th>
                    <th>QTY</th>
                    <th>Rate</th>
                    <th>Total Price</th>
                    
                </tr>
            </thead>
            <tbody>
        """ + ''.join(rows) + f"""
                <tr>
                    <td colspan="5" class="text-right"><strong>Grand Total</strong></td>
                    <td class="text-right"><strong>{str(frappe.utils.flt(grand_total))}</strong></td>
                </tr>
            </tbody>
        </table>
        """
    else:
        html += """
        <div class="no-data">
            No valid journal entries found.
        </div>
        """

    html += "</body></html>"
    return html

    

def escape_html(text):
    """Escape HTML special characters to prevent XSS"""
    if not text:
        return ""
    
    text = str(text)
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    return "".join(html_escape_table.get(c, c) for c in text)






@frappe.whitelist(allow_guest=True)
def get_customer_list_by_hbl_id(id='SHBL-2025-07-08-0011',doctype="Import Sea House Bill"):
    if not frappe.db.exists(doctype,id):
        return []
    customer_list=[]
    if doctype=="Import Sea House Bill":
        
        sea_house_bill_doc=frappe.get_doc("Import Sea House Bill",id)
        if sea_house_bill_doc.customer:
            customer_list.append(sea_house_bill_doc.customer)
        if sea_house_bill_doc.hbl_consignee:
            customer_list.append(sea_house_bill_doc.hbl_consignee)
        if sea_house_bill_doc.co_loader:
            customer_list.append(sea_house_bill_doc.co_loader)
        if sea_house_bill_doc.carrier:
            customer_list.append(sea_house_bill_doc.carrier)
        if sea_house_bill_doc.notify_to:
            customer_list.append(sea_house_bill_doc.notify_to)
    remove_duplicate_customer_list=list(set(customer_list))
    return remove_duplicate_customer_list

# supplier list
@frappe.whitelist(allow_guest=True)
def get_supplier_list_by_hbl_id(id='SHBL-2025-07-08-0011',doctype="Import Sea House Bill"):
    if not frappe.db.exists(doctype,id):
        return []
    supplier_list=[]
    if doctype=="Import Sea House Bill":
        sea_house_bill_doc=frappe.get_doc("Import Sea House Bill",id)
        if sea_house_bill_doc.hbl_shipper:
            supplier_list.append(sea_house_bill_doc.hbl_shipper)
        if sea_house_bill_doc.agent:
            supplier_list.append(sea_house_bill_doc.agent)
        if sea_house_bill_doc.shipping_line:
            supplier_list.append(sea_house_bill_doc.shipping_line)
    remove_duplicate_supplier_list=list(set(supplier_list))
    return remove_duplicate_supplier_list

# agent list



def get_paid_amount_on_purchase_invoice(invoice_id_list: []):
    # Handle empty list
    if not invoice_id_list:
        return 0
    
    # Ensure that each invoice ID is wrapped in single quotes
    formatted_invoice_ids = ["'{}'".format(invoice_id) for invoice_id in invoice_id_list]
    sql_query = f"""
    SELECT SUM(allocated_amount * exchange_rate) as paid_amount 
    FROM `tabPayment Entry Reference` 
    WHERE parenttype = "Payment Entry" 
    AND docstatus = 1
    AND reference_doctype = "Purchase Invoice" 
    AND reference_name IN ({','.join(formatted_invoice_ids)})
    """
    
    result = frappe.db.sql(sql_query)
    
    # Handle None result from SUM when no rows match or all values are NULL
    if result and result[0] and result[0][0] is not None:
        return result[0][0]
    else:
        return 0
