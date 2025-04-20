import frappe
from frappe.model.mapper import get_mapped_doc
@frappe.whitelist()
def make_house_bill(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.master_bill_no=source.name
    doclist = get_mapped_doc("Master Bill", source_name, {
        "Master Bill": {
            "doctype": "House Bill",
            "field_map": {
                "voyage_number":"voy_no",
               "place_of_receipt":"place_of_recipt",
               "vessel":"occean_vessel",
               "port_of_loading":"portt_of_loading",
               "port_of_discharge":"port_of_discharge",
               "place_of_delivery":"place_of_delivery",
               "pre_carried_by":"pre_carriage_by",
               "place_of_issue":"place_of_issue",
               "date_of_issue":"date_of_issue",
            
               
                
            },
        },
    }, target_doc,set_missing_values)
  
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




