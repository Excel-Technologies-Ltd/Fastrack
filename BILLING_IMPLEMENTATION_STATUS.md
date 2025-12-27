# Billing/Accounting Implementation Status

## Overview

Implementation of billing/accounting functionality (Sales Invoice, Purchase Invoice, Journal Entry, Payment Entry tracking) across all House Bill doctypes.

**Date**: December 26, 2025
**Status**: Partially Complete - Core infrastructure ready, individual doctypes need Python/JS updates

---

## ✅ COMPLETED

### 1. Core Infrastructure - Doc Events (100% Complete)

All document event handlers have been updated to work **generically** with all House Bill types:

#### **Sales Invoice Event Handler**
[`/apps/fastrack_erp/fastrack_erp/doc_events/sales_invoice.py`](apps/fastrack_erp/fastrack_erp/doc_events/sales_invoice.py)

- ✅ Dynamic HBL type detection using `custom_hbl_type` field
- ✅ Automatic link field mapping:
  - Import Sea House Bill → `custom_hbl_sea_link`
  - Import Air House Bill → `custom_hbl_air_link`
  - Import D2D Bill → `custom_hbl_d2d_link`
  - Export Sea House Bill → `custom_hbl_export_sea_link`
  - Export Air House Bill → `custom_hbl_export_air_link`
- ✅ `after_submit`: Adds invoice items to HBL's `invoice_list` child table
- ✅ `on_cancel`: Removes invoice items from HBL's `invoice_list`
- ✅ Updates `total_invoice_amount` on HBL

#### **Purchase Invoice Event Handler**
[`/apps/fastrack_erp/fastrack_erp/doc_events/purchase_invoice.py`](apps/fastrack_erp/fastrack_erp/doc_events/purchase_invoice.py)

- ✅ Dynamic HBL type detection
- ✅ Automatic link field mapping:
  - Import Sea House Bill → `custom_shbl_id`
  - Import Air House Bill → `custom_ahbl_id`
  - Import D2D Bill → `custom_dhbl_id`
  - Export Sea House Bill → `custom_eshbl_id`
  - Export Air House Bill → `custom_eahbl_id`
- ✅ `after_submit`: Adds purchase items to HBL's `purchase_invoice_list`
- ✅ `on_cancel`: Removes purchase items from HBL's `purchase_invoice_list`
- ✅ Updates `total_purchase_amount` on HBL

#### **Journal Entry Event Handler**
[`/apps/fastrack_erp/fastrack_erp/doc_events/journal_entry.py`](apps/fastrack_erp/fastrack_erp/doc_events/journal_entry.py)

- ✅ Dynamic HBL type detection
- ✅ Uses same link fields as Purchase Invoice
- ✅ `after_submit`: Adds journal accounts to HBL's `profit_share_list`
- ✅ `on_cancel`: Removes journal accounts from HBL's `profit_share_list`
- ✅ Updates `total_profit_share` on HBL
- ✅ Resolves party names (Customer/Supplier/Employee)

### 2. Core Infrastructure - API Methods (100% Complete)

All API methods have been updated to work **generically** with all House Bill types:

#### **API Methods**
[`/apps/fastrack_erp/fastrack_erp/api.py`](apps/fastrack_erp/fastrack_erp/api.py:140-209)

- ✅ `make_sales_invoice_from_hbl()` - Creates Sales Invoice from any HBL type
- ✅ `make_purchase_invoice_from_hbl()` - Creates Purchase Invoice from any HBL type
- ✅ `make_journal_entry_from_hbl()` - Creates Journal Entry from any HBL type
- ✅ Auto-detects HBL type using `frappe.db.exists()` check
- ✅ Maps fields dynamically based on HBL type
- ✅ Sets appropriate custom fields on target invoices

### 3. Import Air House Bill (100% Complete)

#### **Python Controller**
[`/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.py`](apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.py)

- ✅ `onload()` - Loads payment entries from GL Entry
- ✅ `onload()` - Loads draft invoices (Sales & Purchase)
- ✅ `get_invoice_list()` - Returns list of linked sales invoices
- ✅ `get_gl_entry_from_invoice()` - Fetches payment tracking data
- ✅ `get_draft_sales_and_purchase_invoice_list()` - Fetches draft invoices
  - Custom field filters: `custom_hbl_air_link`, `custom_ahbl_id`

