"""
Shipping details HTML helpers — one function per report type.
"""

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
