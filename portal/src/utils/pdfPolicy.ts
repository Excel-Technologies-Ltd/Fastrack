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
        selectCustomer: true,
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
        selectSupplier: true,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.EXPENSE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.api.download_purchase_invoice_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    },
    [PDF_NAME_LIST.ARRIVAL_NOTICE]: {
        name: PDF_NAME_LIST.ARRIVAL_NOTICE,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: false,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.CONTAINER_INFO.name,
        DOWNLOAD_METHOD: "fastrack_erp.report_api.import_arrival_notice.download_arrival_notice_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            doc_name: "docName"
        }
    },
    [PDF_NAME_LIST.DELIVERY_ORDER]: {
        name: PDF_NAME_LIST.DELIVERY_ORDER,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: false,
        DOWNLOAD_METHOD: "fastrack_erp.report_api.import_delivery_order.download_delivery_order_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            doc_name: "docName"
        }
    },
    [PDF_NAME_LIST.SEA_IMPORT_INVOICE_USD]: {
        name: PDF_NAME_LIST.SEA_IMPORT_INVOICE_USD,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.INVOICE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.report_api.import_sea_invoice_usd.download_sea_import_invoice_usd_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    },
    [PDF_NAME_LIST.SEA_IMPORT_INVOICE_BDT]: {
        name: PDF_NAME_LIST.SEA_IMPORT_INVOICE_BDT,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: true,
        selectSupplier: false,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.INVOICE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.report_api.import_sea_invoice_bdt.download_sea_import_invoice_bdt_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    },
    [PDF_NAME_LIST.SEA_IMPORT_INVOICE_USD]: {
        name: PDF_NAME_LIST.SEA_IMPORT_INVOICE_USD,
        parentDoctype: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.NAME,
        selectPDFNAME: true,
        selectDocName: true,
        selectCustomer: true,
        selectSupplier: false,
        selectChildDoctype: true,
        CHILD_DOCTYPE: DOCTYPE_LIST.IMPORT_SEA_HOUSE_BILL.CHILD_DOCTYPE.INVOICE_LIST.name,
        DOWNLOAD_METHOD: "fastrack_erp.report_api.import_sea_invoice_usd.download_sea_import_invoice_usd_pdf",
        HAS_ARGUMENTS: true,
        ARGUMENTS: {
            invoice_ids: "selectedId",
            doctype_name: "docName"
        }
    }
}





