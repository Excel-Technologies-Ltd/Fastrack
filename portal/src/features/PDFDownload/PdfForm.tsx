import React, { useEffect, useState } from "react";
import Select from "../../components/UI/Select";
import Input from "../../components/UI/Input";
import Button from "../../components/UI/Button";
import { PDF_NAME_LIST } from "../../constants/pdfName";
import { usePDFDownload } from "./PDFDownloadPorvider";
import { PDF_POLICY } from "../../utils/pdfPolicy";
import type { PdfFormOption } from "./PDFDownloadPorvider";
import { useDownloadPDF } from "./hooks/DownloadPDF";
import { validatePdfPolicy } from "../../utils/validateOption";
import { toast } from "react-toastify";
import { useFrappeGetCall } from "frappe-react-sdk";

const PdfForm = () => {
  const { pdfPolicy, setPdfPolicy, setPdfFormOption, pdfFormOption } = usePDFDownload();
  const { previewPdf } = useDownloadPDF();
  const [loading, setLoading] = useState(false);

  console.log("pdfFormOption", pdfFormOption);

  const handleChange = (field: keyof PdfFormOption) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setPdfFormOption({ ...pdfFormOption, [field]: e.target.value });
    // if select pdfName then reset the form without pdfName
    if (field === "pdfName") {
      const policy = PDF_POLICY[e.target.value];
      setPdfPolicy((prev) => ({ ...prev, ...policy }));
      setPdfFormOption((prev) => ({ ...prev, docName: "", customerName: "", supplierName: "" }));
    }
    console.log("field", field, e.target.value);
  };

  const handlePdfNameChange = (selectedPdfName: string) => {
    setPdfFormOption({ ...pdfFormOption, pdfName: selectedPdfName });
    const policy = PDF_POLICY[selectedPdfName];
    setPdfPolicy((prev) => ({ ...prev, ...policy }));
    setPdfFormOption((prev) => ({ ...prev, pdfName: selectedPdfName, docName: "", customerName: "", supplierName: "" }));
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
      } else {
        toast.error(response.errors?.[0]?.message || "Something went wrong");
      }
      setLoading(false);
    } catch (error) {
      console.log("error", error);
    }
  };

  const { data: customerList, mutate: mutateCustomerList } = useFrappeGetCall("fastrack_erp.api.get_customer_list_by_hbl_id", {
    id: pdfFormOption.docName,
    doctype_name: pdfPolicy.parentDoctype
  });

  console.log("customerList", customerList);
  const customerOptions =
    customerList?.message && Array.isArray(customerList.message)
      ? [{ value: "", label: "Select Customer" }, ...customerList.message.map((c: string) => ({ value: c, label: c }))]
      : [{ value: "", label: "Select Customer" }];

  useEffect(() => {
    if (pdfPolicy.selectCustomer && pdfFormOption.docName) {
      mutateCustomerList();
    }
    if (pdfPolicy.selectSupplier && pdfFormOption.docName) {
      // setPdfFormOption((prev) => ({ ...prev, supplierName: "" }));
    }
  }, [pdfPolicy.selectCustomer, pdfFormOption.docName]);

  return (
    <form onSubmit={handleSubmit} className="max-w-md p-4 space-y-4">
      {/* PDF Name Checkboxes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          PDF Name <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-3">
          {Object.values(PDF_NAME_LIST).map((name) => (
            <label key={name} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={pdfFormOption.pdfName === name}
                onChange={() => handlePdfNameChange(name)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">{name}</span>
            </label>
          ))}
        </div>
      </div>

      <Input
        label="Document Name"
        placeholder="Enter document name"
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
        options={[
          { value: "supp1", label: "Supplier 1" },
          { value: "supp2", label: "Supplier 2" },
        ]}
        value={pdfFormOption.supplierName}
        onChange={handleChange("supplierName")}
        required
        disabled={!pdfPolicy.selectSupplier}
      />

      <Button className={`${loading ? "opacity-50 cursor-not-allowed" : ""}`} type="submit">Download PDF</Button>
    </form>
  );
};

export default PdfForm;