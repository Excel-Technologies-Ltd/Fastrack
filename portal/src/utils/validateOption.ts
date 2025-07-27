import { PDF_POLICY } from "./pdfPolicy";
import type { PdfFormOption } from "../features/PDFDownload/PDFDownloadPorvider";

interface ValidationError {
    field: string;
    message: string;
}

export const validatePdfPolicy = (
    pdfFormOption: PdfFormOption
): { isValid: boolean; errors: ValidationError[] } => {
    const errors: ValidationError[] = [];

    // Check if pdfName exists in PDF_POLICY
    if (!pdfFormOption.pdfName || !PDF_POLICY[pdfFormOption.pdfName]) {
        errors.push({ field: "pdfName", message: "PDF Name is required and must be valid" });
        return { isValid: false, errors };
    }

    const policy = PDF_POLICY[pdfFormOption.pdfName];

    // Validate selectDocName
    if (policy.selectDocName && !pdfFormOption.docName) {
        errors.push({ field: "docName", message: "Document Name is required" });
    }

    // Validate selectCustomer
    if (policy.selectCustomer && !pdfFormOption.customerName) {
        errors.push({ field: "customerName", message: "Customer Name is required" });
    }

    // Validate selectSupplier
    if (policy.selectSupplier && !pdfFormOption.supplierName) {
        errors.push({ field: "supplierName", message: "Supplier Name is required" });
    }

    // Validate selectedId when HAS_ARGUMENTS is true
    if (policy.HAS_ARGUMENTS && policy.ARGUMENTS) {
        for (const key in policy.ARGUMENTS) {
            if (policy.ARGUMENTS[key] === "selectedId" && !pdfFormOption.selectedId) {
                errors.push({ field: "selectedId", message: "Selected List ID is required" });
            }
            if (policy.ARGUMENTS[key] === "docName" && !pdfFormOption.docName) {
                errors.push({ field: "docName", message: "Document Name is required for arguments" });
            }
        }
    }

    return {
        isValid: errors.length === 0,
        errors,
    };
};