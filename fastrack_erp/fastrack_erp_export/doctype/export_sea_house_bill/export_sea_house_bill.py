# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExportSeaHouseBill(Document):

	def before_save(self):
		# Set user tracking
		if not self.hbl_open_by:
			self.hbl_open_by = frappe.session.user

	def validate(self):
		# Validate weight distribution
		self.validate_weight()

	def validate_weight(self):
		"""Ensure HBL weight doesn't exceed MBL gross weight"""
		if not self.mbl_link:
			return

		mbl_doc = frappe.get_doc('Export Sea Master Bill', self.mbl_link)

		# Get existing house bills for this MBL (excluding current)
		existing_hbls = frappe.db.get_list(
			'Export Sea House Bill',
			filters={'mbl_link': self.mbl_link, 'docstatus': 1},
			pluck='name'
		)

		# Remove current doc if editing
		if self.name and self.name in existing_hbls:
			existing_hbls.remove(self.name)

		# Calculate total weight of other HBLs
		total_other_weight = 0
		if existing_hbls:
			total_other_weight = frappe.db.get_value(
				'Export Sea House Bill',
				{'name': ['in', existing_hbls]},
				'sum(gross_weight)'
			) or 0

		# Check if total weight exceeds MBL gross weight (if MBL has gr_weight)
		if mbl_doc.get('gr_weight'):
			try:
				mbl_weight = float(mbl_doc.gr_weight)
				total_weight = total_other_weight + (self.gross_weight or 0)

				if total_weight > mbl_weight:
					frappe.throw(
						f"Total HBL weight ({total_weight}) exceeds MBL gross weight ({mbl_weight})"
					)
			except (ValueError, TypeError):
				pass  # If gr_weight is not numeric, skip validation
