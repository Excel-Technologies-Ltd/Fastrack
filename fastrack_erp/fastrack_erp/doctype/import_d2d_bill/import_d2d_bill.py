# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import random
import frappe
from frappe.model.document import Document

class ImportD2DBill(Document):

	def onload(self):
		"""Load invoice, payment, and draft data"""
		self.hbl_data = self.name

		# payment_entry_list / total_payment ("Total Payment Received") and
		# purchase_invoice_list / total_purchase_amount ("Total Expense Amount") are
		# maintained persistently by doc_events.payment_entry and
		# doc_events.purchase_invoice -- do not rebuild here.

		# Get draft invoices
		draft_list = get_draft_sales_and_purchase_invoice_list(self.name)
		draft_invoice_list = []

		for item in draft_list:
			draft_invoice = frappe.new_doc("Fastrack Draft Bill")
			draft_invoice.type = item["type"]
			draft_invoice.invoice_id = item["id"]
			draft_invoice.amount = item["amount"]
			draft_invoice.parent = self.name
			draft_invoice.parenttype = "Import D2D Bill"
			draft_invoice.parentfield = "draft_invoice_list"
			draft_invoice_list.append(draft_invoice)

		self.draft_invoice_list = draft_invoice_list

	def before_save(self):
		# Generate unique invoice UID
		if not self.get("invoice_uid"):
			generate_uuid = str(random.randint(10**9, 10**10 - 1))
			self.invoice_uid = f"INV-{generate_uuid}"

		# Set user tracking
		if not self.hbl_open_by:
			self.hbl_open_by = frappe.session.user

@frappe.whitelist()
def get_draft_sales_and_purchase_invoice_list(house_bill_no):
	"""Get draft invoices for Import D2D Bill"""
	invoice_list = []

	try:
		# Get sales invoices
		sales_invoice_list = frappe.db.get_list(
			"Sales Invoice",
			filters=[
				["custom_hbl_d2d_link", "=", house_bill_no],
				["docstatus", "=", 0]
			],
			fields=["name", "base_grand_total"]
		)

		# Get purchase invoices
		purchase_invoice_list = frappe.db.get_list(
			"Purchase Invoice",
			filters=[
				["custom_import_d2d_link", "=", house_bill_no],
				["docstatus", "=", 0]
			],
			fields=["name", "base_grand_total"]
		)

		# Process sales invoices
		if sales_invoice_list:
			for invoice in sales_invoice_list:
				invoice_list.append({
					"type": "Sales Invoice",
					"id": invoice.name,
					"amount": invoice.base_grand_total
				})

		# Process purchase invoices
		if purchase_invoice_list:
			for invoice in purchase_invoice_list:
				invoice_list.append({
					"type": "Purchase Invoice",
					"id": invoice.name,
					"amount": invoice.base_grand_total
				})

	except Exception as e:
		frappe.log_error(f"Error in get_draft_sales_and_purchase_invoice_list: {str(e)}")

	return invoice_list
