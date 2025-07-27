

const Footer = () => {
  return (
    <footer style={{background: "linear-gradient(to right, #007bff, #00bfff)"}}  className="text-white py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          {/* Logo Section */}
          <div className="mb-4 md:mb-0">
            {/* Replace this div with your actual logo image */}
            <div className="text-xl font-bold tracking-tight">
              Fastrack Cargo Solution
            </div>
            {/* Uncomment and update with actual logo path when available */}
            {/* <img src="/path-to-logo.png" alt="Fastrack Cargo Solution Logo" className="h-10 w-auto" /> */}
          </div>

          {/* Navigation Links */}
          <div className="flex space-x-6 mb-4 md:mb-0">
            <a href="#" className="hover:text-blue-200 transition-colors">Home</a>
            <a href="#" className="hover:text-blue-200 transition-colors">Services</a>
            <a href="#" className="hover:text-blue-200 transition-colors">About</a>
            <a href="#" className="hover:text-blue-200 transition-colors">Contact</a>
          </div>

          {/* Contact Info */}
          <div className="text-center md:text-right">
            <p>Email: info@fastrackcargo.com</p>
            <p>Phone: +1 (123) 456-7890</p>
            <p>Address: 123 Cargo Lane, City, Country</p>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-6 text-center text-sm border-t border-blue-500 pt-4">
          &copy; {new Date().getFullYear()} Fastrack Cargo Solution. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;