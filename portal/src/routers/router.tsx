import { createBrowserRouter } from "react-router-dom";
import MainLayout from "../layout/mainLayout/MainLayout";
import PdfDownload from "../pages/PdfDownload";

export const router = createBrowserRouter([
    {
        element: <MainLayout />,
        children: [
            {
                path: "/",
                element: <PdfDownload />
            },
            {
                path: "/about",
                element: <div>About</div>
            },
            {
                path: "/contact",
            }
        ]
    },
],{
    basename:"/portal"
})
