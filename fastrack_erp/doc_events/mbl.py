import frappe



def validate(doc, method):
    total_container=0
    container_info=[]
    if doc.doctype == "Import Sea Master Bill":
        total_container=doc.total_container
        container_info=doc.container_info
    gr_weight=doc.gr_weight
    total_no_of_hbl=doc.total_no_of_hbl
    
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
    print(total_weight_of_container_list)
    print(gr_weight)
    if not gr_weight == total_weight_of_container_list and doc.doctype == "Import Sea Master Bill":
        frappe.throw("Total weight of container list is not equal to gross weight")
        
    # filter is_create=1 and get the weight
    hbl_info_list= [hbl for hbl in hbl_info if hbl.is_create==1]
    total_weight_of_hbl_list= sum(hbl.weight for hbl in hbl_info_list)
    if len(hbl_info_list)== total_no_of_hbl and not total_weight_of_hbl_list == gr_weight:
        mismatch_value= int(gr_weight) - int(total_weight_of_hbl_list)
        frappe.throw(f"Total weight of HBL list is not equal to gross weight mismatch value is {str(mismatch_value)}")
    if gr_weight< total_weight_of_hbl_list:
        frappe.throw("HBL weight is greater than gross weight")


def update_child_hbl(doc, method):
    name=doc.name
    parent_doctype=doc.mbl_doctype
    # create child doc in master bill
    mbl_doc = frappe.get_doc(parent_doctype, doc.mbl_no)
    if parent_doctype == "Import Sea Master Bill":
        get_all_weight_of_container_info= sum(container.weight for container in doc.container_info)
    else:
        get_all_weight_of_container_info= 0
    if not get_all_weight_of_container_info == int(doc.hbl_weight) and (parent_doctype == "Import Sea Master Bill") :
        frappe.throw("Total weight of container info is not equal to hbl gross weight")
   
    # Find and update the HBLInfo row with matching hbl_no
    if parent_doctype == "Import Sea Master Bill":
        for hbl_info in mbl_doc.hbl_info :
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.hbl_weight
                break
    if parent_doctype == "Import Air Master Bill":
        for hbl_info in mbl_doc.hbl_info:
            if hbl_info.name == doc.hbl_doc_name:
                hbl_info.hbl_link=doc.name
                hbl_info.is_create=1
                hbl_info.weight=doc.hbl_weight
                break
            
    
    validate(mbl_doc, method=None)
    mbl_doc.save(ignore_permissions=True)
 
            