#### **JavaScript Controller**
[`/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.js`](apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.js)

- ✅ Create buttons (visible after submit):
  - Sales Invoice
  - Expense (Purchase Invoice)
  - Profit Share
  - Payment Entry
- ✅ PDF Download buttons:
  - Expense PDF (multi-select dialog)
  - Profit Share PDF (multi-select dialog)
  - Sales Invoice PDF (multi-select dialog)
- ✅ All buttons call generic API methods

---

## ⏳ PENDING

### 4. Import D2D Bill (0% Complete)

**Required Changes:**

#### Python File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_d2d_bill/import_d2d_bill.py`

```python
# Add the following methods (copy from Import Air House Bill):

def onload(self):
    # Load payment entries and draft invoices
    # Change parenttype to "Import D2D Bill"
    # Change custom field filters to:
    #   - custom_hbl_d2d_link (for Sales Invoice)
    #   - custom_dhbl_id (for Purchase Invoice)

def get_invoice_list(self):
    # Return list of sales invoice links

# Add module-level functions:
def get_gl_entry_from_invoice(invoice_list):
    # Get payment entries from GL Entry

def get_draft_sales_and_purchase_invoice_list(house_bill_no):
    # Get draft Sales & Purchase Invoices
    # Filter by custom_hbl_d2d_link and custom_dhbl_id
```

#### JavaScript File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_d2d_bill/import_d2d_bill.js`

```javascript
// Copy entire content from import_air_house_bill.js
// Change 'Import Air House Bill' references to 'Import D2D Bill'
// No other changes needed - uses generic API methods
```

#### Custom Fields Required on Sales Invoice:
- `custom_hbl_d2d_link` (Link to Import D2D Bill)

#### Custom Fields Required on Purchase Invoice:
- `custom_dhbl_id` (Link to Import D2D Bill)

---

### 5. Export Sea House Bill (0% Complete)

**Required Changes:**

#### Python File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_sea_house_bill/export_sea_house_bill.py`

```python
# Add the following methods (copy from Import Air House Bill):

def onload(self):
    # Load payment entries and draft invoices
    # Change parenttype to "Export Sea House Bill"
    # Change custom field filters to:
    #   - custom_hbl_export_sea_link (for Sales Invoice)
    #   - custom_eshbl_id (for Purchase Invoice)

def get_invoice_list(self):
    # Return list of sales invoice links

# Add module-level functions:
def get_gl_entry_from_invoice(invoice_list):
    # Get payment entries from GL Entry

def get_draft_sales_and_purchase_invoice_list(house_bill_no):
    # Get draft Sales & Purchase Invoices
    # Filter by custom_hbl_export_sea_link and custom_eshbl_id
```

#### JavaScript File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_sea_house_bill/export_sea_house_bill.js`

```javascript
// Copy entire content from import_air_house_bill.js
// Change 'Import Air House Bill' references to 'Export Sea House Bill'
// No other changes needed - uses generic API methods
```

#### Custom Fields Required on Sales Invoice:
- `custom_hbl_export_sea_link` (Link to Export Sea House Bill)

#### Custom Fields Required on Purchase Invoice:
- `custom_eshbl_id` (Link to Export Sea House Bill)

#### Custom Fields Required on Journal Entry:
- `custom_eshbl_id` (Link to Export Sea House Bill)

---

### 6. Export Air House Bill (0% Complete)

**Required Changes:**

#### Python File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_air_house_bill/export_air_house_bill.py`

```python
# Add the following methods (copy from Import Air House Bill):

def onload(self):
    # Load payment entries and draft invoices
    # Change parenttype to "Export Air House Bill"
    # Change custom field filters to:
    #   - custom_hbl_export_air_link (for Sales Invoice)
    #   - custom_eahbl_id (for Purchase Invoice)

def get_invoice_list(self):
    # Return list of sales invoice links

# Add module-level functions:
def get_gl_entry_from_invoice(invoice_list):
    # Get payment entries from GL Entry

def get_draft_sales_and_purchase_invoice_list(house_bill_no):
    # Get draft Sales & Purchase Invoices
    # Filter by custom_hbl_export_air_link and custom_eahbl_id
```

