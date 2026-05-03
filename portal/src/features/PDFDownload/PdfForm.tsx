import { useEffect, useState } from "react";
import { Checkbox, Form, Card, Typography, Divider } from "antd";
import {
  DownloadOutlined,
  FileTextOutlined,
  UserOutlined,
  ShopOutlined,
  FilePdfOutlined,
  SearchOutlined,
  UnorderedListOutlined,
} from "@ant-design/icons";
import { AntSelect, AntButton } from "../../components/UI";
import { PDF_NAME_LIST } from "../../constants/pdfName";
import { usePDFDownload } from "./PDFDownloadPorvider";
import { buildPdfPolicyForName } from "../../utils/pdfPolicy";
import { useDownloadPDF } from "./hooks/DownloadPDF";
import { validatePdfPolicy } from "../../utils/validateOption";
import {
  buildCustomerSelectOptions,
  buildSupplierSelectOptions,
} from "../../utils/pdfPickerOptions";
import { toast } from "react-toastify";
import { useFrappeGetDocList } from "frappe-react-sdk";
import { List } from "./List";

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
      setPdfPolicy(buildPdfPolicyForName(""));
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
      setPdfPolicy(buildPdfPolicyForName(selectedPdfName));
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

  const customerOptions = buildCustomerSelectOptions(
    docTypeData as Record<string, unknown>,
    pdfPolicy.CUSTOMER_FIELDS,
    pdfPolicy.CHILD_DOCTYPE,
  );

  const supplierOptions = buildSupplierSelectOptions(
    docTypeData as Record<string, unknown>,
    pdfPolicy.CHILD_DOCTYPE,
  );

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
        width: "100%",
        maxWidth: 1320,
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
      <div className="px-5 py-6 sm:px-7 sm:py-7">
        <Form layout="vertical" onFinish={handleSubmit}>
          <section className="mb-2">
            <Text strong style={{ fontSize: 14, color: "#333" }}>
              <FileTextOutlined style={{ marginRight: 8 }} />
              Select PDF type
            </Text>
            <p className="mb-3 mt-1 text-xs text-gray-500">
              Choose one report, then fill document details and invoice lines below.
            </p>
            <Form.Item required style={{ marginBottom: 0 }}>
              <div
                className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6"
                role="list"
              >
                {pdfNames.map((name) => {
                  const isSelected = pdfFormOption.pdfName === name;
                  return (
                    <div
                      key={name}
                      role="listitem"
                      onClick={() => handlePdfNameChange(name)}
                      className="min-w-0 rounded-lg border px-2.5 py-2 transition-all sm:px-3 sm:py-2.5"
                      style={{
                        borderColor: isSelected ? "#1677ff" : "#d9d9d9",
                        background: isSelected ? "#e6f4ff" : "#fafafa",
                        borderWidth: 1.5,
                        cursor: "pointer",
                        userSelect: "none",
                      }}
                    >
                      <div className="flex items-start gap-2">
                        <Checkbox
                          checked={isSelected}
                          onChange={() => handlePdfNameChange(name)}
                          onClick={(e) => e.stopPropagation()}
                          className="mt-0.5 shrink-0"
                        />
                        <Text
                          className="min-w-0 leading-snug"
                          style={{
                            fontSize: 12,
                            color: isSelected ? "#1677ff" : "#333",
                            fontWeight: isSelected ? 600 : 400,
                          }}
                        >
                          {name}
                        </Text>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Form.Item>
          </section>

          <Divider className="my-6" />

          <section>
            <Text strong style={{ fontSize: 14, color: "#333" }}>
              <SearchOutlined style={{ marginRight: 8 }} />
              Document details
            </Text>
            <div className="mt-3 w-full min-w-0 overflow-x-auto">
              <div className="flex w-full min-w-0 flex-row gap-4">
                <div className="min-w-0 flex-1 basis-0">
                  <AntSelect
                    label="Document Name"
                    placeholder="Type or paste document name…"
                    value={docSearchValue || undefined}
                    onChange={(value: string) => {
                      setDocSearchValue(value);
                      setPdfFormOption((prev) => ({ ...prev, docName: value }));
                    }}
                    onSearch={(value: string) => {
                      setDocSearchValue(value);
                      setPdfFormOption((prev) => {
                        if (prev.docName && value !== prev.docName) {
                          return { ...prev, docName: "" };
                        }
                        return prev;
                      });
                    }}
                    showSearch={true}
                    filterOption={false}
                    allowClear={true}
                    disabled={!pdfPolicy.selectDocName}
                    required={pdfPolicy.selectDocName}
                    options={
                      doclistArray?.map((doc: any) => ({
                        value: doc.name,
                        label: doc.name,
                      })) || []
                    }
                    notFoundContent={
                      docSearchValue
                        ? "No documents found"
                        : "Start typing to search…"
                    }
                  />
                </div>
                <div className="min-w-0 flex-1 basis-0">
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
                      setPdfFormOption((prev) => ({
                        ...prev,
                        customerName: value,
                      }));
                    }}
                    onSearch={(val) => setCustomerSearchVal(val)}
                    onBlur={handleCustomerBlur}
                    showSearch={true}
                    filterOption={(input, option) =>
                      (option?.label ?? "")
                        .toLowerCase()
                        .includes(input.toLowerCase())
                    }
                    allowClear={true}
                    disabled={!pdfPolicy.selectCustomer}
                    required={pdfPolicy.selectCustomer}
                    options={customerOptions}
                    notFoundContent="No customers found"
                  />
                </div>
                <div className="min-w-0 flex-1 basis-0">
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
                      setPdfFormOption((prev) => ({
                        ...prev,
                        supplierName: value,
                      }));
                    }}
                    onSearch={(val) => setSupplierSearchVal(val)}
                    onBlur={handleSupplierBlur}
                    showSearch={true}
                    filterOption={(input, option) =>
                      (option?.label ?? "")
                        .toLowerCase()
                        .includes(input.toLowerCase())
                    }
                    allowClear={true}
                    disabled={!pdfPolicy.selectSupplier}
                    required={pdfPolicy.selectSupplier}
                    options={supplierOptions}
                    notFoundContent="No suppliers found"
                  />
                </div>
              </div>
            </div>
          </section>

          {pdfPolicy.CHILD_DOCTYPE && pdfPolicy.parentDoctype ? (
            <>
              <Divider className="my-6" />
              <section>
                <Text strong style={{ fontSize: 14, color: "#333" }}>
                  <UnorderedListOutlined style={{ marginRight: 8 }} />
                  Invoice lines
                </Text>
                <p className="mb-2 mt-1 text-xs text-gray-500">
                  Select one or more rows when the report requires invoice IDs.
                </p>
                <List />
              </section>
            </>
          ) : null}

          <Divider className="my-6" />

          <Form.Item style={{ marginBottom: 0 }}>
            <AntButton
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<DownloadOutlined />}
              size="large"
              style={{
                width: "100%",
                maxWidth: 400,
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
