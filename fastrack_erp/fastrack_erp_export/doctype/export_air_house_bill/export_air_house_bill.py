# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt

import random
import frappe
from frappe.model.document import Document

class ExportAirHouseBill(Document):

	def onload(self):
		"""Load invoice, payment, and draft data"""
		self.hbl_data = self.name

		# Get invoice list and payment entries
		invoice_list = self.get_invoice_list()
		gl_entry_list = get_gl_entry_from_invoice(invoice_list)
		payment_entry = []

		for idx, gl_entry in enumerate(gl_entry_list):
			payment_entry_doc = frappe.new_doc("Fastrack Payment Entry")
			payment_entry_doc.idx = idx + 1
			payment_entry_doc.payment_link = gl_entry.voucher_no
			payment_entry_doc.customer = gl_entry.party
			payment_entry_doc.invoice = gl_entry.against_voucher
			payment_entry_doc.amount = gl_entry.credit_in_account_currency
			payment_entry_doc.parent = self.name
			payment_entry_doc.parenttype = "Export Air House Bill"
			payment_entry_doc.parentfield = "payment_entry_list"
			payment_entry.append(payment_entry_doc)

		self.payment_entry_list = payment_entry
		self.total_payment = sum(float(item.amount) for item in payment_entry)

		# Get draft invoices
		draft_list = get_draft_sales_and_purchase_invoice_list(self.name)
		draft_invoice_list = []

		for item in draft_list:
			draft_invoice = frappe.new_doc("Fastrack Draft Bill")
			draft_invoice.type = item["type"]
			draft_invoice.invoice_id = item["id"]
			draft_invoice.amount = item["amount"]
			draft_invoice.parent = self.name
			draft_invoice.parenttype = "Export Air House Bill"
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

	def validate(self):
		# Validate weight distribution
		self.validate_weight()

	def validate_weight(self):
		"""Ensure HBL weight doesn't exceed MBL gross weight"""
		if not self.mbl_link:
			return

		mbl_doc = frappe.get_doc('Export Air Master Bill', self.mbl_link)

		# Get existing house bills for this MBL (excluding current)
		existing_hbls = frappe.db.get_list(
			'Export Air House Bill',
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
				'Export Air House Bill',
				{'name': ['in', existing_hbls]},
				'sum(hbl_gr_weight)'
			) or 0

		# Check if total weight exceeds MBL gross weight
		total_weight = total_other_weight + (self.hbl_gr_weight or 0)

		if total_weight > mbl_doc.gr_weight:
			frappe.throw(
				f"Total HBL weight ({total_weight}) exceeds MBL gross weight ({mbl_doc.gr_weight})"
			)

	def get_invoice_list(self):
		"""Get list of invoice links"""
		return [invoice.invoice_link for invoice in self.invoice_list if invoice.invoice_link]


@frappe.whitelist()
def get_gl_entry_from_invoice(invoice_list):
	"""Get GL entries for payment tracking"""
	default_receivable_account = frappe.get_all("Company", ["default_receivable_account", 'name'])
	bank_account = default_receivable_account[0].default_receivable_account
	default_company = default_receivable_account[0].name

	gl_entry_list = frappe.db.get_list("GL Entry",
		filters=[
			["company", "=", default_company],
			["account", "=", bank_account],
			["voucher_type", "=", "Payment Entry"],
			["against_voucher_type", "=", "Sales Invoice"],
			["against_voucher", "in", invoice_list],
			["credit_in_account_currency", ">", 0],
			["docstatus", "=", 1]
		],
		fields=["name", 'credit_in_account_currency', 'party', 'voucher_no', "against_voucher"]
	)
	return gl_entry_list


@frappe.whitelist()
def get_draft_sales_and_purchase_invoice_list(house_bill_no):
	"""Get draft invoices for Export Air House Bill"""
	invoice_list = []

	try:
		# Get sales invoices
		sales_invoice_list = frappe.db.get_list(
			"Sales Invoice",
			filters=[
				["custom_hbl_export_air_link", "=", house_bill_no],
				["docstatus", "=", 0]
			],
			fields=["name", "base_grand_total"]
		)

		# Get purchase invoices
		purchase_invoice_list = frappe.db.get_list(
			"Purchase Invoice",
			filters=[
				["custom_eahbl_id", "=", house_bill_no],
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
