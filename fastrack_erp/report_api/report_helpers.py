"""
Shipping details HTML helpers — one function per report type.
"""

import os

import frappe

_LBL  = "font-weight:bold; padding:3px 6px; vertical-align:top; white-space:nowrap; text-align:left;"
_VAL  = "padding:3px 6px; vertical-align:top; text-align:left;"
_RLBL = "font-weight:bold; padding:3px 6px 3px 18px; vertical-align:top; white-space:nowrap; text-align:left;"


def _make_helpers(doc, format_date_fn=None):
    def _d(field):
        val = doc.get(field)
        return '' if val is None or val == '' else str(val)

    def _date(field, fmt='dd-MMM-yyyy'):
        val = _d(field)
        if format_date_fn and val:
            try:
                return format_date_fn(val, fmt)
            except Exception:
                return val
        return val

    return _d, _date


def _row(l1, v1, l2='', v2=''):
    if not l2:
        return f"""
        <tr>
            <td style="{_LBL}">{l1}</td>
            <td colspan="3" style="{_VAL}">: {v1}</td>
        </tr>"""
    return f"""
        <tr>
            <td style="{_LBL}">{l1}</td>
            <td style="{_VAL}">: {v1}</td>
            <td style="{_RLBL}">{l2}</td>
            <td style="{_VAL}">: {v2}</td>
        </tr>"""


# def _wrap_table(rows_html):
#     return f"""
#     <table style="width:100%; border-collapse:collapse; font-size:12px; table-layout:fixed;">
#         <colgroup>
#             <col style="width:22%">
#             <col style="width:28%">
#             <col style="width:22%">
#             <col style="width:28%">
#         </colgroup>
#         {rows_html}
#     </table>"""

def _wrap_table(rows):
    """Wraps the rows in a 100% width table"""
    return f"""
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px;">
            <tbody>
                {rows}
            </tbody>
        </table>
    """


def normalize_doc_for_invoice_shipping(doc):
    """Map air/d2d HBL fields onto sea-style names for invoice shipping HTML."""
    d = dict(doc.as_dict())
    dt = d.get('doctype') or getattr(doc, 'doctype', None) or ''
    if dt == 'Import Air House Bill':
        d['hbl_consignee'] = d.get('hbl_consignee') or d.get('consignee')
        d['hbl_shipper'] = d.get('hbl_shipper') or d.get('shipper')
        d['notify_to'] = d.get('notify_to') or d.get('notify_party')
        d['hbl_id'] = d.get('hbl_id') or d.get('hbl_no') or d.get('hawb_no')
        if d.get('no_of_pkg_hbl') is None:
            d['no_of_pkg_hbl'] = d.get('no_of_pkg')
        d['hbl_weight'] = d.get('hbl_weight') or d.get('hbl_gr_weight')
        d['mv'] = d.get('mv') or d.get('flight_name')
        d['shipping_line'] = d.get('shipping_line') or d.get('airlines')
        d['port_of_discharge'] = (
            d.get('port_of_discharge') or d.get('port_of_delivery')
        )
        d['hbl_etd'] = d.get('hbl_etd') or d.get('flight_date')
        d['eta'] = d.get('eta') or d.get('arrival_date')
        d['mv_voyage_no'] = d.get('mv_voyage_no') or ''
        d['fv'] = d.get('fv') or ''
        d['fv__v_no'] = d.get('fv__v_no') or ''
        d['hbl_vol_cbm'] = d.get('hbl_vol_cbm') or ''
        d['lc'] = d.get('lc') or d.get('lc_number')
        d['total_container_hbl'] = d.get('total_container_hbl') or 0
        d['custom_shipment_mode'] = d.get('custom_shipment_mode') or ''
        d['description_of_good'] = (
            d.get('description_of_good') or d.get('cargo_description')
        )
    elif dt in ('Import D2D Bill', 'Export D2D Bill'):
        d['hbl_consignee'] = d.get('hbl_consignee') or d.get('consignee')
        d['hbl_shipper'] = d.get('hbl_shipper') or d.get('shipper')
        d['notify_to'] = d.get('notify_to') or d.get('notify_party')
        d['hbl_id'] = d.get('hbl_id') or d.get('hbl_no')
        if d.get('no_of_pkg_hbl') is None:
            d['no_of_pkg_hbl'] = d.get('no_of_pkg')
        d['hbl_weight'] = d.get('hbl_weight') or d.get('gr_weight')
        d['hbl_etd'] = d.get('hbl_etd') or d.get('etd')
        d['port_of_discharge'] = (
            d.get('port_of_discharge') or d.get('port_of_delivery')
        )
        d['mv'] = d.get('mv') or ''
        d['mv_voyage_no'] = d.get('mv_voyage_no') or ''
        d['fv'] = d.get('fv') or ''
        d['fv__v_no'] = d.get('fv__v_no') or ''
        d['hbl_vol_cbm'] = d.get('hbl_vol_cbm') or ''
        d['lc'] = d.get('lc') or d.get('lc_number')
        d['shipping_line'] = d.get('shipping_line') or ''
        d['total_container_hbl'] = d.get('total_container_hbl') or 0
        d['custom_shipment_mode'] = d.get('custom_shipment_mode') or ''
        d['description_of_good'] = (
            d.get('description_of_good') or d.get('cargo_description')
        )
    return frappe._dict(d)


