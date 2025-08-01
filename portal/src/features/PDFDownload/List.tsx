import  { useState, useEffect } from "react";
import { DOCTYPE_LIST } from "../../constants/Doctype";
import { usePDFDownload } from "./PDFDownloadPorvider";

export const List = () => {
    const { docTypeData, errorObj, pdfPolicy, pdfFormOption,setPdfFormOption } = usePDFDownload();
    // const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [selectAll, setSelectAll] = useState(false);
    const selectedIds = pdfFormOption?.selectedId ? pdfFormOption?.selectedId.split(",").filter(id => id.trim()) : [];

    // Get child data
    let childData: any = pdfPolicy.CHILD_DOCTYPE && docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData] 
        ? docTypeData[pdfPolicy.CHILD_DOCTYPE as keyof typeof docTypeData] 
        : [];
    // if customer select then filter by customer
    console.log("pdfFormOption", childData);
    if(pdfPolicy.selectCustomer && pdfFormOption.customerName){
        childData = childData.filter((row: any) => row.customer === pdfFormOption.customerName);
    }
    // if supplier select then filter by supplier
    if(pdfPolicy.selectSupplier && pdfFormOption.supplierName){
        childData = childData.filter((row: any) => row.supplier === pdfFormOption.supplierName);
    }

    // Handle select all checkbox
    const handleSelectAll = (checked: boolean) => {
        setSelectAll(checked);
        if (checked && childData) {
            // Get all name values
            const allIds = childData
                .map((row: any) => row.name)
                .filter((id: any) => id);
            setPdfFormOption((prev) => ({
                ...prev,
                selectedId: allIds.join(",")
            }));
        } else {
            setPdfFormOption((prev) => ({
                ...prev,
                selectedId: ""
            }));
        }
    };

    // Handle individual checkbox
    const handleSelectOne = (name: string, checked: boolean) => {
        if (checked) {
            const newSelectedIds = [...selectedIds, name];
            setPdfFormOption((prev) => ({
                ...prev,
                selectedId: newSelectedIds.join(",")
            }));
        } else {
            const newSelectedIds = selectedIds.filter(id => id.trim() !== name.trim());
            setPdfFormOption((prev) => ({
                ...prev,
                selectedId: newSelectedIds.length > 0 ? newSelectedIds.join(",") : ""
            }));
            setSelectAll(false); // Uncheck select all if individual item is unchecked
        }
    };

    // Update select all state when selectedIds change
    useEffect(() => {
        if (childData && Array.isArray(childData) && selectedIds.length > 0) {
            const allNames = childData
                .map((row: any) => row.name)
                .filter((id: any) => id);
            
            if (allNames.length > 0 && selectedIds.length === allNames.length && selectedIds.length > 0) {
                setSelectAll(true);
            } else {
                setSelectAll(false);
            }
        }
    }, [selectedIds, childData]);

    // Reset selected items when child data changes
    useEffect(() => {
        setPdfFormOption((prev) => ({
            ...prev,
            selectedId: ""
        }));
        setSelectAll(false);
    }, [pdfPolicy.CHILD_DOCTYPE,pdfFormOption.docName]);

    // Update select all state when individual items change - now at top level
    // set array as string join by comma
    // useEffect(() => {
    //     if (childData && Array.isArray(childData)) {
    //         const allInvoiceLinks = childData
    //             .map((row: any) => row.invoice_link)
    //             .filter((id: any) => id);
            
    //         if (allInvoiceLinks.length > 0 && selectedIds.length === allInvoiceLinks.length) {
    //             setSelectAll(true);
    //         } else {
    //             setSelectAll(false);
    //         }
    //     }
    //     if(selectedIds.length > 0){
    //         setPdfFormOption((prev)=>({...prev,selectedId:selectedIds.join(",")}));
    //     }
    // }, [selectedIds, childData]);
    // if pdfFormOption.selectedId is empty clear selectedIds
    // useEffect(() => {
    //     if(pdfFormOption.selectedId){
    //         setSelectedIds([]);
    //         setSelectAll(false);
    //     }
    // }, [pdfFormOption.selectedId]);

    // Reset selected items when child data changes
    // useEffect(() => {
    //     setSelectedIds([]);
    //     setSelectAll(false);
    // }, [pdfPolicy.CHILD_DOCTYPE]);

    if (pdfPolicy.CHILD_DOCTYPE && childData) {
        const columnMap = getChildDocTypeColumnMap(
            pdfPolicy.parentDoctype, 
            pdfPolicy.CHILD_DOCTYPE, 
            docTypeData
        );

        return (
            <div className="mt-10 " style={{fontSize: "10px"}}>
                {/* Error display */}
                {errorObj?.docNameError && pdfPolicy.CHILD_DOCTYPE && pdfFormOption.docName && (
                    <div className="text-red-500 mb-4">{errorObj?.docNameError}</div>
                )}
                
                {/* Selected IDs display for debugging */}
                {selectedIds.length > 0 && (
                    <div className="mb-4 p-2 bg-blue-50 rounded">
                        <strong>Selected IDs:</strong> {JSON.stringify(selectedIds)}
                    </div>
                )}
                
                {/* Table */}
                {Array.isArray(childData) && childData?.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full border-collapse border border-gray-300">
                            <thead>
                                <tr className="bg-gray-100">
                                    <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                                        <input
                                            type="checkbox"
                                            checked={selectAll}
                                            onChange={(e) => handleSelectAll(e.target.checked)}
                                            className="mr-2"
                                            disabled={!pdfPolicy.selectChildDoctype}
                                        />
                                        Select All
                                    </th>
                                    {columnMap?.map((column, index) => (
                                        <th 
                                            key={index} 
                                            className="border border-gray-300 px-4 py-2 text-left font-semibold"
                                        >
                                            {column.label}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {childData.map((row: any, rowIndex: number) => (
                                    <tr key={rowIndex} className="hover:bg-gray-50">
                                        <td className="border border-gray-300 px-4 py-2">
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(row.name)}
                                                onChange={(e) => handleSelectOne(row.name, e.target.checked)}
                                                disabled={!pdfPolicy.selectChildDoctype} // Disable if no invoice_link
                                            />
                                        </td>
                                        {columnMap?.map((column, colIndex) => (
                                            <td 
                                                key={colIndex} 
                                                className="border border-gray-300 px-4 py-2"
                                            >
                                                {row[column.name] || '-'}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-gray-500">{""}</div>
                )}
            </div>
        );
    }

    return (
        <div className="mt-10">
            {/* <div>Debug: {JSON.stringify(docTypeData)}</div> */}
            {errorObj?.docNameError && pdfPolicy.CHILD_DOCTYPE && pdfFormOption.docName && (
                <div className="text-red-500">{errorObj?.docNameError}</div>
            )}
        </div>
    );
};

const getChildDocTypeColumnMap = (docType: string, childDocType: string, docTypeData: any) => {
    const childDocTypeData = docTypeData[childDocType as keyof typeof docTypeData];
    if (!childDocTypeData) return [];

    // Find the correct docType key in DOCTYPE_LIST
    const docTypeKey = Object.keys(DOCTYPE_LIST).find(key => 
        DOCTYPE_LIST[key as keyof typeof DOCTYPE_LIST].NAME === docType
    );
    
    if (!docTypeKey) return [];

    const doctypeConfig = DOCTYPE_LIST[docTypeKey as keyof typeof DOCTYPE_LIST];
    
    // Find the correct child doctype key
    const childDocTypeKey = Object.keys(doctypeConfig.CHILD_DOCTYPE).find(key =>
        doctypeConfig.CHILD_DOCTYPE[key as keyof typeof doctypeConfig.CHILD_DOCTYPE].name === childDocType
    );
    
    if (!childDocTypeKey) return [];

    const columnMap = doctypeConfig.CHILD_DOCTYPE[childDocTypeKey as keyof typeof doctypeConfig.CHILD_DOCTYPE].fields.map((field: any) => ({
        name: field.name,
        label: field.label,
    }));
    
    return columnMap;
};