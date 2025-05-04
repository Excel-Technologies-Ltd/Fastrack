import frappe



def validate(doc, method):
    total_container=doc.total_container
    gr_weight=doc.gr_weight
    total_no_of_hbl=doc.total_no_of_hbl
    container_info=doc.container_info
    hbl_info=doc.hbl_info
    if len(container_info)> total_container:
        frappe.throw(f"Container list should be less than or equal to {total_container}")
    if len(hbl_info)> total_no_of_hbl:
        frappe.throw(f"HBL list should be less than or equal to {total_no_of_hbl}")
        
    total_weight_of_container_list= sum(container.weight for container in container_info)
    print(total_weight_of_container_list)
    print(gr_weight)
    if not gr_weight == total_weight_of_container_list:
        frappe.throw("Total weight of container list is not equal to gross weight")
        
        
    total_weight_of_hbl_list= sum(hbl.weight for hbl in hbl_info)
    if len(hbl_info)== total_no_of_hbl and not total_weight_of_hbl_list == gr_weight:
        mismatch_value= int(gr_weight) - int(total_weight_of_hbl_list)
        frappe.throw(f"Total weight of HBL list is not equal to gross weight mismatch value is {str(mismatch_value)}")
    if gr_weight< total_weight_of_hbl_list:
        frappe.throw("HBL weight is greater than gross weight")


def create_child_hbl(doc, method):
    name=doc.name
    
    # create child doc in master bill
    mbl_doc = frappe.get_doc("Import Sea Master Bill", doc.mbl_no)
    get_all_weight_of_container_info= sum(container.weight for container in doc.container_info)
    print(get_all_weight_of_container_info)
    print(doc.manifested_g_weight)
    if not get_all_weight_of_container_info == int(doc.manifested_g_weight):
        frappe.throw("Total weight of container info is not equal to manifested gross weight")
   
    mbl_doc.append("hbl_info", {
        "weight": doc.manifested_g_weight,
        "hbl_no": doc.name
    })
    validate(mbl_doc, method=None)
    mbl_doc.save()
            