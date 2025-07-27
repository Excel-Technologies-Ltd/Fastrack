import { DOCTYPE_LIST } from "../constants/Doctype"
import { PDF_NAME_LIST } from "../constants/pdfName"


export type PDFPolicy = {
    name: string
    parentDoctype: string
    selectPDFNAME: boolean
    selectDocName: boolean
    selectCustomer: boolean
    selectSupplier: boolean
    selectChildDoctype: boolean
    CHILD_DOCTYPE?: string
    DOWNLOAD_METHOD: string
    HAS_ARGUMENTS?: boolean
    ARGUMENTS?: Record<string, string>
}

export const PDF_POLICY: Record<string, PDFPolicy> = {
    [PDF_NAME_LIST.INCOME]: {
        name: PDF_NAME_LIST.INCOME,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.INVOICE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.api.download_sales_invoice_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    },
    [PDF_NAME_LIST.EXPENSE]: {
        name: PDF_NAME_LIST.EXPENSE,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.EXPENSE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.api.download_purchase_invoice_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    }
}