def get_arrival_notice_shipping_html(doc):
    """Complete shipping details section for Arrival Notice.

    Includes: Notify Party, Consignee, Shipper, all HBL/MBL/vessel fields,
    Total Container, and Goods Description.
    """
    _d, _date = _make_helpers(doc)

    lc          = _d('lc')
    lc_date     = _d('lc_date')
    lc_combined = f"{lc} &amp; {lc_date}" if (lc or lc_date) else ''

    rows = (
        _row('Notify Party',        _d('notify_to'))
        + _row('Consignee',         _d('hbl_consignee'))
        + _row('Shipper',           _d('hbl_shipper'))
        + _row('HBL No',            _d('hbl_id'),            'M/Vsl. Name',      _d('mv'))
        + _row('HBL Date',          _date('hbl_date'),        'Voyage',           _d('mv_voyage_no'))
        + _row('MBL No',            _d('mbl_no'),            'ETD',              _date('hbl_etd'))
        + _row('MBL Date',          _date('mbl_date'),        'ETA',              _date('eta'))
        + _row('L/C No. &amp; Date',lc_combined,             'F/Vsl. Name',      _d('fv'))
        + _row('Port of Loading',   _d('port_of_loading'),   'FV Voyage No',     _d('fv__v_no'))
        + _row('Port of Discharge', _d('port_of_discharge'), 'Inco Terms',       _d('inco_term'))
        + _row('Port of Delivery',  _d('port_of_delivery'),  'Volume CBM',       _d('hbl_vol_cbm'))
        + _row('Shipping Line',     _d('shipping_line'),     'Total (CTN/PKG)',  int(doc.get('no_of_pkg_hbl') or 0))
        + _row('Goods Description', _d('description_of_good'),'Total Container',   int(doc.get('total_container_hbl') or 0))
  
    )
    return _wrap_table(rows)


