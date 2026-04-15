import React from 'react';
import { Select, Form } from 'antd';

interface Option {
  value: string;
  label: string;
}

interface AntSelectProps {
  label?: React.ReactNode;
  placeholder?: string;
  value?: string;
  options?: Option[];
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  onBlur?: () => void;
  required?: boolean;
  disabled?: boolean;
  showSearch?: boolean;
  filterOption?: boolean | ((inputValue: string, option: Option | undefined) => boolean);
  notFoundContent?: React.ReactNode;
  allowClear?: boolean;
  style?: React.CSSProperties;
}

const AntSelect: React.FC<AntSelectProps> = ({
  label,
  placeholder = "Select an option",
  value,
  options = [],
  onChange,
  onSearch,
  onBlur,
  required = false,
  disabled = false,
  showSearch = false,
  filterOption = true,
  notFoundContent = "No options found",
  allowClear = false,
  style,
}) => {
  const selectComponent = (
    <Select
      placeholder={placeholder}
      value={value || undefined}
      onChange={(val) => onChange?.(val ?? "")}
      onSearch={onSearch}
      onBlur={onBlur}
      disabled={disabled}
      showSearch={showSearch}
      filterOption={filterOption as any}
      notFoundContent={notFoundContent}
      allowClear={allowClear}
      style={{ width: '100%', ...style }}
      options={options}
    />
  );

  if (label) {
    return (
      <Form.Item
        label={label}
        required={required}
        style={{ marginBottom: 16 }}
      >
        {selectComponent}
      </Form.Item>
    );
  }

  return selectComponent;
};

export default AntSelect;
