/**
 * Customer / supplier pickers for PDF Download: merge header fields with
 * distinct values from child tables so filters match table rows for every
 * report (import/export sea, air, D2D, MBL, arrival, IGM, etc.).
 */

const sortLabels = (a: string, b: string) =>
  a.localeCompare(b, undefined, { sensitivity: "base" });

const DEFAULT_CUSTOMER_CHILD_KEYS = [
  "invoice_list",
  "draft_invoice_list",
] as const;

const DEFAULT_SUPPLIER_CHILD_KEYS = [
  "purchase_invoice_list",
  "draft_invoice_list",
] as const;

function uniqueSorted(values: string[]): { value: string; label: string }[] {
  const merged = [...new Set(values.map((v) => v.trim()).filter(Boolean))].sort(
    sortLabels,
  );
  return merged.map((v) => ({ value: v, label: v }));
}

function mergeChildKeys(
  defaults: readonly string[],
  policyChild?: string,
): Set<string> {
  const keys = new Set<string>([...defaults]);
  if (policyChild) keys.add(policyChild);
  return keys;
}

function collectRowStrings(
  doc: Record<string, unknown>,
  keys: Set<string>,
  field: "customer" | "supplier",
): string[] {
  const out: string[] = [];
  for (const key of keys) {
    const rows = doc[key];
    if (!Array.isArray(rows)) continue;
    for (const r of rows) {
      if (!r || typeof r !== "object") continue;
      const v = (r as Record<string, unknown>)[field];
      if (v != null && String(v).trim() !== "") {
        out.push(String(v).trim());
      }
    }
  }
  return out;
}

export function buildCustomerSelectOptions(
  docTypeData: Record<string, unknown> | null | undefined,
  customerDocFields: string[] | undefined,
  policyChildDoctype?: string,
): { value: string; label: string }[] {
  if (!docTypeData || Object.keys(docTypeData).length === 0) {
    return [];
  }

  const fromDoc: string[] = [];
  if (customerDocFields?.length) {
    for (const field of customerDocFields) {
      const v = docTypeData[field];
      if (v != null && String(v).trim() !== "") {
        fromDoc.push(String(v).trim());
      }
    }
  }

  const keys = mergeChildKeys(DEFAULT_CUSTOMER_CHILD_KEYS, policyChildDoctype);
  const fromRows = collectRowStrings(docTypeData, keys, "customer");

  return uniqueSorted([...fromDoc, ...fromRows]);
}

export function buildSupplierSelectOptions(
  docTypeData: Record<string, unknown> | null | undefined,
  policyChildDoctype?: string,
): { value: string; label: string }[] {
  if (!docTypeData || Object.keys(docTypeData).length === 0) {
    return [];
  }
  const keys = mergeChildKeys(DEFAULT_SUPPLIER_CHILD_KEYS, policyChildDoctype);
  const fromRows = collectRowStrings(docTypeData, keys, "supplier");
  return uniqueSorted(fromRows);
}
