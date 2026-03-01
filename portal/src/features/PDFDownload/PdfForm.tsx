import React, { useEffect, useState } from "react";
import { Checkbox, Form, Space, Card, Typography, Row, Col } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import { AntSelect, AntButton } from "../../components/UI";
import { PDF_NAME_LIST } from "../../constants/pdfName";
import { usePDFDownload } from "./PDFDownloadPorvider";
import { PDF_POLICY } from "../../utils/pdfPolicy";
import type { PdfFormOption } from "./PDFDownloadPorvider";
import { useDownloadPDF } from "./hooks/DownloadPDF";
import { validatePdfPolicy } from "../../utils/validateOption";
import { toast } from "react-toastify";
import { useFrappeGetDocList } from "frappe-react-sdk";
 
const PdfForm = () => {
  const { pdfPolicy, setPdfPolicy, setPdfFormOption, pdfFormOption, docTypeData } = usePDFDownload();
  const { previewPdf } = useDownloadPDF();
  const [loading, setLoading] = useState(false);
  
  // Use only ONE state for document search/selection
  const [docSearchValue, setDocSearchValue] = useState("");

  console.log("pdfFormOption", pdfFormOption);

  const handleChange = (field: keyof PdfFormOption) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setPdfFormOption({ ...pdfFormOption, [field]: e.target.value });
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
      setDocSearchValue(""); // Also reset the search value
    }
    console.log("field", field, e.target.value);
  };

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
      setDocSearchValue(""); // Reset search value
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
      setDocSearchValue(""); // Reset search value
      const policy = PDF_POLICY[selectedPdfName];
      setPdfPolicy((prev) => ({ ...prev, ...policy }));
    }
    console.log("field", "pdfName", selectedPdfName);
  };

  const handleSubmit = async () => {
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
        setDocSearchValue(""); // Clear search value
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

  // Use docSearchValue for API call
  const { data: docNameList } = useFrappeGetDocList(pdfPolicy.parentDoctype || "", {
    orFilters: [
      ['name', 'like', `%${docSearchValue}%`]
    ],
    limit: 10,
    fields: ['name']
  });
  
  const doclistArray = docNameList && docNameList.length > 0 ? docNameList : [];
  


  // Build customer options from Customer-linked fields defined in CUSTOMER_FIELDS policy
  const customerOptions = (() => {
    const fields = pdfPolicy.CUSTOMER_FIELDS;
    if (!fields || fields.length === 0 || Object.keys(docTypeData).length === 0) return [];
    const values = [
      ...new Set(
        fields
          .map((field) => (docTypeData as any)[field])
          .filter(Boolean)
      ),
    ];
    return values.map((v: string) => ({ value: v, label: v }));
  })();

  // get supplier list from child data and must be unique
  let childData: any = pdfPolicy.CHILD_DOCTYPE && docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData]
        ? docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData]
        : null;

  const supplierList = childData && Array.isArray(childData) ? [...new Set(childData.map((c: any) => c.supplier))] : [];

  const supplierOptions =
    supplierList?.length > 0
      ? [{ value: "", label: "Select Supplier" }, ...supplierList.map((c: any) => ({ value: c, label: c }))]
      : [{ value: "", label: "Select Supplier" }];


  // Sync docSearchValue with pdfFormOption.docName when docName is cleared from other places
  useEffect(() => {
    if (!pdfFormOption.docName && docSearchValue) {
      setDocSearchValue("");
    }
  }, [pdfFormOption.docName]);



  return (
    <Card style={{ maxWidth: 600, margin: '0 auto' }}>
      <Form layout="vertical" onFinish={handleSubmit}>
        {/* PDF Name Checkboxes */}
      <Form.Item
        label={
          <Typography.Text strong>
            PDF Name <Typography.Text type="danger">*</Typography.Text>
          </Typography.Text>
        }
        required
      >
        {Object.values(PDF_NAME_LIST).length > 5 ? (
          // Use grid layout if more than 5 items
          <Row gutter={[8, 8]}>
            {Object.values(PDF_NAME_LIST).map((name) => (
              <Col span={12} key={name}>
                <Checkbox
                  checked={pdfFormOption.pdfName === name}
                  onChange={() => handlePdfNameChange(name)}
                  style={{ fontSize: '12px' }}
                >
                  {name}
                </Checkbox>
              </Col>
            ))}
          </Row>
        ) : (
          // Default vertical layout
          <Space direction="vertical" style={{ width: '100%' }}>
            {Object.values(PDF_NAME_LIST).map((name) => (
              <Checkbox
                key={name}
                checked={pdfFormOption.pdfName === name}
                onChange={() => handlePdfNameChange(name)}
                style={{ fontSize: '12px' }}
              >
                {name}
              </Checkbox>
            ))}
          </Space>
        )}
      </Form.Item>


        {/* Document Name Search */}
        <AntSelect
          label="Document Name"
          placeholder="Enter document name"
          value={docSearchValue}
          onChange={(value: string) => {
            setDocSearchValue(value);
            setPdfFormOption({ ...pdfFormOption, docName: value });
          }}
          onSearch={(value: string) => {
            setDocSearchValue(value);
            if (pdfFormOption.docName && value !== pdfFormOption.docName) {
              setPdfFormOption({ ...pdfFormOption, docName: "" });
            }
          }}
          showSearch={true}
          filterOption={false}
          disabled={!pdfPolicy.selectDocName}
          required={pdfPolicy.selectDocName}
          options={doclistArray?.map((doc: any) => ({ 
            value: doc.name, 
            label: doc.name 
          })) || []}
          notFoundContent={docSearchValue ? "No documents found" : "Start typing to search..."}
        />

        {/* Customer Select */}
        <AntSelect
          label="Customer"
          placeholder="Select Customer"
          value={pdfFormOption.customerName}
          onChange={(value: string) => {
            const fakeEvent = { target: { value } } as React.ChangeEvent<HTMLSelectElement>;
            handleChange("customerName")(fakeEvent);
          }}
          disabled={!pdfPolicy.selectCustomer}
          required={pdfPolicy.selectCustomer}
          options={customerOptions}
        />

        {/* Supplier Select */}
        <AntSelect
          label="Supplier"
          placeholder="Select Supplier"
          value={pdfFormOption.supplierName}
          onChange={(value: string) => {
            const fakeEvent = { target: { value } } as React.ChangeEvent<HTMLSelectElement>;
            handleChange("supplierName")(fakeEvent);
          }}
          disabled={!pdfPolicy.selectSupplier}
          required={pdfPolicy.selectSupplier}
          options={supplierOptions}
        />

        {/* Submit Button */}
        <Form.Item>
          <AntButton 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            icon={<DownloadOutlined />}
            size="large"
            style={{ width: '100%' }}
          >
            {loading ? "Processing..." : "Download PDF"}
          </AntButton>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default PdfForm;