# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class ImportAirHouseBill(Document):
	def on_update(self):
		self.hbl_weight= sum(item.weight for item in self.container_info)
