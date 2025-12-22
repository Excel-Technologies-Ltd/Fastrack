# Import Operations Documentation
## Fastrack ERP - Import Sea & Air Freight Management

This document explains how the Import Sea and Import Air freight operations work in Fastrack ERP, including the master-house bill relationship, workflows, and technical implementation.

---

## Table of Contents
1. [Overview](#overview)
2. [Import Sea Operations](#import-sea-operations)
3. [Import Air Operations](#import-air-operations)
4. [Master-House Bill Relationship](#master-house-bill-relationship)
5. [Workflow Guide](#workflow-guide)
6. [Technical Architecture](#technical-architecture)
7. [Data Validation Rules](#data-validation-rules)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Fastrack ERP manages consolidated freight shipments using a **Master Bill → House Bill** relationship pattern. This allows freight forwarders to:

- Track a single shipment from the shipping line/airline (Master Bill)
- Manage multiple customer consignments within that shipment (House Bills)
- Distribute cargo weight/packages across house bills
- Generate invoices and track payments per customer
- Ensure weight/package accounting is accurate

### Supported Import Types

1. **Import Sea Master Bill (MBL)** ↔ **Import Sea House Bill (HBL)**
   - Ocean freight via shipping lines
   - Container-based tracking
   - Bill of Lading (B/L) numbers

2. **Import Air Master Bill (MAWB)** ↔ **Import Air House Bill (HAWB)**
   - Air freight via airlines
   - Weight-based tracking
   - Air Waybill (AWB) numbers

---

## Import Sea Operations

### Components

#### 1. Import Sea Master Bill (MBL)
**Purpose**: Represents the main shipment from the shipping line.

**Key Fields**:
- `mbl_no`: Master Bill of Lading number (unique identifier)
- `agent`: Shipping agent/supplier
- `shipping_line`: Carrier company
- `consignee`: Master consignee
- `gr_weight`: Total gross weight of shipment
- `total_container`: Number of containers
- `total_no_of_hbl`: Number of house bills to create
- `container_info`: Child table listing all containers (Fastrack Item)
- `hbl_info`: Child table listing all house bills to create (HBL Info)

**Container Info Fields**:
- Container number
- Size (20', 40', etc.)
- Weight
- Number of packages
- Seal number

#### 2. Import Sea House Bill (HBL)
**Purpose**: Individual customer consignment within the master bill.

**Key Fields**:
- `hbl_id`: House Bill of Lading number (unique identifier)
- `mbl_no`: Link to Master Bill (visible)
- `mbl_link`: Link to Master Bill (hidden, actual foreign key)
- `mbl_doctype`: Parent doctype name
- `hbl_doc_name`: Child table row name in MBL
- `customer`: Customer receiving the goods
- `sales_person`: Sales representative
- `container_info`: Portion of containers allocated to this HBL (Fastrack Sea Item)
- `container_cost_info`: Freight certificate/costing
- Financial tracking tables:
  - `invoice_list`: Sales invoices
  - `payment_entry_list`: Payments received
  - `purchase_invoice_list`: Expenses
  - `profit_share_list`: Profit distribution

---

## Import Air Operations

### Components

#### 1. Import Air Master Bill (MAWB)
**Purpose**: Represents the main air shipment from the airline.

**Key Fields**:
- `mbl_no`: Master Air Waybill number (unique identifier)
- `agent`: Air freight agent
- `airlines`: Carrier (airline)
- `consignee`: Master consignee
- `gr_weight`: Total gross weight
- `chargeable_weight`: Chargeable weight for billing
- `total_no_of_hbl`: Number of house air waybills
- `hbl_info`: Child table listing HAWBs to create

**Differences from Sea**:
- No container tracking (weight-based instead)
- Flight information instead of vessel/voyage
- Simpler cargo structure

#### 2. Import Air House Bill (HAWB)
**Purpose**: Individual customer consignment within the master air waybill.

**Key Fields**:
- `hbl_no`: House Air Waybill number (unique identifier)
- `mbl_no`: Link to Master Bill (visible)
- `mbl_link`: Link to Master Bill (hidden FK)
- `mbl_doctype`: "Import Air Master Bill"
- `hbl_doc_name`: Child table row name
- `hbl_gr_weight`: Gross weight of this HAWB
- `customer`: Customer details
- `sales_person`: Sales representative

**Key Differences from Sea HBL**:
- Uses `hbl_gr_weight` instead of `hbl_weight`
- No container allocation
- Flight details instead of vessel details

---

## Master-House Bill Relationship

### Database Schema

```
┌─────────────────────────────┐
│  Import Sea/Air Master Bill │
│                             │
│  - mbl_no (Primary Key)     │
│  - agent                    │
│  - gr_weight                │
│  - total_no_of_hbl          │
│                             │
│  Child Table: hbl_info      │
│  ┌─────────────────────┐    │
│  │ - hbl_no            │    │
│  │ - hbl_link  ────────┼────┼──┐
│  │ - is_create (0/1)   │    │  │
│  │ - weight            │    │  │
│  └─────────────────────┘    │  │
└─────────────────────────────┘  │
                                 │
                                 │ Bidirectional
                                 │ Relationship
                                 │
┌─────────────────────────────┐  │
│ Import Sea/Air House Bill   │  │
│                             │  │
│  - hbl_id/hbl_no (PK)       │  │
│  - mbl_no (visible link)    │  │
│  - mbl_link (FK) ◄──────────┼──┘
│  - mbl_doctype              │
│  - hbl_doc_name             │
│  - customer                 │
│  - weight                   │
└─────────────────────────────┘
```

### Bidirectional Updates

#### On HBL Submit:
1. HBL validates its data (weight limits, container references)
2. System finds parent MBL using `mbl_link`
3. Locates the corresponding row in MBL's `hbl_info` using `hbl_doc_name`
4. Updates the row:
   - Sets `hbl_link` = HBL document name
   - Sets `is_create` = 1 (checked)
   - Sets `weight` = HBL weight
5. Saves the MBL (triggers validation)

#### On MBL Update After Submit:
1. System finds all submitted HBLs linked to this MBL
2. Propagates changes from MBL to each HBL:
   - Agent
   - Ports
   - Dates
   - Other master-level data

---

## Workflow Guide

### Creating a Complete Import Shipment

#### Step 1: Create Master Bill

**For Sea Freight**:
1. Navigate to: **Import Sea Master Bill** → New
2. Fill in master bill details:
   - MBL Number
   - Agent/Shipping Line
   - Vessel/Voyage information
   - Total gross weight
   - Total number of containers
   - **Total No. of HBL** (e.g., 3)

3. Add containers in **Container Info** child table:
   - Container number
   - Size, weight, packages
   - Seal number

4. Add HBL placeholders in **HBL Info** child table:
   - Row 1: HBL No. = "SHBL-00001"
   - Row 2: HBL No. = "SHBL-00002"
   - Row 3: HBL No. = "SHBL-00003"
   - Leave "HBL Link" empty
   - Leave "Is Create" unchecked

5. **Submit** the Master Bill

**For Air Freight**:
1. Navigate to: **Import Air Master Bill** → New
2. Fill in MAWB details:
   - MAWB Number
   - Agent/Airline
   - Flight information
   - Gross weight
   - **Total No. of HBL** (e.g., 3)

3. Add HAWB placeholders in **HBL Info** child table:
   - Row 1: HBL No. = "h1"
   - Row 2: HBL No. = "h2"
   - Row 3: HBL No. = "h3"

4. **Submit** the Master Bill

---

#### Step 2: Create House Bills (Sequential)

**Important**: House Bills must be created in sequential order!

##### Creating the First HBL:

1. Open the submitted Master Bill
2. Scroll to **HBL Info** section
3. Click the **"Create"** button on Row 1

   **What happens**:
   - System checks if MBL is submitted ✓
   - System finds the first uncreated HBL (Row 1)
   - Opens a new HBL form with pre-filled data:
     - MBL link fields (hidden)
     - Agent
     - Carrier/Airline
     - Ports
     - Dates

4. Fill in HBL-specific details:
   - **HAWB No.** (for air) or **HBL ID** (for sea)
   - Customer information
   - Sales person
   - **Weight** (must not exceed MBL gross weight)
   - Number of packages
   - Inco Term

   **For Sea HBL only**:
   - Select containers from Container Info
   - Allocate weight per container

5. **Save** the HBL (validates weight distribution)
6. **Submit** the HBL

   **What happens on submit**:
   - System validates weight doesn't exceed MBL capacity
   - Updates parent MBL's HBL Info Row 1:
     - ✓ Checks "Is Create"
     - Fills "HBL Link" with document name
     - Records weight
   - "Create" button changes to "View" button

##### Creating Subsequent HBLs:

7. Go back to Master Bill
8. Click **"Create"** on Row 2

   **Validation**:
   - System checks Row 1 is created ✓
   - If not, shows: "Please create previous HBL first"

9. Repeat the process for each HBL

10. After all HBLs are created:
    - All rows in HBL Info have "Is Create" checked ✓
    - Sum of all HBL weights = MBL gross weight
    - Master Bill validation passes

---

#### Step 3: Financial Tracking (HBL Level)

Each House Bill acts as the financial hub:

##### Generate Sales Invoice:
1. Open the HBL
2. Click **"Create"** → **"Sales Invoice"**
3. Add invoice items (freight charges, handling fees, etc.)
4. Submit invoice
5. Invoice appears in HBL's `invoice_list` child table

##### Generate Purchase Invoice (Expenses):
1. Open the HBL
2. Click **"Create"** → **"Purchase Invoice"**
3. Add expense items (carrier charges, port fees, etc.)
4. Submit invoice
5. Invoice appears in HBL's `purchase_invoice_list`

##### Track Payments:
1. Create **Payment Entry** against the Sales Invoice
2. Payment automatically links to HBL
3. Appears in `payment_entry_list` child table

##### Profit Sharing:
1. Create **Journal Entry** for profit distribution
2. Links to HBL via custom field
3. Tracks profit splits between parties

---

## Technical Architecture

### File Structure

```
fastrack_erp/
├── fastrack_erp/
│   ├── api.py                          # Core API methods
│   ├── hooks.py                        # Event hooks configuration
│   │
│   ├── doc_events/
│   │   ├── mbl.py                      # Master/House bill validation logic
│   │   ├── sales_invoice.py
│   │   ├── purchase_invoice.py
│   │   └── journal_entry.py
│   │
│   ├── fastrack_erp/doctype/
│   │   ├── import_sea_master_bill/
│   │   │   ├── import_sea_master_bill.json
│   │   │   ├── import_sea_master_bill.py
│   │   │   └── import_sea_master_bill.js    # Client-side logic
│   │   │
│   │   ├── import_sea_house_bill/
│   │   │   ├── import_sea_house_bill.json
│   │   │   ├── import_sea_house_bill.py
│   │   │   └── import_sea_house_bill.js
│   │   │
│   │   ├── import_air_master_bill/
│   │   │   ├── import_air_master_bill.json
│   │   │   ├── import_air_master_bill.py
│   │   │   └── import_air_master_bill.js
│   │   │
│   │   ├── import_air_house_bill/
│   │   │   ├── import_air_house_bill.json
│   │   │   ├── import_air_house_bill.py
│   │   │   └── import_air_house_bill.js
│   │   │
│   │   ├── hbl_info/                   # Child table for HBL list
│   │   ├── fastrack_item/              # MBL containers (Sea)
│   │   ├── fastrack_sea_item/          # HBL containers (Sea)
│   │   └── container_cost_info/        # Freight certificate
│   │
│   └── report_api/                     # PDF generation
│       ├── import_delivery_order.py
│       ├── import_arrival_notice.py
│       ├── import_sea_invoice_bdt.py
│       └── import_sea_invoice_usd.py
```

### Key API Methods

Located in `fastrack_erp/api.py`:

#### 1. House Bill Creation
```python
@frappe.whitelist()
def make_sea_house_bill(source_name, target_doc=None):
    """Creates a new Sea House Bill from Master Bill"""

@frappe.whitelist()
def make_air_house_bill(source_name, target_doc=None):
    """Creates a new Air House Bill from Master Bill"""
```

#### 2. Sequential Validation
```python
@frappe.whitelist()
def get_first_uncreated_hbl_info(master_bill_no, doctype):
    """Returns the first HBL row where is_create=0"""
    # Ensures sequential creation
```

#### 3. Container Queries (Sea only)
```python
def get_single_fastrack_item_by_bill_no(bill_ids, container_no):
    """Aggregates container weight/packages across bills"""
    # Used for validation
```

### Event Hooks

Located in `fastrack_erp/hooks.py`:

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
}
```

### JavaScript Logic

Located in `import_sea_master_bill.js` and `import_air_master_bill.js`:

```javascript
// Child Table Event Handler
frappe.ui.form.on('HBL Info', {
    create_hbl: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        // Validate MBL is submitted
        if(frm.doc.docstatus != 1) {
            return frappe.msgprint("MBL not submitted yet")
        }

        // If already created, navigate to HBL
        if(row.is_create) {
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
                if (r.message.name == row.name) {
                    // Open mapped document
                    frappe.model.open_mapped_doc({
                        method: "fastrack_erp.api.make_sea_house_bill",
                        frm: frm,
                    });
                } else {
                    frappe.msgprint("Create previous HBL first")
                }
            }
        });
    },
});
```

---

## Data Validation Rules

### Master Bill Validation

Located in `doc_events/mbl.py → validate()`:

#### Sea Master Bill:
1. **Container count must match**:
   ```
   len(container_info) == total_container
   ```

2. **HBL count must match**:
   ```
   len(hbl_info) == total_no_of_hbl
   ```

3. **Total container weight must equal gross weight**:
   ```
   sum(container.weight) == gr_weight
   ```

4. **When all HBLs created, sum of HBL weights must equal gross weight**:
   ```
   sum(hbl.weight for all created HBLs) == gr_weight
   ```

5. **HBL total weight cannot exceed gross weight**:
   ```
   sum(hbl.weight) <= gr_weight
   ```

#### Air Master Bill:
1. **HBL count must match**:
   ```
   len(hbl_info) == total_no_of_hbl
   ```

2. **When all HAWBs created, sum must equal gross weight**:
   ```
   sum(hbl.hbl_gr_weight for all created HBLs) == gr_weight
   ```

### House Bill Validation

#### Sea House Bill (import_sea_house_bill.py):

1. **Container names must exist in MBL**:
   ```python
   # All container numbers in HBL must be in MBL
   HBL_containers ⊆ MBL_containers
   ```

2. **Seal numbers must match**:
   ```python
   HBL_container.seal_no == MBL_container.seal_no
   ```

3. **Weight distribution per container**:
   ```python
   # For each container
   sum(all_HBL_weights_for_container) + current_HBL_weight <= MBL_container_weight
   ```

4. **Package distribution per container**:
   ```python
   sum(all_HBL_packages_for_container) + current_HBL_packages <= MBL_container_packages
   ```

5. **HBL total container weight must equal HBL gross weight**:
   ```python
   sum(HBL_container_info.weight) == hbl_weight
   ```

#### Air House Bill (import_air_house_bill.py):

1. **Total HAWB weight cannot exceed MAWB gross weight**:
   ```python
   def validate_weight(self):
       # Get all submitted HAWBs for this MAWB
       existing_hawbs_weight = sum(all submitted HAWB weights)

       # Check total doesn't exceed MAWB capacity
       if (existing_hawbs_weight + self.hbl_gr_weight) > mbl_doc.gr_weight:
           frappe.throw("Weight exceeds MAWB capacity")
   ```

---

## Troubleshooting

### Common Issues

#### 1. "MBL not submitted yet"
**Cause**: Trying to create HBL before submitting Master Bill
**Solution**: Submit the Master Bill first

#### 2. "Create previous HBL first"
**Cause**: Trying to create HBL out of sequence
**Solution**: Create HBLs in order (Row 1, then Row 2, then Row 3...)

#### 3. "Container name do not match with master bill"
**Cause**: Sea HBL references a container not in MBL
**Solution**: Only select containers that exist in MBL's Container Info

#### 4. "Weight mismatch for container"
**Cause**: Trying to allocate more weight than available in container
**Solution**:
- Check how much weight is already allocated to other HBLs
- Reduce the weight for this HBL
- Or increase the container weight in MBL

#### 5. "Total weight of HBL list is not equal to gross weight"
**Cause**: Sum of all HBL weights ≠ MBL gross weight
**Solution**:
- Adjust individual HBL weights
- Ensure last HBL takes the remaining weight
- Check for rounding errors

#### 6. AttributeError: 'ImportAirHouseBill' object has no attribute 'hbl_weight'
**Cause**: Code trying to access Sea-specific field on Air HBL
**Solution**: Use `hbl_gr_weight` for Air, `hbl_weight` for Sea (already fixed in code)

#### 7. "Create" button not working
**Cause**: JavaScript not loaded or wrong child table name
**Solution**:
- Hard refresh browser (Ctrl+Shift+R)
- Clear cache: `bench --site [site] clear-cache`
- Rebuild assets: `bench build --app fastrack_erp`
- Check browser console for errors

---

## Field Name Differences: Sea vs Air

| Concept | Sea Field Name | Air Field Name |
|---------|---------------|----------------|
| Master Bill Number | `mbl_no` | `mbl_no` (MAWB) |
| House Bill Number | `hbl_id` | `hbl_no` (HAWB) |
| Carrier | `shipping_line` | `airlines` |
| Transport Name | `mv` (vessel) | `flight_name` |
| House Bill Weight | `hbl_weight` | `hbl_gr_weight` |
| Containers | `container_info` | N/A (weight-based) |

---

## XML Export (Sea Only)

The system can generate customs-compliant XML for sea imports:

```xml
<Awbolds>
  <Master_bol>
    <Customs_office_code>301</Customs_office_code>
    <Reference_number>MBL-2025-05-0000015</Reference_number>
  </Master_bol>

  <Bol_segment>  <!-- Repeated for each HBL -->
    <Bol_id>
      <Bol_reference>SHBL-00001</Bol_reference>
    </Bol_id>
    <Traders_segment>
      <Carrier>...</Carrier>
      <Consignee>...</Consignee>
    </Traders_segment>
    <ctn_segment>  <!-- Container details -->
      ...
    </ctn_segment>
  </Bol_segment>
</Awbolds>
```

**Usage**: Click "Download XML" button on submitted Master Bill

---

## Development Notes

### Adding New Validations

1. **Master Bill validation**: Edit `doc_events/mbl.py → validate()`
2. **House Bill validation**: Edit respective HBL Python file
3. **Client-side validation**: Edit respective JS file

### Adding New Fields

1. Update JSON schema in respective doctype folder
2. Run `bench migrate`
3. Update mapper functions in `api.py` if needed
4. Update validation logic if needed

### Testing Workflow

1. Create a test MBL with 2-3 containers
2. Add 2-3 HBL entries in HBL Info
3. Submit MBL
4. Create first HBL, allocate partial container weight
5. Submit first HBL
6. Verify MBL's HBL Info updated
7. Create second HBL
8. Try to allocate more weight than available (should fail)
9. Adjust weight and submit
10. Verify total weights match

---

## Summary

The Import Sea and Air functionality in Fastrack ERP implements a sophisticated freight forwarding system with:

- **Master-Detail Pattern**: One master bill → multiple house bills
- **Strict Validation**: Weight and package accounting enforced
- **Bidirectional Sync**: Changes propagate between master and house bills
- **Sequential Creation**: HBLs must be created in order
- **Financial Integration**: Complete revenue/expense tracking per HBL
- **Customs Compliance**: XML export for government systems
- **Rich Reporting**: PDF generation for all business documents

This system ensures accurate cargo accounting, proper weight distribution, and complete financial tracking for freight forwarding operations.

---

**Document Version**: 1.0
**Last Updated**: December 22, 2025
**Maintained By**: Fastrack ERP Development Team
