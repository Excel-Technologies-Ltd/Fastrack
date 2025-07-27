import React, { createContext, useContext, useEffect, useState } from "react";
import type { PDFPolicy } from "../../utils/pdfPolicy";
import { useFrappeGetDoc } from "frappe-react-sdk";


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
    docNameError:string;
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
    docNameError:"",
  },

});

export const PDFDownloadProvider = ({ children }: { children: React.ReactNode }) => {
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
  const [errorObj, setErrorObj] = useState<{docNameError:string}>({docNameError:""});





  const { data, error,  mutate } = useFrappeGetDoc(
    pdfPolicy.parentDoctype,
    pdfFormOption.docName,
    {
        swrConfig: {
          revalidateOnMount:false,
          revalidateIfStale:false,
          revalidateOnFocus:false,
          shouldRetryOnError:false,
        },
      }
  )

// refetch data when docName changes
useEffect(() => {
  mutate();
}, [pdfFormOption.docName]);

useEffect(() => {
  if (data) {
    if (Array.isArray(data)) {
      setDocTypeData({});
    } else {
      setDocTypeData(data);
    }
    setErrorObj((prev)=>({...prev,docNameError:""}));
  }else{
    setDocTypeData({});
    setErrorObj((prev)=>({...prev,docNameError:""}))
  }
  if(error){
    setDocTypeData({});
    setErrorObj((prev)=>({...prev,docNameError:"Not Found Enter Valid Doc Name"}));
  }
}, [data,error]);


  return (
    <PDFDownloadContext.Provider value={{ pdfFormOption, setPdfFormOption, pdfPolicy, setPdfPolicy,docTypeData,errorObj }}>
      {children}
    </PDFDownloadContext.Provider>
  );
};

export const usePDFDownload = () => useContext(PDFDownloadContext);