#### JavaScript File: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_air_house_bill/export_air_house_bill.js`

```javascript
// Copy entire content from import_air_house_bill.js
// Change 'Import Air House Bill' references to 'Export Air House Bill'
// No other changes needed - uses generic API methods
```

#### Custom Fields Required on Sales Invoice:
- `custom_hbl_export_air_link` (Link to Export Air House Bill)

#### Custom Fields Required on Purchase Invoice:
- `custom_eahbl_id` (Link to Export Air House Bill)

#### Custom Fields Required on Journal Entry:
- `custom_eahbl_id` (Link to Export Air House Bill)

---

## Required Child Tables (Already Exist)

All House Bill doctypes need these child tables in their schema:

1. **`invoice_list`** - Fastrack Sales Invoice (tracks sales invoices)
2. **`purchase_invoice_list`** - Fastrack Purchase Invoice (tracks expenses)
3. **`profit_share_list`** - Profit Share List (tracks journal entries)
4. **`payment_entry_list`** - Fastrack Payment Entry (tracks payments via GL)
5. **`draft_invoice_list`** - Fastrack Draft Bill (shows draft invoices)

These child table doctypes already exist:
- `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/fastrack_sales_invoice/`
- `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/fastrack_purchase_invoice/`
- `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/fastrack_payment_entry/`
- `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/fastrack_draft_bill/`

---

## Required Custom Fields

### On Sales Invoice:
```json
{
    "custom_hbl_type": "Select" with options:
        - Import Sea House Bill
        - Import Air House Bill
        - Import D2D Bill
        - Export Sea House Bill
        - Export Air House Bill
    "custom_hbl_sea_link": "Link - Import Sea House Bill",
    "custom_hbl_air_link": "Link - Import Air House Bill",
    "custom_hbl_d2d_link": "Link - Import D2D Bill",
    "custom_hbl_export_sea_link": "Link - Export Sea House Bill",
    "custom_hbl_export_air_link": "Link - Export Air House Bill"
}
```

### On Purchase Invoice:
```json
{
    "custom_hbl_type": "Select" with options (same as Sales Invoice),
    "custom_shbl_id": "Link - Import Sea House Bill",
    "custom_ahbl_id": "Link - Import Air House Bill",
    "custom_dhbl_id": "Link - Import D2D Bill",
    "custom_eshbl_id": "Link - Export Sea House Bill",
    "custom_eahbl_id": "Link - Export Air House Bill"
}
```

### On Journal Entry:
```json
{
    "custom_hbl_type": "Select" with options (same as above),
    "custom_shbl_id": "Link - Import Sea House Bill",
    "custom_ahbl_id": "Link - Import Air House Bill",
    "custom_dhbl_id": "Link - Import D2D Bill",
    "custom_eshbl_id": "Link - Export Sea House Bill",
    "custom_eahbl_id": "Link - Export Air House Bill"
}
```

**Note**: These custom fields may already exist for Import Sea and Import Air. Need to add fields for D2D and Export types.

---

## Implementation Workflow

### For Each Pending House Bill Type:

1. **Check/Add Schema Fields** (JSON file)
   - Ensure child tables exist: `invoice_list`, `purchase_invoice_list`, `profit_share_list`, `payment_entry_list`, `draft_invoice_list`
   - Ensure total fields exist: `total_invoice_amount`, `total_purchase_amount`, `total_profit_share`, `total_payment`

2. **Update Python Controller**
   - Copy `onload()`, `get_invoice_list()` methods from Import Air House Bill
   - Update `parenttype` references
   - Update custom field filters in `get_draft_sales_and_purchase_invoice_list()`

3. **Update JavaScript Controller**
   - Copy entire JS from Import Air House Bill
   - Update doctype name references
   - No other changes needed (API methods are generic)

4. **Add Custom Fields** (if missing)
   - Sales Invoice: Add link field
   - Purchase Invoice: Add link field
   - Journal Entry: Add link field
   - Ensure `custom_hbl_type` select field has all options

