"""
Shared HTML helpers for report PDFs.
"""


def get_shipping_details_html(doc, format_date_fn=None):
    """
    Return a properly aligned 2-column (4-cell) shipping details table.

    Layout per row:  Label (20%) | Value (30%) | Label (20%) | Value (30%)

    Pass `format_date_fn` (e.g. frappe.utils.format_date) to apply date
    formatting in reports that need it (e.g. import_to_concern).
    """

    def _d(field):
        val = doc.get(field)
        if val is None or val == '':
            return ''
        return str(val)

    def _date(field, fmt='dd-MMM-yyyy'):
        val = _d(field)
        if format_date_fn and val:
            try:
                return format_date_fn(val, fmt)
            except Exception:
                return val
        return val

    hbl_id          = _d('hbl_id')
    mv              = _d('mv')
    hbl_date        = _date('hbl_date')
    mv_voyage_no    = _d('mv_voyage_no')
    mbl_no          = _d('mbl_no')
    hbl_etd         = _date('hbl_etd')
    mbl_date        = _date('mbl_date')
    eta             = _date('eta')
    lc              = _d('lc')
    lc_date         = _d('lc_date')
    fv              = _d('fv')
    fv_v_no         = _d('fv__v_no')
    inco_term       = _d('inco_term')
    port_loading    = _d('port_of_loading')
    vol_cbm         = _d('hbl_vol_cbm')
    port_discharge  = _d('port_of_discharge')
    port_delivery   = _d('port_of_delivery')
    no_of_pkg       = int(doc.get('no_of_pkg_hbl') or 0)
    shipping_line   = _d('shipping_line')
    total_container = int(doc.get('total_container_hbl') or 0)

    lc_combined = f"{lc} &amp; {lc_date}" if lc or lc_date else ''

    # Cell styles
    _lbl  = "font-weight:bold; padding:3px 6px; vertical-align:top; white-space:nowrap;"
    _val  = "padding:3px 6px; vertical-align:top;"
    # Right-side label gets extra left padding to create a visible gap from left value
    _rlbl = "font-weight:bold; padding:3px 6px 3px 18px; vertical-align:top; white-space:nowrap;"

    def row(l1, v1, l2='', v2='', v1_colspan=False):
        """Build a 4-cell table row. If v1_colspan, value spans all 3 remaining cols."""
        if v1_colspan:
            return f"""
        <tr>
            <td style="{_lbl}">{l1}</td>
            <td colspan="3" style="{_val}">: {v1}</td>
        </tr>"""
        return f"""
        <tr>
            <td style="{_lbl}">{l1}</td>
            <td style="{_val}">: {v1}</td>
            <td style="{_rlbl}">{l2}</td>
            <td style="{_val}">{': ' + str(v2) if l2 else ''}</td>
        </tr>"""

    rows = (
        row('HBL No',              hbl_id,         'M/Vsl. Name',     mv)
        + row('HBL Date',          hbl_date,        'Voyage',          mv_voyage_no)
        + row('MBL No',            mbl_no,          'ETD',             hbl_etd)
        + row('MBL Date',          mbl_date,        'ETA',             eta)
        + row('L/C No.&amp; Date', lc_combined,     'F/Vsl. Name',     fv)
        + row('Port of Loading',   port_loading,    'FV Voyage No',      fv_v_no, )
        + row('Port of Discharge', port_discharge,  'Inco Terms',      inco_term)
        + row( 'Port of Delivery',  port_delivery,  'Volume CBM',     vol_cbm)
        + row( 'Shipping Line',     shipping_line,  'Total (CTN/PKG)', no_of_pkg) 
        + row( 'Total Container)', total_container) 
        
      
    )

    return f"""
    <table style="width:100%; border-collapse:collapse; font-size:12px; table-layout:fixed;">
        <colgroup>
            <col style="width:22%">
            <col style="width:28%">
            <col style="width:22%">
            <col style="width:28%">
        </colgroup>
        {rows}
    </table>"""
