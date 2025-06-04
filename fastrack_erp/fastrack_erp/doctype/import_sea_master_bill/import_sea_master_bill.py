import frappe
from frappe.model.document import Document
from datetime import datetime

class ImportSeaMasterBill(Document):
	def before_save(self):
		if not self.mbl_open_by:
			self.mbl_open_by= frappe.session.user
		if not self.mbl_date:
			self.mbl_date= datetime.now().date()
	def on_update(self):
		# Proceed only if ETD and at least one of ETA, ATA_CTG, or ATB are set
  
		if self.etd:
			etd = self._parse_date(self.etd)
			print(etd)

			if self.eta:
				print("ETA", self.eta)
				eta = self._parse_date(self.eta)
				if etd > eta:
					frappe.throw("ETD cannot be less than ETA")

			if self.ata_ctg:
				ata_ctg = self._parse_date(self.ata_ctg)
				if etd > ata_ctg:
					frappe.throw("ETD cannot be less than ATA_CTG")

			if self.atb:
				atb = self._parse_date(self.atb)
				if etd > atb:
					frappe.throw("ETD cannot be less than ATB")
		self.validate_no_pkg_in_container()

	def _parse_date(self, date_val):
		# Convert string to datetime.date (if needed)
		if isinstance(date_val, str):
			try:
				return datetime.strptime(date_val, "%Y-%m-%d").date()
			except ValueError:
				# Try full datetime string format fallback
				return datetime.fromisoformat(date_val).date()
		elif isinstance(date_val, datetime):
			return date_val.date()
		else:
			return date_val  
	def validate_no_pkg_in_container(self):
		total_no_of_pkg = sum(item.no_of_pkg for item in self.container_info)
		if total_no_of_pkg != self.no_of_pkg:
			frappe.throw(f"Total number of package in container does not match with total package in master bill")
