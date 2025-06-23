import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None,hbl_id=None):
    def set_missing_values(source, target):
        hbl_info=get_first_uncreated_hbl_info(source.name,"Import Sea Master Bill")
        # 4 array
        target.mbl_link=source.name
        target.mbl_no=source.mbl_no
        target.hbl_id=hbl_info.hbl_no
        target.carrier=source.consignee
        target.agent=source.agent
        target.hbl_doc_name=hbl_info.name
        target.mbl_doctype=hbl_info.parenttype
        target.hbl_etd=source.etd
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
        target.naming_series="SAHBL-.YYYY.-.MM.-"
        target.hbl_id=hbl_info.hbl_no
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

@frappe.whitelist()
def make_sales_invoice_from_hbl(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.custom_hbl_sea_link=source.name
        target.custom_hbl_type="Import Sea House Bill"
        target.customer=""
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
def download_xml_as_pdf(doctype="Import Sea Master Bill", docname="MBL-2025-05-00015"):
    clean_dict = sanitize_dict(get_sea_master_bill_dict_for_xml(docname)).get("Awbolds")

    # Convert to XML without item tags
    root_element = dict_to_xml_without_item_tags(clean_dict, "Awbolds")
    xml_string = tostring(root_element, encoding='utf-8').decode('utf-8')
    
    # Pretty print
    parsed = parseString(xml_string)
    pretty_xml = parsed.toprettyxml(indent="  ")
    
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
    frappe.response["filename"] = f"{docname}.xml"
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
    first_row_doc=frappe.get_doc("Import Sea House Bill", first_row.hbl_link)
    print("first_row_doc", first_row_doc)
    return {
        "Awbolds":{
            "Master_bol":{
                "Custom_office_code":first_row_doc.office_code if first_row_doc.office_code else "",
                "Voyage_number":doc.fv_voyage_no,
                "Date_of_departure":doc.etd,
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
                        "Line_number":1,
                        "Bol_nature":hbl_doc.nature,
                        "Bol_type_code":hbl_doc.bl_type_code
                    },
                    "Consolidated_Cargo":consolidated_cargo ,
                    "Load_unload_place":{
                        "Port_of_origin_code":hbl_doc.port_of_origin_code,
                        "Port_of_unloading_code":hbl_doc.pod_code
                    },
                    "Traders_segment":{
                        "Carrier":{
                            "Carrier_code":frappe.db.get_value("Customer",hbl_doc.carrier,"custom_ain_no"),
                            "Carrier_name":frappe.db.get_value("Customer",hbl_doc.carrier,"customer_name"),
                            "Carrier_address":clean_address(frappe.get_value("Customer",hbl_doc.carrier,"primary_address")) if frappe.get_value("Customer",hbl_doc.carrier,"primary_address") else ""
                        },
                        "Shipping_agent":{
                            "Shipping_agent_name":frappe.db.get_value("Customer",hbl_doc.shipping_line,"customer_name"),
                            "Shipping_agent_address": clean_address(frappe.get_value("Customer",hbl_doc.shipping_line,"primary_address")) if frappe.get_value("Customer",hbl_doc.shipping_line,"primary_address") else ""
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
                            "Consignee_code":frappe.db.get_value("Customer",hbl_doc.hbl_consignee,"custom_ain_no"),
                            "Consignee_name":frappe.db.get_value("Customer",hbl_doc.hbl_consignee,"customer_name"),
                            "Consignee_address": clean_address(frappe.get_value("Customer",hbl_doc.hbl_consignee,"primary_address")) if frappe.get_value("Customer",hbl_doc.hbl_consignee,"primary_address") else ""
                        }
                    },
                    "ctn_segment":get_container_info_for_xml(hbl_doc.container_info),
                    "Goods_segment": {
                            "Number_of_packages": sum(item.no_of_pkg for item in hbl_doc.container_info),
                            "Package_type_code": hbl_doc.pkg_code,
                            "Gross_mass": hbl_doc.hbl_weight,
                            "Shipping_marks": "",
                            "Goods_description": hbl_doc.description_of_good,
                            "Volume_in_cubic_meters": 100,
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
                "Number_of_packages": container_info.no_of_pkg,
                "Type_of_container": container_info.con_type,
                "Status": container_info.status,
                "Seal_number": container_info.seal_no,
                "IMCO": container_info.imco,
                "UN": container_info.un,
                "Ctn_location": container_info.ctn_location,
                "Commidity_code": container_info.commodity_code,
                "Gross_weight": container_info.weight
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












import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist(allow_guest=True)
def download_purchase_invoice_pdf(invoice_ids):
    try:
        # Convert string to list
        if isinstance(invoice_ids, str):
            invoice_ids = invoice_ids.split(',')
        
        # Build HTML content without Jinja
        html_content = build_invoice_html(invoice_ids)
        
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

def build_invoice_html(invoice_ids):
    """Build HTML content programmatically without Jinja templates"""
    
    # Start HTML structure
    html_parts = [
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Expense</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 15px;
                }
                .invoice-section {
                    margin-bottom: 40px;
                    page-break-inside: avoid;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    overflow: hidden;
                }
                .invoice-header {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-bottom: 1px solid #ddd;
                }
                .invoice-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 10px;
                }
                .invoice-details {
                    display: flex;
                    justify-content: space-between;
                    flex-wrap: wrap;
                    gap: 15px;
                }
                .detail-item {
                    flex: 1;
                    min-width: 200px;
                }
                .detail-label {
                    font-weight: bold;
                    color: #666;
                }
                .detail-value {
                    color: #333;
                    margin-top: 2px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 0;
                }
                th {
                    background-color: #007bff;
                    color: white;
                    padding: 12px 8px;
                    text-align: left;
                    font-weight: bold;
                }
                td {
                    padding: 10px 8px;
                    border-bottom: 1px solid #eee;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .text-right {
                    text-align: right;
                }
                .text-center {
                    text-align: center;
                }
                .no-data {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-style: italic;
                }
                .total-row {
                    font-weight: bold;
                    background-color: #f0f8ff;
                    border-top: 2px solid #007bff;
                }
                @media print {
                    body { margin: 10px; }
                    .invoice-section { page-break-inside: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Expense</h1>
                <p>Generated on: """ + str(frappe.utils.now_datetime().strftime('%Y-%m-%d %H:%M:%S')) + """</p>
            </div>
        """
    ]
    
    valid_invoices = 0
    
    # Process each invoice
    for invoice_id in invoice_ids:
        invoice_id = invoice_id.strip()
        
        # Check if invoice exists
        if not frappe.db.exists("Purchase Invoice", invoice_id):
            continue
        
        try:
            # Get invoice document
            invoice = frappe.get_doc("Purchase Invoice", invoice_id)
            valid_invoices += 1
            
            # Build invoice section
            html_parts.append(f"""
            <div class="invoice-section">
                <div class="invoice-header">
                    <div class="invoice-title">Invoice: {escape_html(invoice.name or '')}</div>
                    <div class="invoice-details">
                        <div class="detail-item">
                            <div class="detail-label">Supplier:</div>
                            <div class="detail-value">{escape_html(invoice.supplier or '')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Date:</div>
                            <div class="detail-value">{escape_html(str(invoice.posting_date or ''))}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Status:</div>
                            <div class="detail-value">{escape_html(invoice.status or '')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Grand Total:</div>
                            <div class="detail-value">{frappe.utils.fmt_money(invoice.grand_total or 0, currency=invoice.currency)}</div>
                        </div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Item Code</th>
                            <th>Item Name</th>
                            <th class="text-center">Quantity</th>
                            <th class="text-right">Rate</th>
                            <th class="text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """)
            
            # Add invoice items
            if invoice.items:
                item_total = 0
                for item in invoice.items:
                    item_amount = frappe.utils.flt(item.amount or 0)
                    item_total += item_amount
                    
                    html_parts.append(f"""
                        <tr>
                            <td>{escape_html(item.item_code or '')}</td>
                            <td>{escape_html(item.item_name or '')}</td>
                            <td class="text-center">{frappe.utils.flt(item.qty or 0, 2)}</td>
                            <td class="text-right">{frappe.utils.fmt_money(item.rate or 0, currency=invoice.currency)}</td>
                            <td class="text-right">{frappe.utils.fmt_money(item_amount, currency=invoice.currency)}</td>
                        </tr>
                    """)
                
                # Add total row
                html_parts.append(f"""
                        <tr class="total-row">
                            <td colspan="4" class="text-right"><strong>Total Amount:</strong></td>
                            <td class="text-right"><strong>{frappe.utils.fmt_money(item_total, currency=invoice.currency)}</strong></td>
                        </tr>
                """)
            else:
                html_parts.append("""
                        <tr>
                            <td colspan="5" class="no-data">No items found for this invoice</td>
                        </tr>
                """)
            
            html_parts.append("""
                    </tbody>
                </table>
            </div>
            """)
            
        except Exception as e:
            frappe.log_error(f"Error processing invoice {invoice_id}: {str(e)}")
            html_parts.append(f"""
            <div class="invoice-section">
                <div class="invoice-header">
                    <div class="invoice-title">Invoice: {escape_html(invoice_id)}</div>
                    <div class="no-data">Error loading invoice data: {escape_html(str(e))}</div>
                </div>
            </div>
            """)
    
    # Handle case where no valid invoices found
    if valid_invoices == 0:
        html_parts.append("""
        <div class="invoice-section">
            <div class="no-data">
                <h3>No Valid Invoices Found</h3>
                <p>Please check the invoice IDs and try again.</p>
            </div>
        </div>
        """)
    
    # Close HTML structure
    html_parts.append("""
        </body>
        </html>
    """)
    
    return ''.join(html_parts)

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