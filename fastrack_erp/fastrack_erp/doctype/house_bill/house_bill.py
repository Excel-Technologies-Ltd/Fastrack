# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HouseBill(Document):
	def before_save(self):
		print("before submit")
		print(self.container_items)
		self.validate_weight()
	pass
	def validate_weight(self):
		master_bill = frappe.get_doc("Master Bill", self.master_bill_no)
		master_bill_items=master_bill.item_details
		frappe.msgprint(frappe.as_json(master_bill_items))
		# check total weight of master bill is equal to total weight of house bill
		existing_house_bill=frappe.get_all("House Bill", filters={"master_bill_no": self.master_bill_no},fields=["*"])
		frappe.msgprint(frappe.as_json(existing_house_bill))
		for item in self.container_items:
			if item.weight_in_kg > 0:
				item.weight_in_kg = item.weight_in_kg * 1000
			else:
				frappe.throw("Weight is required")
		frappe.throw("test")
