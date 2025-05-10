# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportSeaHouseBill(Document):

	def on_update(self):
		self.validate_container_weight()
		

	def validate_container_weight(self):
		master_bill_no = self.mbl_no
		for item in self.container_info:
			get_master_item = get_single_fastrack_item_by_bill_no([master_bill_no], item.container_no)
			print(get_master_item)
			get_existing_house_doc_id = frappe.db.get_list('Import Sea House Bill', {'mbl_no': master_bill_no,'docstatus': 1}, ['name'])
			get_existing_house_doc_id = [doc['name'] for doc in get_existing_house_doc_id]
			
			# If this is a new document, exclude it from the existing house bills list
			if self.name in get_existing_house_doc_id:
				get_existing_house_doc_id.remove(self.name)
			
			get_house_item = get_single_fastrack_item_by_bill_no(get_existing_house_doc_id, item.container_no, parent_type='Import Sea House Bill')
			if get_master_item['weight'] < get_house_item['weight'] + item.weight:
				frappe.throw(f"Weight mismatch for container: {item.container_no}, should be less than or equal to {get_master_item['weight']}")

@frappe.whitelist()
def get_single_fastrack_item_by_bill_no(bill_no, item_name, parent_type='Import Sea Master Bill'):
	if not bill_no:  # Handle empty list case
		return {
			"item_name": item_name,
			"weight": 0.0
		}
		
	# Ensure bill_no is a list of strings and join them properly into a string
	bill_no_placeholder = ', '.join([f"'{doc}'" for doc in bill_no])

	# Build the query with properly formatted bill_no
	result = frappe.db.sql(f"""
		SELECT 
			container_no as item_name,
			SUM(weight) as weight
		FROM `tabFastrack Item`
		WHERE parenttype = '{parent_type}'
		AND parent IN ({bill_no_placeholder})
		AND container_no = '{item_name}'
		GROUP BY container_no
	""", as_dict=True)
	
	if len(result) > 0:
		print(result[0])
		return result[0]
	else:
		return {
			"item_name": item_name,
			"weight": 0.0
		}

