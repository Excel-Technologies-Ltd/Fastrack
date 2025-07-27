import React from "react";

type Option = {
  value: string | number;
  label: string;
};

type SelectProps = {
  label?: string;
  options: Option[];
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  name?: string;
  className?: string;
  required?: boolean;
  disabled?: boolean;
};

const Select: React.FC<SelectProps> = ({
  label,
  options,
  value,
  onChange,
  name,
  className = "",
  required = false,
  disabled = false,
}) => (
  <div className={`form-control ${className}`}>
    {label && <label className="label"><span className="label-text">{label}</span></label>}
    <select
      className="select select-bordered w-full input-primary"
      value={value}
      onChange={onChange}
      name={name}
      required={required}
      disabled={disabled}
    >
      <option value="" disabled hidden>Select an option</option>
      {options?.map((opt:Option) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  </div>
);

export default Select;
