import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.mbl_no=source.name
        target.hbl_parent=source.parent
        target.carrier=source.consignee
        target.agent=source.agent
    doclist = get_mapped_doc("Import Sea Master Bill", source_name, {
        "Import Sea Master Bill": {
            "doctype": "Import Sea House Bill",
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

@frappe.whitelist()
def download_xml_as_pdf(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    clean_dict = sanitize_dict(doc.as_dict())

    xml_bytes = dicttoxml(clean_dict, custom_root=doctype.replace(" ", "_"), attr_type=False)
    parsed = parseString(xml_bytes)
    pretty_xml = parsed.toprettyxml(indent="  ")

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

    # Remove output_filename — it’s not supported in Frappe v14
    pdf_content = get_pdf(html, options={"page-size": "A4"})

    frappe.response["type"] = "binary"
    frappe.response["filename"] = f"{docname}.xml.pdf"
    frappe.response["filecontent"] = pdf_content
    frappe.response["headers"] = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"attachment; filename={docname}.xml.pdf"
    }





