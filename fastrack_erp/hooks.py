app_name = "fastrack_erp"
app_title = "Fastrack Erp"
app_publisher = "Shaid Azmin"
app_description = "Erp For Fastrack"
app_email = "azmin@excelbd.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/fastrack_erp/css/fastrack_erp.css"
# app_include_js = "/assets/fastrack_erp/js/fastrack_erp.js"

# include js, css files in header of web template
# web_include_css = "/assets/fastrack_erp/css/fastrack_erp.css"
# web_include_js = "/assets/fastrack_erp/js/fastrack_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "fastrack_erp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "fastrack_erp.utils.jinja_methods",
# 	"filters": "fastrack_erp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "fastrack_erp.install.before_install"
# after_install = "fastrack_erp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "fastrack_erp.uninstall.before_uninstall"
# after_uninstall = "fastrack_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "fastrack_erp.utils.before_app_install"
# after_app_install = "fastrack_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "fastrack_erp.utils.before_app_uninstall"
# after_app_uninstall = "fastrack_erp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fastrack_erp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Import Sea Master Bill": {
		"on_update": "fastrack_erp.doc_events.mbl.validate",
		"on_update_after_submit": "fastrack_erp.doc_events.mbl.validate",
	},
 "Import Sea House Bill": {
	"on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
	"before_cancel": "fastrack_erp.doc_events.mbl.delete_child_hbl_on_cancel",
 },
 "Import Air Master Bill": {
	"on_update": "fastrack_erp.doc_events.mbl.validate",
 },
 "Import Air House Bill": {
	"on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
 },
 "Sales Invoice": {
	"on_submit": "fastrack_erp.doc_events.sales_invoice.after_submit",
	"before_cancel": "fastrack_erp.doc_events.sales_invoice.on_cancel",
 },
 "Purchase Invoice": {
	"on_submit": "fastrack_erp.doc_events.purchase_invoice.after_submit",
	"before_cancel": "fastrack_erp.doc_events.purchase_invoice.on_cancel",
 },
 "Journal Entry": {
	"on_submit": "fastrack_erp.doc_events.journal_entry.after_submit",
	"before_cancel": "fastrack_erp.doc_events.journal_entry.on_cancel",
 },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"fastrack_erp.tasks.all"
# 	],
# 	"daily": [
# 		"fastrack_erp.tasks.daily"
# 	],
# 	"hourly": [
# 		"fastrack_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"fastrack_erp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"fastrack_erp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "fastrack_erp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "fastrack_erp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "fastrack_erp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["fastrack_erp.utils.before_request"]
# after_request = ["fastrack_erp.utils.after_request"]

# Job Events
# ----------
# before_job = ["fastrack_erp.utils.before_job"]
# after_job = ["fastrack_erp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"fastrack_erp.auth.validate"
# ]
fixtures = [
	{
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                  "Sales Invoice-custom_hbl_sea_link",
                  "Sales Invoice-custom_hbl_type",
                  "Sales Invoice-custom_hbl_air_link",
                  "Customer-custom_customer_type",
                  "Customer-custom_bin_no",
                  "Customer-custom_ain_no",
                  "Customer-custom_customer_type",
                  "Journal Entry-custom_hbl_type",
                  "Journal Entry-custom_shbl_id",
                  "Purchase Invoice-custom_hbl_type",
                  "Purchase Invoice-custom_shbl_id",
                  "Payment Entry-custom_on_behalf_of_customer",
                  "Purchase Invoice Item-custom_exchange_rate",
                  "Supplier-custom_ain_no",
                  "Supplier-custom_bin_no",
                  "Payment Entry Reference-custom_hbl_type",
                  "Payment Entry Reference-custom_hbl_no"
                 
                ],
            ],
        ]
    },
    {
        "dt":"Property Setter",
        "filters":[
            [
                "name",
                "in",
                [
                    "Customer-main-field_order",
                    "Customer-account_manager-hidden",
                    "Customer-main-quick_entry",
                    "Customer-opportunity_name-hidden",
                    "Customer-lead_name-hidden",
                    "Sales Invoice-main-field_order"
                    
                ]
            ]
        ]
    },
]
website_route_rules = [{'from_route': '/portal/<path:app_path>', 'to_route': 'portal'},]