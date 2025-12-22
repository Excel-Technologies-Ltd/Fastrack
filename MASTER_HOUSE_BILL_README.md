# Master Bill to House Bill Documentation

## Overview

This document explains the Master Bill (MBL) to House Bill (HBL) functionality in Fastrack ERP. The system supports four different workflows:

1. **Import Sea** - Import Sea Master Bill → Import Sea House Bill
2. **Import Air** - Import Air Master Bill → Import Air House Bill
3. **Export Sea** - Export Sea Master Bill → Export Sea House Bill
4. **Export Air** - Export Air Master Bill → Export Air House Bill

All four workflows follow the same pattern and architecture, with minor field variations.

---

## Table of Contents

- [Business Workflow](#business-workflow)
- [Technical Architecture](#technical-architecture)
- [Field Mappings](#field-mappings)
- [Database Schema](#database-schema)
- [Implementation Details](#implementation-details)
- [Usage Guide](#usage-guide)
- [Validation Rules](#validation-rules)
- [Troubleshooting](#troubleshooting)

---

## Business Workflow

### Sequential HBL Creation Process

1. **Create Master Bill**: Create and submit an Import/Export Sea/Air Master Bill with basic shipment details
2. **Add HBL Info**: Add rows to the HBL Info child table specifying:
   - HBL Number
   - Expected Weight (optional)
3. **Sequential Creation**: House Bills must be created in the order they appear in the HBL Info table
4. **Create House Bill**: Click the "Create HBL" button on an HBL Info row to generate a House Bill
5. **Auto-Update**: When a House Bill is submitted, the parent Master Bill's HBL Info is automatically updated with:
   - Link to the created HBL
   - Actual weight from the HBL
   - Status flag (`is_create = 1`)

### Key Business Rules

- Master Bill must be submitted before creating House Bills
- House Bills must be created sequentially (can't skip rows)
- Total HBL weight cannot exceed Master Bill gross weight
- Weight validation occurs on HBL submission
- Canceling an HBL updates the parent MBL automatically

---

## Technical Architecture

### Components

Each Master/House Bill workflow consists of:

1. **Master Bill DocType** (e.g., Import Sea Master Bill)
   - Main shipment document
   - Contains HBL Info child table
   - Tracks total number of HBLs and gross weight

2. **HBL Info Child DocType** (e.g., HBL Info, Import Air HBL Info, Export Sea HBL Info, Export Air HBL Info)
   - Child table within Master Bill
   - Contains HBL reference data
   - Fields:
     - `hbl_no` - House Bill number
     - `hbl_link` - Link to created House Bill document
     - `is_create` - Flag indicating if HBL has been created (0 or 1)
     - `weight` - Actual weight from the House Bill
     - `create_hbl` - Button field to trigger HBL creation

3. **House Bill DocType** (e.g., Import Sea House Bill)
   - Detailed shipment document for individual consignments
   - Links back to parent Master Bill
   - Contains weight and container information

### Architecture Diagram

```
┌─────────────────────────────────┐
│   Master Bill (MBL)             │
│  - mbl_no                       │
│  - gr_weight                    │
│  - total_no_of_hbl              │
│                                 │
│  ┌───────────────────────────┐  │
│  │ HBL Info (Child Table)    │  │
│  │ - hbl_no                  │  │
│  │ - hbl_link    ───────┐    │  │
│  │ - is_create          │    │  │
│  │ - weight             │    │  │
│  │ - create_hbl [Button]│    │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
                                  │
                                  │ (Bidirectional Link)
                                  │
                                  ▼
┌─────────────────────────────────┐
│   House Bill (HBL)              │
│  - hbl_no                       │
│  - mbl_link (FK to MBL)         │
│  - mbl_no (Display Link)        │
│  - hbl_doc_name (HBL Info row)  │
│  - mbl_doctype                  │
│  - weight/hbl_weight/hbl_gr_wt  │
│  - container_info (Sea only)    │
└─────────────────────────────────┘
```

---

## Field Mappings

### Master Bill to House Bill Field Mapping

#### Import Sea
```
Import Sea Master Bill → Import Sea House Bill
- mbl_no → mbl_no
- name → mbl_link
- consignee → consignee
- agent → agent
- mbl_date → mbl_date
- port_of_loading → port_of_loading
- port_of_delivery → port_of_delivery
- vessel → vessel
- voyage → voyage
```

#### Import Air
```
Import Air Master Bill → Import Air House Bill
- mbl_no → mbl_no
- name → mbl_link
- consignee → airlines
- agent → agent
- mbl_date → mbl_date
- port_of_loading → port_of_loading
- port_of_delivery → port_of_delivery
```

#### Export Sea
```
Export Sea Master Bill → Export Sea House Bill
- mbl_no → mbl_no
- name → mbl_link
- agent → agent
- mbl_date → mbl_date
- port_of_loading → port_of_loading
- port_of_delivery → port_of_delivery
- vessel → vessel_name
- voyage → voyage_no
- etd → etd
```

#### Export Air
```
Export Air Master Bill → Export Air House Bill
- mbl_no → mbl_no
- name → mbl_link
- agent → agent
- airline → airline
- mbl_date → mbl_date
- port_of_loading → port_of_loading
- port_of_delivery → port_of_delivery
- flight → flight_name
- flight_date → flight_date
- etd → etd
```

### Weight Field Names by DocType

| DocType | Weight Field Name | Notes |
|---------|------------------|-------|
| Import Sea Master Bill | `gr_weight` | Gross weight |
| Import Sea House Bill | `hbl_weight` | HBL weight |
| Import Air Master Bill | `gr_weight` | Gross weight |
| Import Air House Bill | `hbl_gr_weight` | HBL gross weight |
| Export Sea Master Bill | `gr_weight` | Gross weight |
| Export Sea House Bill | `gross_weight` | Gross weight |
| Export Air Master Bill | `gr_weight` | Gross weight |
| Export Air House Bill | `hbl_gr_weight` | HBL gross weight |

---

## Database Schema

### Master Bill Fields (Common)

```python
{
    "mbl_no": "Data",              # Primary identifier
    "gr_weight": "Float",           # Gross weight
    "total_no_of_hbl": "Int",      # Expected number of HBLs
    "hbl_info": "Table",           # Child table
    "mbl_open_by": "Link(User)",   # User tracking
}
```

### HBL Info Fields (Child Table)

```python
{
    "hbl_no": "Data",              # HBL number
    "hbl_link": "Link",            # Link to House Bill doc
    "is_create": "Check",          # 0=not created, 1=created
    "weight": "Float",             # Weight from HBL
    "create_hbl": "Button",        # Trigger HBL creation
}
```

### House Bill Fields (Common)

```python
{
    "hbl_no": "Data",              # Primary identifier
    "mbl_link": "Link",            # FK to Master Bill (hidden)
    "mbl_no": "Link",              # Display link to Master Bill
    "mbl_doctype": "Data",         # Parent doctype name (hidden)
    "hbl_doc_name": "Data",        # HBL Info row name (hidden)
    "hbl_open_by": "Link(User)",   # User tracking
}
```

---

## Implementation Details

### 1. API Methods

Location: `/apps/fastrack_erp/fastrack_erp/api.py`

Each workflow has a dedicated API method:

```python
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None):
    """Create Import Sea House Bill from Master Bill"""

@frappe.whitelist()
def make_air_house_bill(source_name, target_doc=None):
    """Create Import Air House Bill from Master Bill"""

@frappe.whitelist()
def make_export_sea_house_bill(source_name, target_doc=None):
    """Create Export Sea House Bill from Master Bill"""

@frappe.whitelist()
def make_export_air_house_bill(source_name, target_doc=None):
    """Create Export Air House Bill from Master Bill"""

@frappe.whitelist()
def get_first_uncreated_hbl_info(master_bill_no, doctype):
    """Get the first HBL Info row that hasn't been created yet"""
```

### 2. JavaScript Implementation

Each Master Bill has a JavaScript file with child table event handlers:

**Example: Import Sea Master Bill**

```javascript
frappe.ui.form.on('HBL Info', {
    create_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Check if MBL is submitted
        if(frm.doc.docstatus != 1){
            return frappe.msgprint("MBL not submitted yet")
        }

        // If HBL already created, route to it
        if(row.is_create){
            frappe.set_route("Form", "Import Sea House Bill", row.hbl_link);
            return
        }

        // Check sequential creation
        frappe.call({
            method: "fastrack_erp.api.get_first_uncreated_hbl_info",
            args: {
                master_bill_no: frm.doc.name,
                doctype: frm.doc.doctype
            },
            callback: function (r) {
                if (r.message && r.message.name == row.name) {
                    // This is the next HBL to create
                    frappe.model.open_mapped_doc({
                        method: "fastrack_erp.api.make_sea_house_bill",
                        frm: frm,
                    });
                } else {
                    frappe.msgprint("Please create previous HBL first")
                }
            }
        });
    },
});
```

**File Locations:**
- Import Sea: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_sea_master_bill/import_sea_master_bill.js`
- Import Air: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_master_bill/import_air_master_bill.js`
- Export Sea: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_sea_master_bill/export_sea_master_bill.js`
- Export Air: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_air_master_bill/export_air_master_bill.js`

### 3. Server-Side Validation

Each House Bill has validation logic:

**Example: Import Sea House Bill**

```python
def validate_weight(self):
    """Ensure HBL weight doesn't exceed MBL gross weight"""
    if not self.mbl_link:
        return

    mbl_doc = frappe.get_doc('Import Sea Master Bill', self.mbl_link)

    # Get existing house bills for this MBL (excluding current)
    existing_hbls = frappe.db.get_list(
        'Import Sea House Bill',
        filters={'mbl_link': self.mbl_link, 'docstatus': 1},
        pluck='name'
    )

    if self.name and self.name in existing_hbls:
        existing_hbls.remove(self.name)

    # Calculate total weight of other HBLs
    total_other_weight = 0
    if existing_hbls:
        total_other_weight = frappe.db.get_value(
            'Import Sea House Bill',
            {'name': ['in', existing_hbls]},
            'sum(hbl_weight)'
        ) or 0

    # Check if total weight exceeds MBL gross weight
    total_weight = total_other_weight + (self.hbl_weight or 0)

    if total_weight > mbl_doc.gr_weight:
        frappe.throw(
            f"Total HBL weight ({total_weight}) exceeds MBL gross weight ({mbl_doc.gr_weight})"
        )
```

**File Locations:**
- Import Sea: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_sea_house_bill/import_sea_house_bill.py`
- Import Air: `/apps/fastrack_erp/fastrack_erp/fastrack_erp/doctype/import_air_house_bill/import_air_house_bill.py`
- Export Sea: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_sea_house_bill/export_sea_house_bill.py`
- Export Air: `/apps/fastrack_erp/fastrack_erp/fastrack_erp_export/doctype/export_air_house_bill/export_air_house_bill.py`

### 4. Event Hooks

Location: `/apps/fastrack_erp/fastrack_erp/hooks.py`

```python
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
        "on_update_after_submit": "fastrack_erp.doc_events.mbl.validate",
    },
    "Import Air House Bill": {
        "on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
        "before_cancel": "fastrack_erp.doc_events.mbl.delete_child_hbl_on_cancel",
    },
    "Export Sea House Bill": {
        "on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
        "before_cancel": "fastrack_erp.doc_events.mbl.delete_child_hbl_on_cancel",
    },
    "Export Air House Bill": {
        "on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
        "before_cancel": "fastrack_erp.doc_events.mbl.delete_child_hbl_on_cancel",
    },
}
```

### 5. Event Handler Functions

Location: `/apps/fastrack_erp/fastrack_erp/doc_events/mbl.py`

```python
def update_child_hbl(doc, method):
    """Update parent MBL's HBL Info when HBL is submitted"""
    parent_doctype = doc.mbl_doctype
    mbl_doc = frappe.get_doc(parent_doctype, doc.mbl_link)

    # Update the HBL Info row
    for hbl_info in mbl_doc.hbl_info:
        if hbl_info.name == doc.hbl_doc_name:
            hbl_info.hbl_link = doc.name
            hbl_info.is_create = 1

            # Use correct weight field based on doctype
            if parent_doctype == "Import Sea Master Bill":
                hbl_info.weight = doc.hbl_weight
            elif parent_doctype == "Import Air Master Bill":
                hbl_info.weight = doc.hbl_gr_weight
            elif parent_doctype == "Export Sea Master Bill":
                hbl_info.weight = doc.gross_weight
            elif parent_doctype == "Export Air Master Bill":
                hbl_info.weight = doc.hbl_gr_weight
            break

    # Validate for imports only
    if parent_doctype in ["Import Sea Master Bill", "Import Air Master Bill"]:
        validate(mbl_doc, method=None)

    mbl_doc.save(ignore_permissions=True)

def delete_child_hbl_on_cancel(doc, method):
    """Clear HBL Info when HBL is cancelled"""
    parent_doctype = doc.mbl_doctype
    mbl_doc = frappe.get_doc(parent_doctype, doc.mbl_link)

    for hbl_info in mbl_doc.hbl_info:
        if hbl_info.hbl_link == doc.name:
            hbl_info.hbl_link = None
            hbl_info.is_create = 0
            break

    mbl_doc.save(ignore_permissions=True)
```

---

## Usage Guide

### Import Sea Workflow

1. **Create Import Sea Master Bill**
   - Navigate to: Import > Import Sea Master Bill > New
   - Fill in required fields:
     - MBL No.
     - Consignee
     - Gross Weight
     - Total No. of HBL
     - Port of Loading/Delivery
     - Vessel, Voyage
   - Submit the document

2. **Add HBL Info**
   - After submission, scroll to "HBL Info" section
   - Click "Add Row"
   - Enter HBL No. for each house bill
   - Save

3. **Create House Bills**
   - Click "Create HBL" button on the first row
   - System opens a new Import Sea House Bill form with pre-filled data
   - Add container information and weight details
   - Submit the House Bill
   - System automatically updates the HBL Info row

4. **Repeat for Additional HBLs**
   - Create remaining House Bills in sequential order
   - Each submission updates the parent Master Bill

### Import Air Workflow

Same as Import Sea, but:
- Use Import Air Master Bill and Import Air House Bill
- No container information required
- Weight field is `hbl_gr_weight`

### Export Sea Workflow

Same as Import Sea, but:
- Use Export Sea Master Bill and Export Sea House Bill
- Weight field is `gross_weight`
- No validation against total HBL count/weight

### Export Air Workflow

Same as Export Sea, but:
- Use Export Air Master Bill and Export Air House Bill
- Weight field is `hbl_gr_weight`
- No container information required

---

## Validation Rules

### Import Operations (Sea & Air)

1. **Master Bill Validation** (`validate` function)
   - Container list count must equal `total_container` (Sea only)
   - HBL list count must equal `total_no_of_hbl`
   - Total weight of containers must equal `gr_weight` (Sea only)
   - Total weight of HBLs must equal `gr_weight` (when all HBLs created)
   - HBL weight cannot exceed `gr_weight`

2. **House Bill Validation**
   - Total weight of container info must equal HBL weight (Sea only)
   - Sum of all HBL weights cannot exceed MBL gross weight
   - Validates against other submitted HBLs for the same MBL

### Export Operations (Sea & Air)

1. **Master Bill Validation**
   - No automatic validation enforced
   - Can be added as needed

2. **House Bill Validation**
   - Sum of all HBL weights cannot exceed MBL gross weight (if `gr_weight` is set)
   - Validates against other submitted HBLs for the same MBL

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "MBL not submitted yet" | Master Bill is in draft state | Submit the Master Bill first |
| "Please create previous HBL first" | Trying to skip HBL sequence | Create HBLs in order from top to bottom |
| "Total HBL weight exceeds MBL gross weight" | Weight distribution exceeds capacity | Reduce HBL weight or increase MBL gross weight |
| "Container list should be equal to {total_container}" | Container count mismatch | Add/remove containers to match total |
| "Total weight of HBL list is not equal to gross weight" | Weight mismatch | Adjust HBL weights to match MBL gross weight |

---

## Troubleshooting

### Common Issues

#### 1. Can't Create HBL - "MBL not submitted yet"

**Problem**: Trying to create House Bill before Master Bill is submitted

**Solution**: Submit the Master Bill first

```
Import Sea Master Bill > Submit
```

#### 2. Can't Create HBL - "Create previous HBL first"

**Problem**: Trying to create HBL out of sequence

**Solution**: Create HBLs in the order they appear in the HBL Info table

#### 3. Weight Validation Error

**Problem**: Total HBL weight exceeds MBL gross weight

**Solution**:
- Check weights on all submitted HBLs
- Ensure sum of HBL weights ≤ MBL gross weight
- Edit and resubmit HBLs if needed

#### 4. HBL Not Updating Parent MBL

**Problem**: Submitting HBL doesn't update the MBL's HBL Info

**Solution**:
- Check event hooks are registered in `hooks.py`
- Verify `mbl_doctype` and `hbl_doc_name` fields are set correctly
- Check server logs for errors

#### 5. AttributeError on Field Access

**Problem**: Error like "object has no attribute 'hbl_weight'"

**Solution**:
- Check you're using the correct weight field name for the doctype
- Sea Import: `hbl_weight`
- Air Import/Export: `hbl_gr_weight`
- Sea Export: `gross_weight`

### Debug Mode

To debug issues:

1. **Check Server Logs**
   ```bash
   bench --site development.localhost console
   ```

2. **Verify Event Hooks**
   ```bash
   bench --site development.localhost console
   >>> frappe.get_hooks("doc_events")
   ```

3. **Check Field Values**
   ```python
   doc = frappe.get_doc("Import Sea House Bill", "HBL-001")
   print(doc.mbl_link)
   print(doc.mbl_doctype)
   print(doc.hbl_doc_name)
   ```

---

## Developer Notes

### Adding New Master/House Bill Types

To add a new Master/House Bill workflow:

1. **Create Master Bill DocType** with fields:
   - `mbl_no`, `gr_weight`, `total_no_of_hbl`
   - HBL Info child table

2. **Create HBL Info Child DocType** with fields:
   - `hbl_no`, `hbl_link`, `is_create`, `weight`, `create_hbl`

3. **Create House Bill DocType** with fields:
   - `hbl_no`, `mbl_link`, `mbl_no`, `mbl_doctype`, `hbl_doc_name`
   - Weight field (use consistent naming)

4. **Add API Method** in `api.py`:
   ```python
   @frappe.whitelist()
   def make_your_house_bill(source_name, target_doc=None):
       # Implementation
   ```

5. **Add JavaScript** in master bill JS file:
   ```javascript
   frappe.ui.form.on('Your HBL Info', {
       create_hbl: function (frm, cdt, cdn) {
           // Implementation
       }
   });
   ```

6. **Add Validation** in house bill Python file:
   ```python
   def validate_weight(self):
       # Implementation
   ```

7. **Register Event Hooks** in `hooks.py`:
   ```python
   "Your House Bill": {
       "on_submit": "fastrack_erp.doc_events.mbl.update_child_hbl",
       "before_cancel": "fastrack_erp.doc_events.mbl.delete_child_hbl_on_cancel",
   }
   ```

8. **Update Event Handler** in `mbl.py`:
   - Add condition in `update_child_hbl()`
   - Add doctype in `delete_child_hbl_on_cancel()`

### Customization Points

- **Field Mappings**: Modify in API methods (`make_*_house_bill`)
- **Validation Rules**: Modify in House Bill `validate_weight()` methods
- **Sequential Creation**: Modify JavaScript event handlers
- **Weight Field Names**: Update in `update_child_hbl()` function

---

## File Structure

```
apps/fastrack_erp/
├── fastrack_erp/
│   ├── api.py                                    # API methods for all workflows
│   ├── hooks.py                                  # Event hook registration
│   ├── doc_events/
│   │   └── mbl.py                                # Event handler functions
│   ├── fastrack_erp/                             # Import module
│   │   └── doctype/
│   │       ├── import_sea_master_bill/
│   │       │   ├── import_sea_master_bill.json   # Schema
│   │       │   ├── import_sea_master_bill.py     # Python controller
│   │       │   └── import_sea_master_bill.js     # JavaScript
│   │       ├── import_sea_house_bill/
│   │       │   ├── import_sea_house_bill.json
│   │       │   ├── import_sea_house_bill.py      # Validation logic
│   │       │   └── import_sea_house_bill.js
│   │       ├── hbl_info/                          # Child doctype
│   │       │   └── hbl_info.json
│   │       ├── import_air_master_bill/
│   │       ├── import_air_house_bill/
│   │       └── import_air_hbl_info/
│   └── fastrack_erp_export/                      # Export module
│       └── doctype/
│           ├── export_sea_master_bill/
│           ├── export_sea_house_bill/
│           ├── export_sea_hbl_info/
│           ├── export_air_master_bill/
│           ├── export_air_house_bill/
│           └── export_air_hbl_info/
└── MASTER_HOUSE_BILL_README.md                   # This file
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-22 | Initial documentation covering all four workflows |

---

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review server logs for error details
- Contact development team

---

**Last Updated**: December 22, 2025
