import { PDFDownloadProvider } from "./PDFDownloadPorvider";
import PdfForm from "./PdfForm";

export default function PDFDownload() {
  return (
    <PDFDownloadProvider>
      <div className="w-full px-4 py-6 sm:px-6 lg:px-8">
        <PdfForm />
      </div>
    </PDFDownloadProvider>
  );
}