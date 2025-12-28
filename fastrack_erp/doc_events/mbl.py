import frappe



def validate(doc, method):
    total_container=0
    container_info=[]
    if doc.doctype == "Import Sea Master Bill":
        total_container=doc.total_container
        container_info=doc.container_info
    gr_weight=doc.gr_weight
    total_no_of_hbl= doc.get("total_no_of_hbl") or doc.get("total__hbl")
    
    hbl_info=doc.hbl_info
    if len(container_info)> total_container and doc.doctype == "Import Sea Master Bill":
        frappe.throw(f"Container list should be less than or equal to {total_container}")
    if len(hbl_info)> total_no_of_hbl:
        frappe.throw(f"HBL list should be less than or equal to {total_no_of_hbl}")
    if not len(container_info)== total_container and doc.doctype == "Import Sea Master Bill":
        frappe.throw(f"Container list should be equal to {total_container}")
    if not len(hbl_info)== total_no_of_hbl:
        frappe.throw(f"HBL list should be equal to {total_no_of_hbl}")
    total_weight_of_container_list= sum(container.weight for container in container_info) or 0
    if not gr_weight == total_weight_of_container_list and doc.doctype == "Import Sea Master Bill":
        frappe.throw("Total weight of container list is not equal to gross weight")
        
    # filter is_create=1 and get the weight
    hbl_info_list= [hbl for hbl in hbl_info if hbl.is_create==1]
    total_weight_of_hbl_list= sum(hbl.weight for hbl in hbl_info_list)
    print(total_weight_of_hbl_list)
    print(gr_weight)
    if len(hbl_info_list)== total_no_of_hbl and not round(total_weight_of_hbl_list,2) == round(gr_weight,2):
        mismatch_value= round(gr_weight,2) - round(total_weight_of_hbl_list,2)
        frappe.throw(f"Total weight of HBL list is not equal to gross weight mismatch value is {str(mismatch_value)}")
    if gr_weight< total_weight_of_hbl_list:
        frappe.throw("HBL weight is greater than gross weight")


def update_child_hbl(doc, method):
    name=doc.name
    parent_doctype=doc.mbl_doctype
    # create child doc in master bill
    mbl_doc = frappe.get_doc(parent_doctype, doc.mbl_link)

    # Validate container weight for Sea imports
    if parent_doctype == "Import Sea Master Bill":
        get_all_weight_of_container_info= sum(float(container.weight) for container in doc.container_info)
        if not get_all_weight_of_container_info == float(doc.hbl_weight):
            frappe.throw("Total weight of container info is not equal to hbl gross weight")

    # Find and update the HBLInfo row with matching hbl_no
    if parent_doctype == "Import Sea Master Bill":
        for hbl_info in mbl_doc.hbl_info :
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.hbl_weight
                break
    elif parent_doctype == "Import Air Master Bill":
        for hbl_info in mbl_doc.hbl_info:
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.hbl_gr_weight
                break
    elif parent_doctype == "Export Sea Master Bill":
        for hbl_info in mbl_doc.hbl_info:
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.gross_weight
                break
    elif parent_doctype == "Export Air Master Bill":
        for hbl_info in mbl_doc.hbl_info:
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.hbl_gr_weight
                break

    # Only validate if it's an import master bill
    if parent_doctype in ["Import Sea Master Bill", "Import Air Master Bill"]:
        validate(mbl_doc, method=None)
    mbl_doc.save(ignore_permissions=True)
 
 
def delete_child_hbl_on_cancel(doc, method):
    name=doc.name
    parent_doctype=doc.mbl_doctype
    mbl_doc = frappe.get_doc(parent_doctype, doc.mbl_link)

    if parent_doctype in ["Import Sea Master Bill", "Import Air Master Bill", "Export Sea Master Bill", "Export Air Master Bill"]:
        for hbl_info in mbl_doc.hbl_info:
            if hbl_info.hbl_link == doc.name:
                hbl_info.hbl_link=None
                hbl_info.is_create=0
                break

    mbl_doc.save(ignore_permissions=True)
            