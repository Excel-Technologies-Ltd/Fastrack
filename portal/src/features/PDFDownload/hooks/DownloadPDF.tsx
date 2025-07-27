import { usePDFDownload, type PdfFormOption } from "../PDFDownloadPorvider";
import { PDF_POLICY, type PDFPolicy } from "../../../utils/pdfPolicy";


interface ValidationError {
  field: string;
  message: string;
}

interface FrappeCallError {
  message: string;
}

export const useDownloadPDF = () => {
  const { pdfFormOption } = usePDFDownload();

  // Validate the form options


  // Prepare arguments for the API call
  const pdfPolicy = PDF_POLICY[pdfFormOption.pdfName] || ({} as PDFPolicy);
  const args = pdfPolicy.HAS_ARGUMENTS && pdfPolicy.ARGUMENTS ? pdfPolicy.ARGUMENTS : {};
  const argsMap = Object.entries(args).reduce((acc, [key, value]) => {
    acc[key] = pdfFormOption[value as keyof PdfFormOption];
    return acc;
  }, {} as Record<string, any>);

  // Initialize useFrappeGetCall
  

  const previewPdf = async (): Promise<{
    success: boolean;
    errors?: ValidationError[];
    apiError?: string;
  }> => {

    if (!pdfPolicy.DOWNLOAD_METHOD) {
      return {
        success: false,
        errors: [{ field: "downloadMethod", message: "Download method not specified in policy" }],
      };
    }

    try {
      const queryString = new URLSearchParams(argsMap).toString();

      const url = `/api/method/${pdfPolicy.DOWNLOAD_METHOD}?${queryString}`;
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);

      // Open the PDF in a new tab for preview
      window.open(downloadUrl, "_blank");

      // Clean up the blob URL after a short delay to ensure the browser has time to open it
      setTimeout(() => {
        window.URL.revokeObjectURL(downloadUrl);
      }, 1000);

      return { success: true };
    } catch (err) {
      const errorMessage = (err as FrappeCallError)?.message || "Failed to preview PDF";
      return {
        success: false,
        apiError: errorMessage,
      };
    }
  };

  return {
    previewPdf,

  };
};