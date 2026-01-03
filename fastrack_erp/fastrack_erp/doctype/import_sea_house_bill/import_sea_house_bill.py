# Copyright (c) 2025, Shaid Azmin and contributors
# For license information, please see license.txt
import random
import frappe
from frappe.model.document import Document
#  "payment_link",
#   "customer",
#   "invoice",
#   "amount"
class ImportSeaHouseBill(Document):
      
	def onload(self):
		self.hbl_data=self.name
		
		invoice_list = self.get_invoice_list()
		gl_entry_list = get_gl_entry_from_invoice(invoice_list)
		payment_entry=[]
		for idx, gl_entry in enumerate(gl_entry_list):
			payment_entry_doc = frappe.new_doc("Fastrack Payment Entry")
			payment_entry_doc.idx = idx + 1
			payment_entry_doc.payment_link = gl_entry.voucher_no
			payment_entry_doc.customer = gl_entry.party
			payment_entry_doc.invoice = gl_entry.against_voucher
			payment_entry_doc.amount = gl_entry.credit_in_account_currency
			payment_entry_doc.parent = self.name
			payment_entry_doc.parenttype = "Import Sea House Bill"
			payment_entry_doc.parentfield = "payment_entry_list"
			payment_entry.append(payment_entry_doc)
		self.payment_entry_list = payment_entry
		self.total_payment = sum(float(item.amount) for item in payment_entry)
		draft_list=get_draft_sales_and_purchase_invoice_list(self.name)
		draft_invoice_list=[]
		for item in draft_list:
			draft_invoice=frappe.new_doc("Fastrack Draft Bill")
			draft_invoice.type=item["type"]
			draft_invoice.invoice_id=item["id"]
			draft_invoice.amount=item["amount"]
			draft_invoice.parent=self.name
			draft_invoice.parenttype="Import Sea House Bill"
			draft_invoice.parentfield="draft_invoice_list"
			draft_invoice_list.append(draft_invoice)
		self.draft_invoice_list = draft_invoice_list

	def before_save(self):
    #  need 10 digit uuid
		generate_uuid = str(random.randint(10**9, 10**10 - 1))
		if not self.invoice_uid:
			generate_uuid = str(random.randint(10**9, 10**10 - 1))
		self.invoice_uid=f"INV-{generate_uuid}"
		total_price = 0
		total_qty = 0

		for row in self.container_cost_info:
			total_price += (row.qty or 0) * (row.amount or 0)
			total_qty += row.qty or 0
		self.total = total_price
		self.average_total = (total_price / total_qty) if total_qty else 0

		# Validate container count
		self.validate_container_count()

	def on_update(self):
		total_price = 0
		total_qty = 0

		for row in self.container_cost_info:
			total_price += (row.qty or 0) * (row.amount or 0)
			total_qty += row.qty or 0

		self.total = total_price
		self.average_total = (total_price / total_qty) if total_qty else 0
		self.validate_container_count()
		self.validate_container_name()
		self.validate_container_weight()
		self.validate_no_pkg_in_container()
		self.hbl_weight= sum(item.weight for item in self.container_info)
		self.gross_weight= self.hbl_weight		
	def on_update_after_submit(self):
		self.validate_no_pkg_in_container()
		total_price = 0
		total_qty = 0

		for row in self.container_cost_info:
			total_price += (row.qty or 0) * (row.amount or 0)
			total_qty += row.qty or 0
		self.total = total_price
		self.average_total = (total_price / total_qty) if total_qty else 0

  
		
	def validate_container_name(self):
		
		mbl_doc = frappe.get_doc('Import Sea Master Bill', self.mbl_link)
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
		master_bill_no = self.mbl_link
		for item in self.container_info:
			get_master_item = get_single_fastrack_item_by_bill_no([master_bill_no], item.custom_container_no)
			get_existing_house_doc_id = frappe.db.get_list('Import Sea House Bill', {'mbl_link': master_bill_no,'docstatus': 1}, ['name'])
			get_existing_house_doc_id = [doc['name'] for doc in get_existing_house_doc_id]
			# If this is a new document, exclude it from the existing house bills list
			if self.name in get_existing_house_doc_id:
				get_existing_house_doc_id.remove(self.name)
			
			get_house_item = get_single_fastrack_item_by_bill_no(get_existing_house_doc_id, item.custom_container_no, parent_type='Import Sea House Bill')
			master_seal_no = get_master_item['seal_no']
			house_seal_no = item.seal_no
			if master_seal_no != house_seal_no:
				frappe.throw(f"Seal number mismatch for container: {item.custom_container_no}")
			house_item_weight = get_house_item['weight'] or 0.0
			master_item_weight = get_master_item['weight'] or 0.0
			item_weight = item.weight or 0.0
			if master_item_weight < house_item_weight + item_weight :
				frappe.throw(f"Weight mismatch for container: {item.custom_container_no}, should be less than or equal to {get_master_item['weight']}")
			house_item_no_of_pkg = get_house_item['no_of_pkg'] or 0.0
			print(get_house_item)
			master_item_no_of_pkg = get_master_item['no_of_pkg'] or 0.0
			item_no_of_pkg = item.no_of_pkg or 0.0
			if master_item_no_of_pkg < house_item_no_of_pkg + item_no_of_pkg:
				frappe.throw(f"Number of package mismatch for container: {item.custom_container_no}, should be less than or equal to {get_master_item['no_of_pkg']}")
    
	def get_invoice_list(self):
		return [invoice.invoice_link for invoice in self.invoice_list if invoice.invoice_link]
	def validate_no_pkg_in_container(self):
		total_no_of_pkg = sum(item.no_of_pkg for item in self.container_info)
		if total_no_of_pkg != self.no_of_pkg_hbl:
			frappe.throw(f"Total number of package in container does not match with total package in house bill")

	def validate_container_count(self):
		"""Validate that container_info rows don't exceed total_container_hbl"""
		total_containers = self.total_container_hbl or 0
		actual_containers = len(self.container_info) if self.container_info else 0

		if actual_containers > total_containers:
			frappe.throw(
				f"Cannot add more than {total_containers} container(s). "
				f"You currently have {actual_containers} containers. "
				f"Please update 'Total Container HBL' field to add more containers."
			)


