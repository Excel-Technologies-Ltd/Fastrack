import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry


class CustomPaymentEntry(PaymentEntry):


	def on_submit(self):
		frappe.msgprint("Payment Entry Submitted")
		self.make_gl_entries()
		self.update_outstanding_amounts()
		self.update_payment_schedule()
		# self.update_payment_requests()
		self.update_advance_paid()  
		self.set_status()
