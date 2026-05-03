import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { PDFPolicy } from "../../utils/pdfPolicy";
import { useFrappeGetCall, useFrappeGetDoc } from "frappe-react-sdk";

// Define the structure of the form data
export type PdfFormOption = {
  pdfName: string;
  docName?: string;
  customerName?: string;
  supplierName?: string;
  selectedInvoice?: string[];
  selectedId?: string;
};

// Define the context type
type PDFDownloadContextType = {
  pdfFormOption: PdfFormOption;
  setPdfFormOption: React.Dispatch<React.SetStateAction<PdfFormOption>>;
  pdfPolicy: PDFPolicy;
  setPdfPolicy: React.Dispatch<React.SetStateAction<PDFPolicy>>;
  docTypeData: {};
  errorObj: {
    docNameError: string;
  };
};

// Create the context with a default (temporary) value
const PDFDownloadContext = createContext<PDFDownloadContextType>({
  pdfFormOption: {
    pdfName: "",
    docName: "",
    customerName: "",
    supplierName: "",
  },
  setPdfFormOption: () => {},
  pdfPolicy: {
    name: "",
    parentDoctype: "",
    selectPDFNAME: false,
    selectDocName: false,
    selectCustomer: false,
    selectSupplier: false,
    selectChildDoctype: false,
    CHILD_DOCTYPE: "",
    DOWNLOAD_METHOD: "",
  },
  setPdfPolicy: () => {},
  docTypeData: {},
  errorObj: {
    docNameError: "",
  },
});

