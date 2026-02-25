frappe.ui.form.on("Sales Invoice", {
	custom_total_freight_charge: function (frm) {
		calculate_freight(frm);
	},
	custom_freight_percentage: function (frm) {
		calculate_freight(frm);
	},
});

function calculate_freight(frm) {
	var total = flt(frm.doc.custom_total_freight_charge) || 0;
	var pct = flt(frm.doc.custom_freight_percentage) || 0;

	if (!total || !pct) {
		frm.set_value("custom_service_commission", 0);
		frm.set_value("custom_vat", 0);
		frm.set_value("custom_freight_charge", 0);
		return;
	}

	// Service Commission = (Total Freight Charge / (100 + Percentage) * Percentage) / 115 * 100
	var service_commission = ((total / (100 + pct)) * pct) / 115 * 100;

	// VAT = Service Commission * 15%
	var vat = service_commission * 0.15;

	// Freight Charge = Total Freight Charge - Service Commission - VAT
	var freight_charge = total - service_commission - vat;

	frm.set_value("custom_service_commission", flt(service_commission, 2));
	frm.set_value("custom_vat", flt(vat, 2));
	frm.set_value("custom_freight_charge", flt(freight_charge, 2));
}
