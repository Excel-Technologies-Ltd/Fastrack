"""
Resolve HBL `invoice_list` rows from linked Sales Invoices when the child
table on the HBL is empty (common for Export flows where SI links via
custom_*_link fields only).
"""

import frappe

_PARENT_DOCTYPE_TO_SI_LINK = {
    'Import Sea House Bill': 'custom_hbl_sea_link',
    'Import Air House Bill': 'custom_hbl_air_link',
    'Import D2D Bill': 'custom_import_d2d_link',
    'Export Sea House Bill': 'custom_export_hbl_sea_link',
    'Export Air House Bill': 'custom_export_hbl_air_link',
    'Export D2D Bill': 'custom_export_d2d_link',
}


def _si_link_field(parent_doctype):
    return _PARENT_DOCTYPE_TO_SI_LINK.get(parent_doctype)


def _row_to_portal_dict(row):
    """Child rows may be dict-like, Document rows, or frappe._dict; as_dict is not always callable."""
    if row is None:
        return {
            'name': None,
            'invoice_link': None,
            'customer': None,
            'item_code': None,
            'qty': None,
        }
    if isinstance(row, dict):
        d = dict(row)
    else:
        as_dict_fn = getattr(row, 'as_dict', None)
        if callable(as_dict_fn):
            d = as_dict_fn()
        else:
            try:
                d = dict(row)
            except (TypeError, ValueError):
                d = {}
    return {
        'name': d.get('name'),
        'invoice_link': d.get('invoice_link'),
        'customer': d.get('customer'),
        'item_code': d.get('item_code'),
        'qty': d.get('qty'),
    }


def _child_row_links_sales_invoice(row):
    """True if HBL invoice_list row actually references a Sales Invoice."""
    if row is None:
        return False
    if isinstance(row, dict):
        link = row.get('invoice_link')
    else:
        link = getattr(row, 'invoice_link', None)
    return bool(link and str(link).strip())


def portal_invoice_line_payload(parent_doctype, hbl_name):
    """
    Return serializable invoice line rows for the portal PDF picker.
    Uses child table rows when present; otherwise linked Sales Invoices.
    """
    if not parent_doctype or not hbl_name:
        return []
    frappe.has_permission(parent_doctype, ptype='read', doc=hbl_name, throw=True)
    doc = frappe.get_doc(parent_doctype, hbl_name)
    existing = list(doc.get('invoice_list') or [])
    linked_rows = [r for r in existing if r is not None and _child_row_links_sales_invoice(r)]
    if linked_rows:
        return [_row_to_portal_dict(r) for r in linked_rows]
    resolve_invoice_list_for_hbl_pdf(doc, parent_doctype, None)
    return [
        _row_to_portal_dict(r)
        for r in (doc.invoice_list or [])
        if r is not None
    ]


def _hbl_link_targets(parent_doctype, hbl_key):
    """Values that may appear in Sales Invoice link field (name vs hbl_id)."""
    vals = {hbl_key}
    if frappe.db.exists(parent_doctype, hbl_key):
        hid = frappe.db.get_value(parent_doctype, hbl_key, 'hbl_id')
        if hid:
            vals.add(hid)
    name_by_hid = frappe.db.get_value(
        parent_doctype,
        {'hbl_id': hbl_key},
        'name',
    )
    if name_by_hid:
        vals.add(name_by_hid)
    return [x for x in vals if x]


def _synthetic_row_from_si_name(si_name):
    """Build one invoice_list row using DB only (no SI Doc read permission)."""
    head = frappe.db.get_value(
        'Sales Invoice',
        si_name,
        ['customer', 'grand_total', 'currency'],
        as_dict=True,
    )
    if not head:
        return None
    items = frappe.db.get_all(
        'Sales Invoice Item',
        filters={'parent': si_name},
        fields=['item_code', 'qty', 'rate'],
        order_by='idx asc',
        limit_page_length=1,
    )
    if not items:
        return frappe._dict(
            name=si_name,
            customer=head.get('customer'),
            invoice_link=si_name,
            item_code='',
            qty='',
            rate=0,
            total_price=float(head.get('grand_total') or 0),
            currency=head.get('currency') or '',
        )
    first = items[0]
    return frappe._dict(
        name=si_name,
        customer=head.get('customer'),
        invoice_link=si_name,
        item_code=first.get('item_code'),
        qty=first.get('qty'),
        rate=float(first.get('rate') or 0),
        total_price=float(head.get('grand_total') or 0),
        currency=head.get('currency') or '',
    )


def _synthetic_rows_from_sales_invoices(
    parent_doctype,
    hbl_name,
    link_field,
    si_names,
):
    """Resolve SI names; query per link value (OR in SQL is fragile across versions)."""
    link_targets = _hbl_link_targets(parent_doctype, hbl_name)
    seen = set()
    names = []
    for tval in link_targets:
        fl = [['docstatus', '=', 1], [link_field, '=', tval]]
        if si_names:
            fl = fl + [['name', 'in', list(si_names)]]
        batch = frappe.db.get_all(
            'Sales Invoice',
            filters=fl,
            fields=['name'],
            order_by='posting_date desc, name desc',
            limit_page_length=200,
        )
        for r in batch:
            n = r.get('name')
            if n and n not in seen:
                seen.add(n)
                names.append(n)
    if not names:
        return []

    rows = []
    for si_name in names:
        row = _synthetic_row_from_si_name(si_name)
        if row:
            rows.append(row)
    return rows


def resolve_invoice_list_for_hbl_pdf(doc, parent_doctype, invoice_ids):
    """
    Set doc.invoice_list for PDF: prefer matching child rows; else linked SIs.
    invoice_ids: comma-separated child `name` or Sales Invoice `name`.
    """
    link_field = _si_link_field(parent_doctype)
    existing = list(doc.get('invoice_list') or [])
    ids = [s.strip() for s in (invoice_ids or '').split(',') if s.strip()]

    if ids:
        by_child = [r for r in existing if r.name in ids]
        if by_child:
            doc.invoice_list = by_child
            return
        if link_field:
            doc.invoice_list = _synthetic_rows_from_sales_invoices(
                parent_doctype,
                doc.name,
                link_field,
                ids,
            )
            return
        doc.invoice_list = []
        return

    if existing:
        linked_only = [r for r in existing if _child_row_links_sales_invoice(r)]
        if linked_only:
            doc.invoice_list = linked_only
            return

    if link_field:
        doc.invoice_list = _synthetic_rows_from_sales_invoices(
            parent_doctype,
            doc.name,
            link_field,
            None,
        )
        return

    doc.invoice_list = []