def get_invoice_usd_shipping_html(doc):
    """Shipping details section for Sea Import Invoice USD.

    Includes: Notify Party, Consignee, Shipper, all HBL/MBL/vessel fields,
    and Total Container. Shipment Mode / Weight / Goods Description are rendered
    separately in the invoice template.
    """
    doc = normalize_doc_for_invoice_shipping(doc)
    _d, _date = _make_helpers(doc)

    lc          = _d('lc')
    lc_date     = _d('lc_date')
    lc_combined = f"{lc} &amp; {lc_date}" if (lc or lc_date) else ''


    rows = (
        _row('Notify Party',        _d('notify_to'))
        + _row('Consignee',         _d('hbl_consignee'))
        + _row('Shipper',           _d('hbl_shipper'))
        + _row('HBL No',            _d('hbl_id'),            'M/Vsl. Name',      _d('mv'))
        + _row('HBL Date',          _date('hbl_date'),        'Voyage',           _d('mv_voyage_no'))
        + _row('MBL No',            _d('mbl_no'),            'ETD',              _date('hbl_etd'))
        + _row('MBL Date',          _date('mbl_date'),        'ETA',              _date('eta'))
        + _row('L/C No. &amp; Date',lc_combined,             'F/Vsl. Name',      _d('fv'))
        + _row('Port of Loading',   _d('port_of_loading'),   'FV Voyage No',     _d('fv__v_no'))
        + _row('Port of Discharge', _d('port_of_discharge'), 'Inco Terms',       _d('inco_term'))
        + _row('Port of Delivery',  _d('port_of_delivery'),  'Total Weight', (str(doc.get('hbl_weight') or 0))+' KG')
        + _row( 'Shipment Mode', (doc.get('custom_shipment_mode') or ""), 'Volume CBM',       _d('hbl_vol_cbm'))
        + _row('Shipping Line',     _d('shipping_line'),     'Total (CTN/PKG)',  int(doc.get('no_of_pkg_hbl') or 0))
        + _row( 'Goods Description', (doc.get('description_of_good') or '' ),  'Total Container',   int(doc.get('total_container_hbl') or 0) )
        
    )
    return _wrap_table(rows)


def get_invoice_bdt_shipping_html(doc, container_volume=''):
    """Shipping details section for Sea Import Invoice BDT.

    Includes BDT-specific layout: Consignee fixed as MODHUMOTI BANK LIMITED,
    Container Volume, Shipment Mode, and Goods Description inline.
    """
    doc = normalize_doc_for_invoice_shipping(doc)
    _d, _date = _make_helpers(doc)

    lc          = _d('lc')
    lc_date     = _d('lc_date')
    lc_combined = f"{lc} &amp; {lc_date}" if (lc or lc_date) else ''

    rows = (
        _row('Notify Party',        _d('notify_to'))
        + _row('Consignee',         _d('hbl_consignee'))
        + _row('Shipper',           _d('hbl_shipper'))
        + _row('HBL No',            _d('hbl_id'),            'M/Vsl. Name',      _d('mv'))
        + _row('HBL Date',          _date('hbl_date'),        'Voyage',           _d('mv_voyage_no'))
        + _row('MBL No',            _d('mbl_no'),            'ETD',              _date('hbl_etd'))
        + _row('MBL Date',          _date('mbl_date'),        'ETA',              _date('eta'))
        + _row('L/C No. &amp; Date',lc_combined,             'F/Vsl. Name',      _d('fv'))
        + _row('Port of Loading',   _d('port_of_loading'),   'FV Voyage No',     _d('fv__v_no'))
        + _row('Port of Discharge', _d('port_of_discharge'), 'Inco Terms',       _d('inco_term'))
        + _row('Port of Delivery',  _d('port_of_delivery'),  'Total Weight', (str(doc.get('hbl_weight') or 0))+' KG')
        + _row( 'Shipment Mode', (doc.get('custom_shipment_mode') or ""), 'Volume CBM',       _d('hbl_vol_cbm'))
        + _row('Shipping Line',     _d('shipping_line'),     'Total (CTN/PKG)',  int(doc.get('no_of_pkg_hbl') or 0))
        + _row( 'Goods Description', (doc.get('description_of_good') or '' ),  'Total Container',   int(doc.get('total_container_hbl') or 0) )
        
    )
    return _wrap_table(rows)


