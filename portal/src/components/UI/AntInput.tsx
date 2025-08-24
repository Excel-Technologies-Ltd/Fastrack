import React from 'react';
import { Input, Form } from 'antd';

interface AntInputProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  disabled?: boolean;
  type?: string;
  name?: string;
  style?: React.CSSProperties;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
}

const AntInput: React.FC<AntInputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  type = "text",
  name,
  style,
  prefix,
  suffix
}) => {
  const inputComponent = (
    <Input
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      type={type}
      name={name}
      style={style}
      prefix={prefix}
      suffix={suffix}
    />
  );

  if (label) {
    return (
      <Form.Item 
        label={label}
        required={required}
      >
        {inputComponent}
      </Form.Item>
    );
  }

  return inputComponent;
};

export default AntInput;
