import React from 'react';
import { Select, Form } from 'antd';

interface Option {
  value: string;
  label: string;
}

interface AntSelectProps {
  label?: string;
  placeholder?: string;
  value?: string;
  options?: Option[];
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  required?: boolean;
  disabled?: boolean;
  showSearch?: boolean;
  filterOption?: boolean;
  notFoundContent?: string;
  style?: React.CSSProperties;
}

const AntSelect: React.FC<AntSelectProps> = ({
  label,
  placeholder = "Select an option",
  value,
  options = [],
  onChange,
  onSearch,
  required = false,
  disabled = false,
  showSearch = false,
  filterOption = true,
  notFoundContent = "No options found",
  style
}) => {
  const selectComponent = (
    <Select
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onSearch={onSearch}
      disabled={disabled}
      showSearch={showSearch}
      filterOption={filterOption}
      notFoundContent={notFoundContent}
      style={style}
      options={options}
    />
  );

  if (label) {
    return (
      <Form.Item 
        label={label}
        required={required}
      >
        {selectComponent}
      </Form.Item>
    );
  }

  return selectComponent;
};

export default AntSelect;
