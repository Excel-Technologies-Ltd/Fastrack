import React, { useEffect, useState } from "react";
import Select from "../../components/UI/Select";

import Button from "../../components/UI/Button";
import { PDF_NAME_LIST } from "../../constants/pdfName";
import { usePDFDownload } from "./PDFDownloadPorvider";
import { PDF_POLICY } from "../../utils/pdfPolicy";
import type { PdfFormOption } from "./PDFDownloadPorvider";
import { useDownloadPDF } from "./hooks/DownloadPDF";
import { validatePdfPolicy } from "../../utils/validateOption";
import { toast } from "react-toastify";
import { useFrappeGetDocList } from "frappe-react-sdk";
import SearchableInput from "../../components/UI/SearchableInput";

const PdfForm = () => {
  const { pdfPolicy, setPdfPolicy, setPdfFormOption, pdfFormOption, docTypeData } = usePDFDownload();
  const { previewPdf } = useDownloadPDF();
  const [loading, setLoading] = useState(false);
  const [docNameSearch, setDocNameSearch] = useState("");

  console.log("pdfFormOption", pdfFormOption);

  const handleChange = (field: keyof PdfFormOption) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setPdfFormOption({ ...pdfFormOption, [field]: e.target.value });
    
    // Handle docName search separately
    if (field === "docName") {
      setDocNameSearch(e.target.value);
    }
    
    // if select pdfName then reset the form without pdfName
    if (field === "pdfName") {
      const policy = PDF_POLICY[e.target.value];
      setPdfPolicy((prev) => ({ ...prev, ...policy }));
      setPdfFormOption((prev) => ({ 
        ...prev, 
        docName: "", 
        customerName: "", 
        supplierName: "", 
        selectedId: "" 
      }));
      setDocNameSearch(""); // Reset search term
    }
    console.log("field", field, e.target.value);
  };



  // docNameList
  const { data: docNameList } = useFrappeGetDocList(
    pdfPolicy.parentDoctype,
   {
      orFilters: [
        ['name', 'like', `%${docNameSearch}%`]
      ],
      limit: 10,
      fields: ['name'],
      orderBy: {
        field: 'modified',
        order: 'desc'
      },
    } ,
    {
      swrConfig: {
        revalidateOnMount: false,
        revalidateIfStale: false,
        revalidateOnFocus: false,
        shouldRetryOnError: false,
      },
    }
  );
  const docNameListArray = docNameList && docNameList.length > 0 ? docNameList : [];

 

  const handlePdfNameChange = (selectedPdfName: string) => {
    // If the clicked PDF name is already selected, uncheck it
    if (pdfFormOption.pdfName === selectedPdfName) {
      setPdfFormOption((prev) => ({ 
        ...prev, 
        pdfName: "", 
        docName: "", 
        customerName: "", 
        supplierName: "", 
        selectedId: "" 
      }));
      setDocNameSearch("");
      // Reset policy to default state
      setPdfPolicy((prev) => ({ 
        ...prev, 
        selectDocName: false,
        selectCustomer: false, 
        selectSupplier: false, 
        selectChildDoctype: false,
        parentDoctype: "",
        CHILD_DOCTYPE: ""
      }));
    } else {
      // Select the new PDF name
      setPdfFormOption((prev) => ({ 
        ...prev, 
        pdfName: selectedPdfName, 
        docName: "", 
        customerName: "", 
        supplierName: "", 
        selectedId: "" 
      }));
      setDocNameSearch("");
      const policy = PDF_POLICY[selectedPdfName];
      setPdfPolicy((prev) => ({ ...prev, ...policy }));
    }
    console.log("field", "pdfName", selectedPdfName);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const validateOption = validatePdfPolicy(pdfFormOption);
      if (!validateOption.isValid) {
        toast.error(validateOption.errors[0].message);
        setLoading(false);
        return;
      }
      const response = await previewPdf();
      if (response.success) {
        toast.success("PDF Previewed Successfully");
        // clear the form
        setPdfFormOption({ 
          pdfName: "", 
          docName: "", 
          customerName: "", 
          supplierName: "", 
          selectedInvoice: [], 
          selectedId: "" 
        });
        setDocNameSearch("");
        setPdfPolicy({ 
          ...pdfPolicy, 
          selectCustomer: false, 
          selectSupplier: false, 
          selectChildDoctype: false 
        });
      } else {
        toast.error(response.errors?.[0]?.message || "Something went wrong");
      }
      setLoading(false);
    } catch (error) {
      console.log("error", error);
    }
  };

  // get customer list from child data and must be unique
  let childData: any = pdfPolicy.CHILD_DOCTYPE && docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData] 
        ? docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData] 
        : null;
        
  const customerList = childData && Array.isArray(childData) ? [...new Set(childData.map((c: any) => c.customer))] : [];
  const supplierList = childData && Array.isArray(childData) ? [...new Set(childData.map((c: any) => c.supplier))] : [];
  const customerOptions =
    customerList?.length > 0
      ? [{ value: "", label: "Select Customer" }, ...customerList.map((c: any) => ({ value: c, label: c }))]
      : [{ value: "", label: "Select Customer" }];
  const supplierOptions =
    supplierList?.length > 0
      ? [{ value: "", label: "Select Supplier" }, ...supplierList.map((c: any) => ({ value: c, label: c }))]
      : [{ value: "", label: "Select Supplier" }];

  // useEffect(() => {
  //   if (pdfPolicy.selectCustomer && pdfFormOption.docName) {
  //     // mutateCustomerList();
  //   }
  //   if (pdfPolicy.selectSupplier && pdfFormOption.docName) {
  //     // setPdfFormOption((prev) => ({ ...prev, supplierName: "" }));
  //   }
  // }, [pdfPolicy.selectCustomer, pdfFormOption.docName]);

  return (
    <form onSubmit={handleSubmit} className="max-w-md p-4 space-y-4" style={{fontSize: "10px"}}>
      {/* PDF Name Checkboxes */}
      <div>
        <label className="block font-medium text-gray-700 mb-2">
          PDF Name <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-2 gap-3">
          {Object.values(PDF_NAME_LIST).map((name) => (
            <label key={name} className="flex items-center space-x-2 cursor-pointer" style={{fontSize: "10px"}}>
              <input
                type="checkbox"
                checked={pdfFormOption.pdfName === name}
                onChange={() => handlePdfNameChange(name)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                style={{fontSize: "10px"}}
              />
              <span className="text-sm text-gray-700">{name}</span>
            </label>
          ))}
        </div>
      </div>

      <SearchableInput
      name="docName"
        label="Document Name"
        placeholder="Enter document name"
        searchable={true}
        options={docNameListArray?.map((doc: any) => ({ value: doc.name, label: doc.name })) || []}
        onSelect={(value) => {
          setPdfFormOption({ ...pdfFormOption, docName: value });
          setDocNameSearch(value);
        }}
        value={pdfFormOption.docName}
        onChange={handleChange("docName")}
        required={pdfPolicy.selectDocName}
        disabled={!pdfPolicy.selectDocName}
      />

      <Select
        label="Customer"
        options={customerOptions}
        value={pdfFormOption.customerName}
        onChange={handleChange("customerName")}
        required
        disabled={!pdfPolicy.selectCustomer}
      />

      <Select
        label="Supplier"
        options={supplierOptions}
        value={pdfFormOption.supplierName}
        onChange={handleChange("supplierName")}
        required
        disabled={!pdfPolicy.selectSupplier}
      />

      <Button 
        className={`${loading ? "opacity-50 cursor-not-allowed flex items-center justify-center space-x-2" : ""}`} 
        type="submit" 
        disabled={loading}
      >
        {loading && (
          <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        <span>{loading ? "Processing..." : "Download PDF"}</span>
      </Button>
    </form>
  );
};

export default PdfForm;