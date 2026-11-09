import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions
from frappe.utils import cint, flt, getdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    for field in ("company", "from_date", "to_date"):
        if not filters.get(field):
            frappe.throw(_("Company, From Date and To Date are required"))
    if getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be after To Date"))
    frappe.has_permission("Company", doc=filters.company, throw=True)
    frappe.has_permission("GL Entry", "read", throw=True)
    currency = frappe.get_cached_value("Company", filters.company, "default_currency")
    columns = [dict(label=_("Account Name"), fieldname="account", fieldtype="Link", options="Account", width=340)]
    columns += [dict(label=_(label), fieldname=label.lower(), fieldtype="Currency", options="currency", width=160)
                for label in ("Opening", "Debit", "Credit", "Balance")]

    # Permission-filtered posting accounts under the Asset and Liability roots.
    accounts = frappe.get_list("Account", filters={"company": filters.company,
        "root_type": ["in", ["Asset", "Liability"]]},
        fields=["name", "lft", "rgt", "is_group", "account_type", "root_type"],
        order_by="lft", limit_page_length=0)
    selected = filters.get("account") or []
    if isinstance(selected, str):
        selected = frappe.parse_json(selected)
    if not isinstance(selected, list):
        frappe.throw(_("Accounts must be a list"))
    by_name = {a.name: a for a in accounts}
    if any(name not in by_name for name in selected):
        frappe.throw(_("Select accessible Asset or Liability accounts from the selected company"))
    if filters.get("root_type") and filters.root_type not in ("Asset", "Liability"):
        frappe.throw(_("Invalid account root type"))
    if filters.get("account_type") and filters.account_type not in ("Bank", "Cash"):
        frappe.throw(_("Invalid account type"))
    ranges = [by_name[name] for name in selected]
    type_ranges = [a for a in accounts if a.account_type == filters.get("account_type")]
    accounts = [a for a in accounts if not a.is_group
        and (not ranges or any(p.lft <= a.lft <= p.rgt for p in ranges))
        and (not filters.get("root_type") or a.root_type == filters.root_type)
        and (not filters.get("account_type") or any(p.lft <= a.lft <= p.rgt for p in type_ranges))]
    if not accounts:
        return columns, []

    params = dict(filters, accounts=[a.name for a in accounts])
    conditions = []
    for field, doctype in (("cost_center", "Cost Center"), ("project", "Project")):
        if filters.get(field):
            doc = frappe.get_doc(doctype, filters[field])
            doc.check_permission("read")
            if doc.company != filters.company:
                frappe.throw(_("{0} must belong to the selected company").format(_(doctype)))
            if field == "cost_center":
                params.update(cc_lft=doc.lft, cc_rgt=doc.rgt)
                conditions.append("cost_center IN (SELECT name FROM `tabCost Center` WHERE company=%(company)s AND lft >= %(cc_lft)s AND rgt <= %(cc_rgt)s)")
            else:
                conditions.append("project = %(project)s")
    match = build_match_conditions("GL Entry")
    if match:
        conditions.append(match)
    extra = " AND " + " AND ".join(conditions) if conditions else ""
    # Opening vouchers through To Date belong to Opening, never period turnover.
    amounts = frappe.db.sql("""
        SELECT account,
            SUM(CASE WHEN posting_date < %(from_date)s OR is_opening = 'Yes'
                THEN debit - credit ELSE 0 END) AS opening,
            SUM(CASE WHEN posting_date >= %(from_date)s AND COALESCE(is_opening, 'No') != 'Yes'
                THEN debit ELSE 0 END) AS debit,
            SUM(CASE WHEN posting_date >= %(from_date)s AND COALESCE(is_opening, 'No') != 'Yes'
                THEN credit ELSE 0 END) AS credit
        FROM `tabGL Entry`
        WHERE company = %(company)s AND account IN %(accounts)s
            AND posting_date <= %(to_date)s AND is_cancelled = 0
    """ + extra + " GROUP BY account", params, as_dict=True)
    amounts = {r.account: r for r in amounts}
    precision = cint(frappe.db.get_default("currency_precision")) or 2
    data = []
    for account in accounts:
        values = amounts.get(account.name, {})
        row = dict(account=account.name, currency=currency)
        for field in ("opening", "debit", "credit"):
            row[field] = flt(values.get(field), precision)
        row["balance"] = flt(row["opening"] + row["debit"] - row["credit"], precision)
        if cint(filters.get("show_zero_balances")) or any(row[f] for f in ("opening", "debit", "credit", "balance")):
            data.append(row)
    return columns, data, _("Amounts are in {0}. Opening includes earlier entries and opening vouchers through To Date. Negative balances are credit balances.").format(currency)
