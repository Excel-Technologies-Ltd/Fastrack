import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None,hbl_id=None):
    def set_missing_values(source, target):
        hbl_info=get_first_uncreated_hbl_info(source.name,"Import Sea Master Bill")
        # 4 array
        target.mbl_no=source.name
        target.hbl_id=hbl_info.hbl_no
        target.carrier=source.consignee
        target.agent=source.agent
        target.hbl_doc_name=hbl_info.name
        target.mbl_doctype=hbl_info.parenttype
        target.date_of_departure=source.etd
        target.date_of_arrival=source.eta
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
    return {
        "Awbolds":{
            "Master_bol":{
                "Custom_office_code":301,
                "Voyage_number":doc.fv_voyage_no,
                "Date_of_departure":"2025-05-01",
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
                        "Port_of_origin_code":hbl_doc.hbl_port_of_origin,
                        "Port_of_unloading_code":hbl_doc.hbl_place_of_unloading
                    },
                    "Traders_segment":{
                        "Carrier":{
                            "Carrier_code":hbl_doc.carrier,
                            "Carrier_name":frappe.db.get_value("Customer",hbl_doc.carrier,"customer_name"),
                            "Carrier_address":clean_address(hbl_doc.carrier_address_hbl) or ""
                        },
                        "Shipping_agent":{
                            "Shipping_agent_code":hbl_doc.shipping_line,
                            "Shipping_agent_name":frappe.db.get_value("Customer",hbl_doc.shipping_line,"customer_name"),
                            "Shipping_agent_address":clean_address(hbl_doc.shipping_line_address_hbl) or ""
                        },
                        "Exporter":{
                            "Exporter_code":hbl_doc.hbl_shipper,
                            "Exporter_name":frappe.db.get_value("Supplier",hbl_doc.hbl_shipper,"supplier_name"),
                            "Exporter_address":clean_address(hbl_doc.shipper_address_hbl) or ""
                        },
                        "Notify":{
                            "Notify_code":hbl_doc.notify_to,
                            "Notify_name":frappe.db.get_value("Customer",hbl_doc.notify_to,"customer_name"),
                            "Notify_address":clean_address(hbl_doc.notify_address_hbl) or ""
                        },
                        "Consignee":{
                            "Consignee_code":hbl_doc.hbl_consignee,
                            "Consignee_name":frappe.db.get_value("Customer",hbl_doc.hbl_consignee,"customer_name"),
                            "Consignee_address":clean_address(hbl_doc.consignee_address_hbl) or ""
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



def get_container_info_for_xml(container_info_list):
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