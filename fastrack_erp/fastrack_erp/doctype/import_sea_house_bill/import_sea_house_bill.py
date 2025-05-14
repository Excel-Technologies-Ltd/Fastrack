# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ImportSeaHouseBill(Document):

	def on_update(self):
		self.validate_container_weight()
		self.hbl_weight= sum(item.weight for item in self.container_info)
		self.validate_container_name()
	def validate_container_name(self):
		
		mbl_doc = frappe.get_doc('Import Sea Master Bill', self.mbl_no)
		container_name_array= [item.container_no for item in mbl_doc.container_info]
		custom_container_name_array = [item.custom_container_no for item in self.container_info]
		print(frappe.as_json(container_name_array))
		# find unmatch value from custom_container_name_array and container_name_array
		unmatch_value = [value for value in custom_container_name_array if value not in container_name_array]
		print(container_name_array)
		# print(custom_container_name_array)
		# print(unmatch_value)
		if len(unmatch_value) > 0:
			join_unmatch_value = ', '.join(unmatch_value)
			frappe.throw(f"Container name do not match with master bill: {join_unmatch_value}")


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
			house_item_weight = get_house_item['weight'] or 0.0
			master_item_weight = get_master_item['weight'] or 0.0
			item_weight = item.weight or 0.0
			if master_item_weight < house_item_weight + item_weight :
				frappe.throw(f"Weight mismatch for container: {item.container_no}, should be less than or equal to {get_master_item['weight']}")

@frappe.whitelist()
def get_single_fastrack_item_by_bill_no(bill_no, item_name, parent_type='Import Sea Master Bill'):
	if not bill_no:  # Handle empty list case
		return {
			"item_name": item_name,
			"weight": 0.0
		}
	table_name = 'tabFastrack Item'
	item_name='container_no'
	if parent_type == 'Import Sea House Bill':
		table_name = 'tabFastrack Sea Item'
		item_name='custom_container_no'
	elif parent_type == 'Import Sea Master Bill':
		table_name = 'tabFastrack Item'
		item_name='container_no'
		
	# Ensure bill_no is a list of strings and join them properly into a string
	bill_no_placeholder = ', '.join([f"'{doc}'" for doc in bill_no])

	# Build the query with properly formatted bill_no
	result = frappe.db.sql(f"""
		SELECT 
			{item_name} as item_name,
			SUM(weight) as weight
		FROM `{table_name}`
		WHERE parenttype = '{parent_type}'
		AND parent IN ({bill_no_placeholder})
		AND {item_name} = '{item_name}'
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

