import React, { createContext, useContext, useEffect, useState } from "react";
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





const { data :mblData  , error:mblError,  mutate:mblMutate,isLoading:mblIsLoading,isValidating:mblIsValidating } = useFrappeGetCall(
  pdfPolicy.getMethod || "frappe.client.get",
  pdfPolicy.getMethod ? {
    mbl_id: pdfFormOption.docName,
  } : undefined,
  {
    swrConfig: {
      revalidateOnMount: false,
      revalidateIfStale: false,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  }
)

  const { data, error,  mutate,isLoading,isValidating } = useFrappeGetDoc(
    pdfPolicy.parentDoctype,
    pdfFormOption.docName,
    
    {
        swrConfig: {
          revalidateOnMount:false,
          revalidateIfStale:false,
          revalidateOnFocus:true,
          shouldRetryOnError:false,
        },
      }
  )
  console.log("pdfFormOption.docName-bgry", pdfFormOption.docName);
  console.log("data_object", data,isLoading,isValidating);
  console.log("mblData_object", mblData,mblIsLoading,mblIsValidating);

// refetch data when docName changes
useEffect(() => {
  
  if(pdfFormOption.docName && !pdfPolicy.isMasterBill){
    mutate();
  }
  if(pdfFormOption.docName && pdfPolicy.isMasterBill){
    mblMutate();
  }
}, [pdfFormOption.docName]);

useEffect(() => {
  // Clear error first
  setErrorObj((prev) => ({ ...prev, docNameError: "" }));

  // // Handle error states
  // if (error || mblError) {
  //   setDocTypeData({});
  //   setErrorObj((prev) => ({ 
  //     ...prev, 
  //     docNameError: "Not Found. Enter Valid Doc Name" 
  //   }));
  //   return;
  // }

  // Determine which data to use based on policy
  const targetData = pdfPolicy.isMasterBill ? mblData : data;
  console.log("targetData_object", targetData);

  // Handle data processing
  if (targetData) {
    // Check if data is an array (which seems to be an invalid state)
    if (Array.isArray(targetData)) {
      setDocTypeData({});
    } else {
      // For master bill, use the message property, otherwise use data directly
      const processedData = pdfPolicy.isMasterBill ? targetData?.message : targetData;
      setDocTypeData(processedData || {});
      console.log("doc_data",docTypeData)
    }
  } else {
    // No data available
    setDocTypeData({});
  }
}, [data, error, mblData, mblError, pdfPolicy.isMasterBill]);


  return (
    <PDFDownloadContext.Provider value={{ pdfFormOption, setPdfFormOption, pdfPolicy, setPdfPolicy,docTypeData,errorObj }}>
      {children}
    </PDFDownloadContext.Provider>
  );
};

export const usePDFDownload = () => useContext(PDFDownloadContext);
