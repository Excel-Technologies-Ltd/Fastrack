import frappe
from fastrack_erp.patches.rebuild_hbl_derived_tables import execute as _execute

def execute():
    """
    Re-run the rebuild script to update HBL derived tables from existing documents
    that were manually updated after submission, prior to the on_update_after_submit
    hooks being introduced.
    """
    _execute()
