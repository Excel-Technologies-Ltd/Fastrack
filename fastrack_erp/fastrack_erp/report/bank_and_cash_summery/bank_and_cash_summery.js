frappe.query_reports["Bank and Cash Summery"] = {
    filters: [
        {
            fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company",
            default: frappe.defaults.get_user_default("Company"), reqd: 1,
            on_change() {
                frappe.query_report.set_filter_value({account: [], cost_center: "", project: ""});
            }
        },
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
            default: frappe.datetime.month_start(), reqd: 1},
        {fieldname: "to_date", label: __("To Date"), fieldtype: "Date",
            default: frappe.datetime.get_today(), reqd: 1},
        {
            fieldname: "account", label: __("Accounts"),
            fieldtype: "MultiSelectList", options: "Account",
            get_data(txt) {
                return frappe.db.get_link_options("Account", txt, {
                    company: frappe.query_report.get_filter_value("company"),
                    root_type: ["in", ["Asset", "Liability"]]
                });
            }
        },
        {fieldname: "root_type", label: __("Account Root"), fieldtype: "Select",
            options: ["", "Asset", "Liability"]},
        {fieldname: "account_type", label: __("Account Type"), fieldtype: "Select",
            options: ["", "Bank", "Cash"]},
        {
            fieldname: "cost_center", label: __("Cost Center"), fieldtype: "Link", options: "Cost Center",
            get_query() { return {filters: {company: frappe.query_report.get_filter_value("company")}}; }
        },
        {
            fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project",
            get_query() { return {filters: {company: frappe.query_report.get_filter_value("company")}}; }
        },
        {fieldname: "show_zero_balances", label: __("Show Zero Balances"), fieldtype: "Check", default: 0}
    ]
};