export const PDFDownloadProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [pdfFormOption, setPdfFormOption] = useState<PdfFormOption>({
    pdfName: "",
    docName: "",
    customerName: "",
    supplierName: "",
    selectedInvoice: [],
    selectedId: "",
  });
  const [docTypeData, setDocTypeData] = useState<{}>({});
  const [pdfPolicy, setPdfPolicy] = useState<PDFPolicy>({
    name: "",
    parentDoctype: "",
    selectPDFNAME: false,
    selectDocName: false,
    selectCustomer: false,
    selectSupplier: false,
    selectChildDoctype: false,
    CHILD_DOCTYPE: "",
    DOWNLOAD_METHOD: "",
  });
  const [errorObj, setErrorObj] = useState<{ docNameError: string }>({
    docNameError: "",
  });

  const mblCallSwrKey =
    pdfPolicy.isMasterBill &&
    pdfPolicy.getMethod &&
    pdfFormOption.docName?.trim()
      ? `pdf-mbl|${pdfPolicy.getMethod}|${pdfFormOption.docName.trim()}`
      : null;

  const {
    data: mblData,
    error: mblError,
    mutate: mblMutate,
    isLoading: mblIsLoading,
    isValidating: mblIsValidating,
  } = useFrappeGetCall(
    pdfPolicy.getMethod || "frappe.client.get",
    mblCallSwrKey
      ? { mbl_id: pdfFormOption.docName?.trim() || "" }
      : undefined,
    mblCallSwrKey,
    {
      revalidateOnMount: false,
      revalidateIfStale: false,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    },
  );

  /** Server resolves child `invoice_list` or linked Sales Invoices (no SI list perm). */
  const portalInvoiceLinesFetchEnabled = Boolean(
    pdfFormOption.docName?.trim() &&
      pdfPolicy.parentDoctype &&
      pdfPolicy.CHILD_DOCTYPE === "invoice_list",
  );

  const hblDocSwrKey =
    pdfPolicy.parentDoctype && pdfFormOption.docName?.trim()
      ? `pdf-doc|${pdfPolicy.parentDoctype}|${pdfFormOption.docName.trim()}`
      : null;

  const { data, error, mutate, isLoading, isValidating } = useFrappeGetDoc(
    pdfPolicy.parentDoctype || "",
    pdfFormOption.docName?.trim() || "",
    hblDocSwrKey,
    {
      revalidateOnMount: false,
      revalidateIfStale: false,
      revalidateOnFocus: true,
      shouldRetryOnError: false,
    },
  );

  /** Same HBL lines for every PDF type — omit pdfName so cache is shared across
   *  Sea Export USD/BDT, FC Export, Shipping, etc. and switching types does not
   *  briefly clear rows while a duplicate fetch runs. */
  const portalLinesSwrKey = portalInvoiceLinesFetchEnabled
    ? `portal-hbl-inv|${pdfPolicy.parentDoctype}|${pdfFormOption.docName.trim()}`
    : null;

  const { data: portalLinesResponse } = useFrappeGetCall<{
    message?: unknown;
  }>(
    "fastrack_erp.api.get_hbl_invoice_lines_for_portal",
    portalLinesSwrKey
      ? {
          parent_doctype: pdfPolicy.parentDoctype,
          hbl_name: pdfFormOption.docName?.trim() || "",
        }
      : undefined,
    portalLinesSwrKey,
    {
      revalidateOnMount: false,
      revalidateIfStale: false,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    },
  );

  const portalInvoiceRows = useMemo(() => {
    const raw = portalLinesResponse as Record<string, unknown> | undefined;
    if (!raw) return [];
    const msg = raw.message;
    if (Array.isArray(msg)) return msg;
    if (typeof msg === "string") {
      try {
        const parsed = JSON.parse(msg) as unknown;
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return [];
      }
    }
    return [];
  }, [portalLinesResponse]);

  // refetch when document or HBL doctype (import vs export) changes
  useEffect(() => {
    if (pdfFormOption.docName && !pdfPolicy.isMasterBill) {
      mutate();
    }
    if (pdfFormOption.docName && pdfPolicy.isMasterBill) {
      mblMutate();
    }
  }, [pdfFormOption.docName, pdfPolicy.parentDoctype, pdfPolicy.isMasterBill]);

  useEffect(() => {
    setErrorObj((prev) => ({ ...prev, docNameError: "" }));

    const targetData = pdfPolicy.isMasterBill ? mblData : data;

    const fromPortal = portalInvoiceRows.map(
      (row: Record<string, unknown>) => ({
        name: row.name != null ? String(row.name) : "",
        invoice_link:
          row.invoice_link != null
            ? String(row.invoice_link)
            : String(row.name ?? ""),
        customer: row.customer,
        item_code:
          row.item_code != null && String(row.item_code).trim() !== ""
            ? String(row.item_code)
            : "-",
        qty:
          row.qty != null && String(row.qty).trim() !== ""
            ? String(row.qty)
            : "-",
      }),
    );

    const shellDoc = (): Record<string, unknown> =>
      pdfFormOption.docName?.trim()
        ? { name: pdfFormOption.docName.trim() }
        : {};

    if (!targetData) {
      if (portalInvoiceLinesFetchEnabled && fromPortal.length > 0) {
        setDocTypeData({
          ...shellDoc(),
          invoice_list: fromPortal,
        });
      } else {
        setDocTypeData(
          portalInvoiceLinesFetchEnabled
            ? { ...shellDoc(), invoice_list: [] }
            : {},
        );
      }
      return;
    }

    if (Array.isArray(targetData)) {
      setDocTypeData({});
      return;
    }

    let processedData: Record<string, unknown> | null = pdfPolicy.isMasterBill
      ? ((targetData as { message?: Record<string, unknown> }).message as
          | Record<string, unknown>
          | null
          | undefined) ?? null
      : (targetData as Record<string, unknown>);

    if (!processedData || typeof processedData !== "object") {
      processedData = shellDoc();
    }

    if (portalInvoiceLinesFetchEnabled && fromPortal.length > 0) {
      processedData = { ...processedData, invoice_list: fromPortal };
    }

    setDocTypeData(processedData);
  }, [
    data,
    error,
    mblData,
    mblError,
    pdfPolicy.isMasterBill,
    pdfPolicy.parentDoctype,
    pdfPolicy.CHILD_DOCTYPE,
    portalInvoiceLinesFetchEnabled,
    portalInvoiceRows,
    pdfFormOption.docName,
  ]);

  return (
    <PDFDownloadContext.Provider
      value={{
        pdfFormOption,
        setPdfFormOption,
        pdfPolicy,
        setPdfPolicy,
        docTypeData,
        errorObj,
      }}
    >
      {children}
    </PDFDownloadContext.Provider>
  );
};

export const usePDFDownload = () => useContext(PDFDownloadContext);
