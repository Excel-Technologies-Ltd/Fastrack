import React, { useState, useRef, useEffect } from 'react';
import { Search, X, ChevronDown } from 'lucide-react';

interface Option {
  value: string;
  label: string;
}

interface SearchableInputProps {
  name?: string;
  label?: string;
  placeholder?: string;
  value?: string;
  options?: Option[];
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSelect?: (value: string) => void;
  onInputChange?: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
  searchable?: boolean;
  maxResults?: number;
  className?: string;
  error?: string;
}

const SearchableInput: React.FC<SearchableInputProps> = ({
  name,
  label,
  placeholder = "Search...",
  value = "",
  options = [],
  onChange,
  onSelect,
  onInputChange,
  required = false,
  disabled = false,
  searchable = true,
  maxResults = 10,
  className = "",
  error
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filteredOptions, setFilteredOptions] = useState<Option[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter options based on input value
  useEffect(() => {
    console.log("SearchableInput - value:", value);
    console.log("SearchableInput - options:", options);
    console.log("SearchableInput - searchable:", searchable);
    
    let filtered: Option[] = [];
    
    if (!searchable) {
      filtered = options.slice(0, maxResults);
    } else {
      if (value.trim() === '') {
        filtered = options.slice(0, maxResults);
      } else {
        filtered = options.filter(option =>
          option.label.toLowerCase().includes(value.toLowerCase()) ||
          option.value.toLowerCase().includes(value.toLowerCase())
        ).slice(0, maxResults);
      }
    }
    
    setFilteredOptions(filtered);
    setHighlightedIndex(-1);
    
    console.log("SearchableInput - filteredOptions:", filtered);
  }, [value, options, maxResults, searchable]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    console.log("SearchableInput - handleInputChange called with:", inputValue);
    onChange?.(e);
    onInputChange?.(inputValue);        
    if (!isOpen && inputValue) {
      setIsOpen(true);
    }
  };

  // Handle option selection
  const handleOptionSelect = (option: Option) => {
    console.log("Selected option:", option);
    
    // Update the input value with the selected option's label
    const syntheticEvent = {
      target: { value: option.label, name }
    } as React.ChangeEvent<HTMLInputElement>;
    
    onChange?.(syntheticEvent);
    onInputChange?.(option.label);
    onSelect?.(option.value);
    
    setIsOpen(false);
    setHighlightedIndex(-1);
    inputRef.current?.blur();
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return;

    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        e.preventDefault();
        setIsOpen(true);
        return;
      }
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < filteredOptions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && filteredOptions[highlightedIndex]) {
          handleOptionSelect(filteredOptions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        inputRef.current?.blur();
        break;
      case 'Tab':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Clear input
  const handleClear = () => {
    const fakeEvent = {
      target: { value: '', name }
    } as React.ChangeEvent<HTMLInputElement>;
    
    onChange?.(fakeEvent);
    onInputChange?.('');
    onSelect?.('');
    setIsOpen(false);
    setHighlightedIndex(-1);
    inputRef.current?.focus();
  };

  // Handle input focus
  const handleFocus = () => {
    if (!disabled && options.length > 0) {
      setIsOpen(true);
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Label */}
      {label && (
        <label className="block font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative" ref={dropdownRef}>
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-gray-400" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          name={name}
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`
            w-full pl-10 pr-12 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
            ${error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
          `}
          autoComplete="off"
        />
        
        <div className="absolute inset-y-0 right-0 flex items-center">
          {value && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 mr-1 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="h-4 w-4 text-gray-400" />
            </button>
          )}
          <div className="pr-3">
            <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {/* Dropdown */}
      {isOpen && !disabled && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {filteredOptions.length > 0 ? (
            <ul className="py-1">
              {filteredOptions.map((option, index) => (
                <li key={`${option.value}-${index}`}>
                  <button
                    type="button"
                    onClick={() => handleOptionSelect(option)}
                    className={`
                      w-full text-left px-4 py-2 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none transition-colors
                      ${index === highlightedIndex ? 'bg-blue-50' : ''}
                    `}
                  >
                    <span className="block truncate">{option.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-3 text-gray-500 text-sm">
              {value ? `No results found for "${value}"` : 'Start typing to search...'}
            </div>
          )}
        </div>
      )}
    </div>
  );
};


export default SearchableInput;