import { Outlet } from "react-router-dom";
// import Header from "../../components/MainLayout/Header";
// import Footer from "../../components/MainLayout/Footer";


export default function MainLayout() {
  const redirectToDesk = () => {
    window.location.href = "/app"; // or your custom desk URL
  };
  return (
    <div className="">
      {/* <Header /> */}
     
      {/* <Footer /> */}
      <div className="flex flex-col min-h-screen bg-white text-gray-900">
      {/* Header */}

      {/* Main Content */}
      <main className="flex-1 p-6"> <Outlet /></main>
    </div>
    </div>
  )
}