@frappe.whitelist()
def get_single_fastrack_item_by_bill_no(bill_no, item_name, parent_type='Import Sea Master Bill'):
	if not bill_no:  # Handle empty list case
		return {
			"item_name": item_name,
			"seal_no": "",
			"weight": 0.0,
			"no_of_pkg": 0.0,

		}
	table_name = 'tabFastrack Item'
	item_column='container_no'
	if parent_type == 'Import Sea House Bill':
		table_name = 'tabFastrack Sea Item'
		item_column='custom_container_no'
	elif parent_type == 'Import Sea Master Bill':
		table_name = 'tabFastrack Item'
		item_column='container_no'
		
	# Ensure bill_no is a list of strings and join them properly into a string
	bill_no_placeholder = ', '.join([f"'{doc}'" for doc in bill_no])

	# Build the query with properly formatted bill_no
	result = frappe.db.sql(f"""
		SELECT 
			{item_column} as item_name,
			seal_no as seal_no,
			SUM(weight) as weight,
			SUM(no_of_pkg) as no_of_pkg
		FROM `{table_name}`
		WHERE parenttype = '{parent_type}'
		AND parent IN ({bill_no_placeholder})
		AND {item_column} = '{item_name}'
		AND docstatus = 1
		GROUP BY {item_column}
	""", as_dict=True)
	print(result)
	if len(result) > 0:
		print(result[0])
		return result[0]
	else:
		return {
			"item_name": item_name,
			"weight": 0.0,
			"seal_no": "",
			"no_of_pkg": 0.0
		}



@frappe.whitelist()
def get_gl_entry_from_invoice(invoice_list):
    default_receivable_account = frappe.get_all("Company",["default_receivable_account",'name'])
    bank_account = default_receivable_account[0].default_receivable_account
    default_company = default_receivable_account[0].name
    gl_entry_list = frappe.db.get_list("GL Entry",
                                       filters=[["company","=",default_company],["account","=",bank_account],["voucher_type","=","Payment Entry"],["against_voucher_type","=","Sales Invoice"],["against_voucher","in",invoice_list],
                                                ["credit_in_account_currency",">",0],["docstatus","=",1]],
                                       fields=["name",'credit_in_account_currency','party','voucher_no',"against_voucher"]
                                       )
    return gl_entry_list
    
    
    
@frappe.whitelist()
def get_draft_sales_and_purchase_invoice_list(house_bill_no):
    """
    Fixed version that properly handles document objects
    """
    invoice_list = []
    
    try:
        # Get sales invoices
        sales_invoice_list = frappe.db.get_list(
            "Sales Invoice",
            filters=[
                ["custom_hbl_sea_link", "=", house_bill_no],
                ["docstatus", "=", 0]
            ],
            fields=["name","base_grand_total"]
        )
        
        # Get purchase invoices  
        purchase_invoice_list = frappe.db.get_list(
            "Purchase Invoice",
            filters=[
                ["custom_shbl_id", "=", house_bill_no],
                ["docstatus", "=", 0]
            ],
            fields=["name","base_grand_total"]
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
