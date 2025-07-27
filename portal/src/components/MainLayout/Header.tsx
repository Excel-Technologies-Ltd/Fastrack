

const Header = () => {
  return (
    <header style={{background: "linear-gradient(to right, #007bff, #00bfff)"}}  className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo Section */}
        <div className="flex items-center">
          {/* Replace this div with your actual logo image */}
          <div className="text-2xl font-bold tracking-tight">
            Fastrack Cargo Solution
          </div>
          {/* Uncomment and update with actual logo path when available */}
          {/* <img src="/path-to-logo.png" alt="Fastrack Cargo Solution Logo" className="h-12 w-auto" /> */}
        </div>

        {/* Navigation Links */}
        <nav className="space-x-6">
          <a href="#" className="hover:text-blue-200 transition-colors">Home</a>
          <a href="#" className="hover:text-blue-200 transition-colors">Services</a>
          <a href="#" className="hover:text-blue-200 transition-colors">About</a>
          <a href="#" className="hover:text-blue-200 transition-colors">Contact</a>
        </nav>
      </div>
    </header>
  );
};

export default Header;