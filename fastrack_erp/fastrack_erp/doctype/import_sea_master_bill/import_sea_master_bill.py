import frappe
from frappe.model.document import Document
from datetime import datetime

class ImportSeaMasterBill(Document):
	def before_save(self):
		if not self.mbl_open_by:
			self.mbl_open_by= frappe.session.user
		if not self.mbl_date:
			self.mbl_date= datetime.now().date()
		if not self.naming_series_2:
			self.naming_series_2= self.naming_series

	def on_update_after_submit(self):
		self.validate_no_pkg_in_container()
		consignee_ain_no=frappe.db.get_value("Customer",self.consignee,"custom_ain_no")
		if not consignee_ain_no:
			frappe.throw(f"Set Ain No in Customer -({self.consignee})")
		hbl_docs = frappe.get_all("Import Sea House Bill", filters={"mbl_link": self.name,"docstatus":1},pluck="name")
		for hbl_name in hbl_docs:
			hbl_doc = frappe.get_doc("Import Sea House Bill", hbl_name)
			hbl_doc.mbl_no= self.mbl_no if self.mbl_no else hbl_doc.mbl_no
			hbl_doc.mv= self.mv if self.mv else hbl_doc.mv
			hbl_doc.port_of_loading= self.port_of_loading if self.port_of_loading else hbl_doc.port_of_loading
			hbl_doc.fv= self.fv if self.fv else hbl_doc.fv
			hbl_doc.mbl_date= self.mbl_date if self.mbl_date else hbl_doc.mbl_date
			hbl_doc.mv_voyage_no= self.mv_voyage_no if self.mv_voyage_no else hbl_doc.mv_voyage_no
			hbl_doc.port_of_discharge= self.port_of_discharge if self.port_of_discharge else hbl_doc.port_of_discharge
			hbl_doc.fv__v_no= self.fv_voyage_no if self.fv_voyage_no else hbl_doc.fv__v_no
			hbl_doc.agent=self.agent if self.agent else hbl_doc.agent
			hbl_doc.shipping_line=self.shipping_line if self.shipping_line else hbl_doc.shipping_line
			hbl_doc.carrier=self.consignee if self.consignee else hbl_doc.carrier
			hbl_doc.port_of_delivery=self.port_of_delivery if self.port_of_delivery else hbl_doc.port_of_delivery
			hbl_doc.fv_etd=self.fv_etd if self.fv_etd else hbl_doc.fv_etd
			hbl_doc.save()
		
	def on_update(self):
		consignee_ain_no=frappe.db.get_value("Customer",self.consignee,"custom_ain_no")
		if not consignee_ain_no:
			frappe.throw(f"Set Ain No in Customer -({self.consignee})")
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