def get_fc_shipping_html(doc, format_date_fn=None):
    """Shipping details section for FC / To Whom It May Concern.

    Same layout as Invoice USD but with optional date formatting applied to
    HBL Date, HBL ETD, MBL Date, and ETA fields.
    """
    _d, _date = _make_helpers(doc, format_date_fn)

    lc          = _d('lc')
    lc_date     = _d('lc_date')
    lc_combined = f"{lc} &amp; {lc_date}" if (lc or lc_date) else ''

    rows = (
        _row('Notify Party',        _d('notify_to'))
        + _row('Consignee',         _d('hbl_consignee'))
        + _row('Shipper',           _d('hbl_shipper'))
        + _row('HBL No',            _d('hbl_id'),            'M/Vsl. Name',      _d('mv'))
        + _row('HBL Date',          _date('hbl_date'),        'Voyage',           _d('mv_voyage_no'))
        + _row('MBL No',            _d('mbl_no'),            'ETD',              _date('hbl_etd'))
        + _row('MBL Date',          _date('mbl_date'),        'ETA',              _date('eta'))
        + _row('L/C No. &amp; Date',lc_combined,             'F/Vsl. Name',      _d('fv'))
        + _row('Port of Loading',   _d('port_of_loading'),   'FV Voyage No',     _d('fv__v_no'))
        + _row('Port of Discharge', _d('port_of_discharge'), 'Inco Terms',       _d('inco_term'))
        + _row('Port of Delivery',  _d('port_of_delivery'),  'Volume CBM',       _d('hbl_vol_cbm'))
        + _row('Shipping Line',     _d('shipping_line'),     'Total (CTN/PKG)',  int(doc.get('no_of_pkg_hbl') or 0))
        + _row('Total Container',   int(doc.get('total_container_hbl') or 0))
    )
    return _wrap_table(rows)


# Legacy alias kept for any callers not yet updated.
def get_shipping_details_html(doc, format_date_fn=None):
    return get_fc_shipping_html(doc, format_date_fn)


# Minimal body CSS (optional). Do not use position:fixed for footers — wkhtmltopdf
# splits/scales them badly; use merge_fastrack_wkhtml_pdf_options() instead.
FASTTRACK_PDF_MAIN_CSS = """
.ft-pdf-main {
    box-sizing: border-box;
}
"""

# Standalone document for wkhtmltopdf --footer-html (avoids print.bundle.css).
FASTTRACK_WKHTML_FOOTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100%;
  }
  body {
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 8px !important;
    line-height: 1.15 !important;
    color: #000 !important;
    text-align: center;
  }
  p {
    margin: 0 0 0.35mm 0 !important;
    padding: 0 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 8px !important;
    line-height: 1.15 !important;
    font-weight: normal !important;
    white-space: nowrap !important;
  }
  p:last-child { margin-bottom: 0 !important; }
  strong {
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 8px !important;
    font-weight: bold !important;
  }
</style>
</head>
<body>
<p><strong>DHAKA OFFICE:</strong> HOUSE# 14(2nd Floor), ROAD# 13/C, BLOCK # E, BANANI, DHAKA -1213, BANGLADESH. Tel: +880-2-8836368, Fax: +880-2-8836374</p>
<p><strong>CHITTAGONG OFFICE:</strong> 259B/A, HARUN BHABON (1st Floor), BADAMTOLI, SK. MUJIB ROAD, AGRABAD C/A, CHITTAGONG. Tel: +880-31-2527634</p>
</body>
</html>
"""


def _write_fastrack_footer_html_path():
    path = os.path.join(
        '/tmp',
        'ft-pdf-footer-{0}.html'.format(frappe.generate_hash(length=10)),
    )
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(FASTTRACK_WKHTML_FOOTER_HTML)
    return path


def merge_fastrack_wkhtml_pdf_options(extra=None):
    """Native wkhtml footer (correct size, no page-split). Pass orientation etc. in extra."""
    opts = {
        'footer-html': _write_fastrack_footer_html_path(),
        'footer-spacing': '2',
        'margin-bottom': '18mm',
    }
    if extra:
        opts.update(extra)
    return opts
