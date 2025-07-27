import { List } from "./List";
import { PDFDownloadProvider } from "./PDFDownloadPorvider";
import PdfForm from "./PdfForm";

export default function PDFDownload() {
    return (
          <PDFDownloadProvider>
            <div className="flex gap-4 p-4 justify-between">
                <div className="w-2/5">
                    <PdfForm />
                </div>
                <div className="w-3/5">
                    <List />
                </div>
            </div>
          </PDFDownloadProvider>
    )
}