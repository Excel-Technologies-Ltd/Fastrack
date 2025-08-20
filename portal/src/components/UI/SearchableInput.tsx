import React, { useState, useRef, useEffect } from "react";

type Option = {
  value: string;
  label: string;
};

type InputProps = {
  label?: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  name?: string;
  className?: string;
  required?: boolean;
  disabled?: boolean;
  // New props for searchable select
  searchable?: boolean;
  options?: Option[];
  onSelect?: (value: string) => void;
};

const SearchableInput: React.FC<InputProps> = ({
  label,
  type = "text",
  placeholder = "",
  value,
  onChange,
  name,
  className = "",
  required = false,
  disabled = false,
  searchable = false,
  options = [],
  onSelect,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredOptions, setFilteredOptions] = useState<Option[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update search term when value changes externally
  useEffect(() => {
    if (value && !searchTerm) {
      const selectedOption = options.find(option => option.value === value);
      if (selectedOption) {
        setSearchTerm(selectedOption.label);
      } else {
        setSearchTerm(value);
      }
    }
  }, [value, options]); // Remove searchTerm from dependencies

  // Filter options based on search term
  useEffect(() => {
    if (searchable && options.length > 0) {
      const filtered = options.filter(option =>
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredOptions(filtered);
    } else {
      setFilteredOptions(options);
    }
  }, [searchTerm, options, searchable]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    
    if (searchable) {
      setSearchTerm(inputValue);
      setIsOpen(true);
    }
    
    if (onChange) {
      onChange(e);
    }
  };

  const handleOptionSelect = (option: Option) => {
    setSearchTerm(option.label);
    setIsOpen(false);
    
    if (onSelect) {
      onSelect(option.value);
    }
    
    // Create a synthetic event to maintain compatibility
    if (onChange) {
      const syntheticEvent = {
        target: { value: option.value, name }
      } as React.ChangeEvent<HTMLInputElement>;
      onChange(syntheticEvent);
    }
  };

  const handleInputFocus = () => {
    if (searchable && options.length > 0) {
      setIsOpen(true);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!searchable || !isOpen) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      // Focus first option or next option
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      // Focus previous option
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filteredOptions.length > 0) {
        handleOptionSelect(filteredOptions[0]);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  if (searchable) {
    return (
      <div className={`form-control relative ${className}`} ref={dropdownRef}>
        {label && (
          <label className="label">
            <span className="label-text">{label}</span>
          </label>
        )}
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            placeholder={placeholder}
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onKeyDown={handleKeyDown}
            name={name}
            required={required}
            disabled={disabled}
            className="input input-bordered w-full input-primary pr-10"
            style={{ fontSize: "10px" }}
            autoComplete="off"
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg
              className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        
        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option, index) => (
                <div
                  key={`${option.value}-${index}`}
                  className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                  style={{ fontSize: "10px" }}
                  onClick={() => handleOptionSelect(option)}
                >
                  {option.label}
                </div>
              ))
            ) : (
              <div className="px-3 py-2 text-gray-500 text-sm" style={{ fontSize: "10px" }}>
                No options found
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // Regular input fallback
  return (
    <div className={`form-control ${className}`}>
      {label && (
        <label className="label">
          <span className="label-text">{label}</span>
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        name={name}
        required={required}
        disabled={disabled}
        className="input input-bordered w-full input-primary"
        style={{ fontSize: "10px" }}
      />
    </div>
  );
};

export default SearchableInput;