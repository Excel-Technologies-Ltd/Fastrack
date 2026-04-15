import { useEffect, useState } from "react";
import { Checkbox, Form, Card, Typography, Row, Col, Divider } from "antd";
import {
  DownloadOutlined,
  FileTextOutlined,
  UserOutlined,
  ShopOutlined,
  FilePdfOutlined,
  SearchOutlined,
} from "@ant-design/icons";
import { AntSelect, AntButton } from "../../components/UI";
import { PDF_NAME_LIST } from "../../constants/pdfName";
import { usePDFDownload } from "./PDFDownloadPorvider";
import { PDF_POLICY } from "../../utils/pdfPolicy";
import { useDownloadPDF } from "./hooks/DownloadPDF";
import { validatePdfPolicy } from "../../utils/validateOption";
import { toast } from "react-toastify";
import { useFrappeGetDocList } from "frappe-react-sdk";

const { Title, Text } = Typography;

const PdfForm = () => {
  const { pdfPolicy, setPdfPolicy, setPdfFormOption, pdfFormOption, docTypeData } = usePDFDownload();
  const { previewPdf } = useDownloadPDF();
  const [loading, setLoading] = useState(false);

  const [docSearchValue, setDocSearchValue] = useState("");
  const [customerSearchVal, setCustomerSearchVal] = useState("");
  const [supplierSearchVal, setSupplierSearchVal] = useState("");

  const resetAllFields = () => {
    setPdfFormOption((prev) => ({
      ...prev,
      docName: "",
      customerName: "",
      supplierName: "",
      selectedId: "",
    }));
    setDocSearchValue("");
    setCustomerSearchVal("");
    setSupplierSearchVal("");
  };

  const handlePdfNameChange = (selectedPdfName: string) => {
    if (pdfFormOption.pdfName === selectedPdfName) {
      setPdfFormOption((prev) => ({
        ...prev,
        pdfName: "",
        docName: "",
        customerName: "",
        supplierName: "",
        selectedId: "",
      }));
      resetAllFields();
      setPdfPolicy((prev) => ({
        ...prev,
        selectDocName: false,
        selectCustomer: false,
        selectSupplier: false,
        selectChildDoctype: false,
        parentDoctype: "",
        CHILD_DOCTYPE: "",
      }));
    } else {
      setPdfFormOption((prev) => ({
        ...prev,
        pdfName: selectedPdfName,
        docName: "",
        customerName: "",
        supplierName: "",
        selectedId: "",
      }));
      resetAllFields();
      const policy = PDF_POLICY[selectedPdfName];
      setPdfPolicy((prev) => ({ ...prev, ...policy }));
    }
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
        toast.success("PDF downloaded successfully");
        setPdfFormOption({
          pdfName: "",
          docName: "",
          customerName: "",
          supplierName: "",
          selectedInvoice: [],
          selectedId: "",
        });
        resetAllFields();
        setPdfPolicy({
          ...pdfPolicy,
          selectCustomer: false,
          selectSupplier: false,
          selectChildDoctype: false,
        });
      } else {
        toast.error(response.errors?.[0]?.message || "Something went wrong");
      }
      setLoading(false);
    } catch (error) {
      console.error("PDF download error:", error);
      setLoading(false);
    }
  };

  const { data: docNameList } = useFrappeGetDocList(pdfPolicy.parentDoctype || "", {
    orFilters: [["name", "like", `%${docSearchValue}%`]],
    limit: 10,
    fields: ["name"],
  });

  const doclistArray = docNameList && docNameList.length > 0 ? docNameList : [];

  // Build customer options from policy-defined fields in the fetched document
  const customerOptions = (() => {
    const fields = pdfPolicy.CUSTOMER_FIELDS;
    if (!fields || fields.length === 0 || Object.keys(docTypeData).length === 0) return [];
    const values = [
      ...new Set(
        fields.map((field) => (docTypeData as any)[field]).filter(Boolean)
      ),
    ];
    return values.map((v: string) => ({ value: v, label: v }));
  })();

  // Build supplier options from child doctype data
  const childData: any =
    pdfPolicy.CHILD_DOCTYPE && docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData]
      ? docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData]
      : null;

  const supplierList =
    childData && Array.isArray(childData)
      ? [...new Set(childData.map((c: any) => c.supplier).filter(Boolean))]
      : [];

  const supplierOptions = supplierList.map((c: any) => ({ value: c, label: c }));

  // Sync docSearchValue when docName is cleared externally
  useEffect(() => {
    if (!pdfFormOption.docName && docSearchValue) {
      setDocSearchValue("");
    }
  }, [pdfFormOption.docName]);

  // Auto-select Document Name on exact API match — fixes paste UX
  useEffect(() => {
    if (!docSearchValue || pdfFormOption.docName === docSearchValue) return;
    const exactMatch = doclistArray.find(
      (doc: any) => doc.name.toLowerCase() === docSearchValue.trim().toLowerCase()
    );
    if (exactMatch) {
      setDocSearchValue(exactMatch.name);
      setPdfFormOption((prev) => ({ ...prev, docName: exactMatch.name }));
    }
  }, [doclistArray]);

  // Auto-select Customer on blur if pasted value exactly matches an option
  const handleCustomerBlur = () => {
    if (!customerSearchVal || pdfFormOption.customerName) return;
    const match = customerOptions.find(
      (opt) => opt.value.toLowerCase() === customerSearchVal.trim().toLowerCase()
    );
    if (match) {
      setPdfFormOption((prev) => ({ ...prev, customerName: match.value }));
      setCustomerSearchVal("");
    }
  };

  // Auto-select Supplier on blur if pasted value exactly matches an option
  const handleSupplierBlur = () => {
    if (!supplierSearchVal || pdfFormOption.supplierName) return;
    const match = supplierOptions.find(
      (opt) => opt.value.toLowerCase() === supplierSearchVal.trim().toLowerCase()
    );
    if (match) {
      setPdfFormOption((prev) => ({ ...prev, supplierName: match.value }));
      setSupplierSearchVal("");
    }
  };

  const pdfNames = Object.values(PDF_NAME_LIST);

  return (
    <Card
      style={{
        maxWidth: 620,
        margin: "0 auto",
        borderRadius: 12,
        boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
        border: "1px solid #e8e8e8",
        overflow: "hidden",
      }}
      styles={{ body: { padding: 0 } }}
    >
      {/* Header */}
      <div
        style={{
          background: "linear-gradient(135deg, #1677ff 0%, #0958d9 100%)",
          padding: "20px 28px",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <FilePdfOutlined style={{ fontSize: 28, color: "#fff" }} />
        <div>
          <Title level={4} style={{ color: "#fff", margin: 0, lineHeight: 1.3 }}>
            PDF Download
          </Title>
          <Text style={{ color: "rgba(255,255,255,0.78)", fontSize: 13 }}>
            Select a document type and fill in the details
          </Text>
        </div>
      </div>

      {/* Form Body */}
      <div style={{ padding: "24px 28px 28px" }}>
        <Form layout="vertical" onFinish={handleSubmit}>

          {/* PDF Type Section */}
          <Divider orientation="left" orientationMargin={0} style={{ marginTop: 0, marginBottom: 12 }}>
            <Text strong style={{ fontSize: 13, color: "#555" }}>
              <FileTextOutlined style={{ marginRight: 6 }} />
              Select PDF Type
            </Text>
          </Divider>

          <Form.Item required style={{ marginBottom: 20 }}>
            <Row gutter={[8, 8]}>
              {pdfNames.map((name) => {
                const isSelected = pdfFormOption.pdfName === name;
                return (
                  <Col span={pdfNames.length > 5 ? 12 : 24} key={name}>
                    <div
                      onClick={() => handlePdfNameChange(name)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "9px 14px",
                        borderRadius: 8,
                        border: `1.5px solid ${isSelected ? "#1677ff" : "#d9d9d9"}`,
                        background: isSelected ? "#e6f4ff" : "#fafafa",
                        cursor: "pointer",
                        transition: "all 0.18s",
                        userSelect: "none",
                      }}
                    >
                      <Checkbox
                        checked={isSelected}
                        onChange={() => handlePdfNameChange(name)}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <Text
                        style={{
                          fontSize: 13,
                          color: isSelected ? "#1677ff" : "#333",
                          fontWeight: isSelected ? 500 : 400,
                        }}
                      >
                        {name}
                      </Text>
                    </div>
                  </Col>
                );
              })}
            </Row>
          </Form.Item>

          {/* Document Details Section */}
          <Divider orientation="left" orientationMargin={0} style={{ marginBottom: 12 }}>
            <Text strong style={{ fontSize: 13, color: "#555" }}>
              <SearchOutlined style={{ marginRight: 6 }} />
              Document Details
            </Text>
          </Divider>

          {/* Document Name — supports paste via auto-select on exact API match */}
          <AntSelect
            label="Document Name"
            placeholder="Type or paste document name…"
            value={docSearchValue || undefined}
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
            allowClear={true}
            disabled={!pdfPolicy.selectDocName}
            required={pdfPolicy.selectDocName}
            options={doclistArray?.map((doc: any) => ({ value: doc.name, label: doc.name })) || []}
            notFoundContent={docSearchValue ? "No documents found" : "Start typing to search…"}
          />

          {/* Customer — supports paste via filterOption + onBlur auto-select */}
          <AntSelect
            label={
              <span>
                <UserOutlined style={{ marginRight: 5 }} />
                Customer
              </span>
            }
            placeholder="Type or paste customer name…"
            value={pdfFormOption.customerName || undefined}
            onChange={(value: string) => {
              setCustomerSearchVal("");
              setPdfFormOption({ ...pdfFormOption, customerName: value });
            }}
            onSearch={(val) => setCustomerSearchVal(val)}
            onBlur={handleCustomerBlur}
            showSearch={true}
            filterOption={(input, option) =>
              (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
            }
            allowClear={true}
            disabled={!pdfPolicy.selectCustomer}
            required={pdfPolicy.selectCustomer}
            options={customerOptions}
            notFoundContent="No customers found"
          />

          {/* Supplier — supports paste via filterOption + onBlur auto-select */}
          <AntSelect
            label={
              <span>
                <ShopOutlined style={{ marginRight: 5 }} />
                Supplier
              </span>
            }
            placeholder="Type or paste supplier name…"
            value={pdfFormOption.supplierName || undefined}
            onChange={(value: string) => {
              setSupplierSearchVal("");
              setPdfFormOption({ ...pdfFormOption, supplierName: value });
            }}
            onSearch={(val) => setSupplierSearchVal(val)}
            onBlur={handleSupplierBlur}
            showSearch={true}
            filterOption={(input, option) =>
              (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
            }
            allowClear={true}
            disabled={!pdfPolicy.selectSupplier}
            required={pdfPolicy.selectSupplier}
            options={supplierOptions}
            notFoundContent="No suppliers found"
          />

          {/* Download Button */}
          <Form.Item style={{ marginBottom: 0, marginTop: 8 }}>
            <AntButton
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<DownloadOutlined />}
              size="large"
              style={{
                width: "100%",
                height: 48,
                borderRadius: 8,
                fontSize: 15,
                fontWeight: 500,
              }}
            >
              {loading ? "Processing…" : "Download PDF"}
            </AntButton>
          </Form.Item>

        </Form>
      </div>
    </Card>
  );
};

export default PdfForm;
