import React from "react";

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
};

const Input: React.FC<InputProps> = ({
  label,
  type = "text",
  placeholder = "",
  value,
  onChange,
  name,
  className = "",
  required = false,
  disabled = false,
}) => (
  <div className={`form-control  ${className}`}>
    {label && <label className="label"><span className="label-text">{label}</span></label>}
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      name={name}
      required={required}
      disabled={disabled}
      className="input input-bordered w-full input-primary"
    />
  </div>
);

export default Input;
