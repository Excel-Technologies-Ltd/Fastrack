/**
 * Customer / supplier pickers for PDF Download: unique parties linked on the
 * selected document (header link fields) and on its invoice lines.
 */

type PickerOption = { value: string; label: string };

/** Header Link fields pointing to Customer / Supplier, per parent doctype. */
const PARTY_LINK_FIELDS: Record<string, { customer: string[]; supplier: string[] }> = {
  "Import Sea House Bill": {
    customer: ["customer", "hbl_consignee", "notify_to", "co_loader", "cf_agent"],
    supplier: ["hbl_shipper", "agent", "shipping_line", "carrier"],
  },
  "Import Air House Bill": {
    customer: ["customer", "consignee", "notify_party"],
    supplier: ["shipper", "agent", "airlines"],
  },
  "Import D2D Bill": {
    customer: ["customer", "consignee", "notify_party"],
    supplier: ["shipper", "agent"],
  },
  "Import Sea Master Bill": {
    customer: [],
    supplier: ["consignee", "shipper", "agent", "shipping_line"],
  },
  "Export Sea House Bill": {
    customer: ["hbl_shipper", "hbl_consignee", "notify_to", "also_notify_party", "delivery_agent", "agent", "cf_agent"],
    supplier: ["shipping_line"],
  },
  "Export Air House Bill": {
    customer: ["shipper", "consignee", "notify_party", "also_notify_party", "agent"],
    supplier: ["vendor", "airline"],
  },
  "Export D2D Bill": {
    customer: ["customer", "consignee", "notify_party"],
    supplier: ["shipper", "agent"],
  },
};

/** Child tables whose rows carry a customer / supplier link. */
const CUSTOMER_CHILD_KEYS = ["invoice_list"];
const SUPPLIER_CHILD_KEYS = ["purchase_invoice_list"];

const toText = (v: unknown) => (v != null ? String(v).trim() : "");

function uniqueSorted(values: string[]): PickerOption[] {
  return [...new Set(values.filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }))
    .map((v) => ({ value: v, label: v }));
}

function collectPartyValues(
  doc: Record<string, unknown> | null | undefined,
  headerFields: string[],
  childKeys: string[],
  rowField: "customer" | "supplier",
): string[] {
  if (!doc) return [];
  const out = headerFields.map((f) => toText(doc[f]));
  for (const key of childKeys) {
    const rows = doc[key];
    if (!Array.isArray(rows)) continue;
    for (const row of rows) {
      if (row && typeof row === "object") {
        out.push(toText((row as Record<string, unknown>)[rowField]));
      }
    }
  }
  return out;
}

export function buildCustomerSelectOptions(
  docTypeData: Record<string, unknown> | null | undefined,
  parentDoctype: string,
  policyChildDoctype?: string,
): PickerOption[] {
  const childKeys = [...new Set([...CUSTOMER_CHILD_KEYS, ...(policyChildDoctype ? [policyChildDoctype] : [])])];
  return uniqueSorted(
    collectPartyValues(docTypeData, PARTY_LINK_FIELDS[parentDoctype]?.customer ?? [], childKeys, "customer"),
  );
}

export function buildSupplierSelectOptions(
  docTypeData: Record<string, unknown> | null | undefined,
  parentDoctype: string,
): PickerOption[] {
  return uniqueSorted(
    collectPartyValues(docTypeData, PARTY_LINK_FIELDS[parentDoctype]?.supplier ?? [], SUPPLIER_CHILD_KEYS, "supplier"),
  );
}