5. **Run Migration**
   ```bash
   bench --site development.localhost migrate
   bench build --app fastrack_erp
   bench --site development.localhost clear-cache
   ```

6. **Test**
   - Create a House Bill and submit it
   - Click "Sales Invoice" button → creates invoice with link
   - Submit Sales Invoice → should update HBL's invoice_list
   - Create Purchase Invoice with HBL link → should update purchase_invoice_list
   - Create Journal Entry with HBL link → should update profit_share_list
   - Test PDF download buttons

---

## Architecture Summary

### Data Flow

```
┌──────────────────────────────┐
│   Sales Invoice (Submitted)  │
│  - custom_hbl_type           │
│  - custom_hbl_*_link         │
└──────────┬───────────────────┘
           │
           │ on_submit hook
           ▼
┌──────────────────────────────┐
│ sales_invoice.after_submit() │ (Generic handler)
│  - Reads custom_hbl_type     │
│  - Maps to correct link field│
│  - Gets HBL document         │
└──────────┬───────────────────┘
           │
           │ Appends items
           ▼
┌──────────────────────────────┐
│   House Bill (Any Type)      │
│  - invoice_list ←─────────── │ Sales invoices added here
│  - purchase_invoice_list     │ Purchase invoices added here
│  - profit_share_list         │ Journal entries added here
│  - payment_entry_list        │ Payments (from GL) added here
│  - draft_invoice_list        │ Draft invoices shown here
└──────────────────────────────┘
```

### Generic Implementation Benefits

✅ **Single Source of Truth**: Doc event handlers work for all HBL types
✅ **Maintainability**: Changes to billing logic happen in one place
✅ **Consistency**: All HBL types behave identically
✅ **Scalability**: Easy to add new HBL types in future

---

## Testing Checklist

For each House Bill type, verify:

- [ ] ✅ Sales Invoice creation from HBL works
- [ ] ✅ Sales Invoice submit updates HBL's invoice_list
- [ ] ✅ Sales Invoice cancel removes from HBL's invoice_list
- [ ] ✅ Purchase Invoice submit updates HBL's purchase_invoice_list
- [ ] ✅ Purchase Invoice cancel removes from purchase_invoice_list
- [ ] ✅ Journal Entry submit updates HBL's profit_share_list
- [ ] ✅ Journal Entry cancel removes from profit_share_list
- [ ] ✅ Payment Entry appears in payment_entry_list (via GL Entry)
- [ ] ✅ Draft invoices appear in draft_invoice_list
- [ ] ✅ PDF download dialogs work
- [ ] ✅ Total amounts calculate correctly

---

## Next Steps

1. **Immediate**:
   - Add custom fields to Sales Invoice, Purchase Invoice, Journal Entry for D2D and Export types
   - Copy Python logic to Import D2D Bill
   - Copy JavaScript to Import D2D Bill
   - Test Import D2D Bill billing workflow

2. **Then**:
   - Copy Python logic to Export Sea House Bill
   - Copy JavaScript to Export Sea House Bill
   - Test Export Sea billing workflow

3. **Finally**:
   - Copy Python logic to Export Air House Bill
   - Copy JavaScript to Export Air House Bill
   - Test Export Air billing workflow

4. **Documentation**:
   - Update MASTER_HOUSE_BILL_README.md with billing functionality
   - Create user guide for billing workflow

---

## Files Modified

### Generic Infrastructure (Works for All Types):
1. `/apps/fastrack_erp/fastrack_erp/doc_events/sales_invoice.py` ✅
2. `/apps/fastrack_erp/fastrack_erp/doc_events/purchase_invoice.py` ✅
3. `/apps/fastrack_erp/fastrack_erp/doc_events/journal_entry.py` ✅
4. `/apps/fastrack_erp/fastrack_erp/api.py` ✅

### Import Air House Bill (Complete):
5. `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.py` ✅
6. `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.js` ✅

### Pending:
7. Import D2D Bill Python & JavaScript ⏳
8. Export Sea House Bill Python & JavaScript ⏳
9. Export Air House Bill Python & JavaScript ⏳

---

**Last Updated**: December 26, 2025
**Implementation Progress**: 50% (Core infrastructure + 1 of 4 pending doctypes)
