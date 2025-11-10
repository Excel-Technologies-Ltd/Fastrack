import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry


class CustomPaymentEntry(PaymentEntry):
	"""
	Custom Payment Entry class that overrides ERPNext's PaymentEntry
	This allows you to override any method from the parent class
	"""


	def on_submit(self):
		self.make_gl_entries()
		self.update_outstanding_amounts()
		self.update_payment_schedule()
		self.update_payment_requests()
		self.update_advance_paid()  # advance_paid_status depends on the payment request amount
		self.set_status()
