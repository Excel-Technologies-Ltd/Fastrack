import React from "react";

type ButtonProps = {
  children: React.ReactNode;
  type?: "button" | "submit" | "reset";
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  color?: "primary" | "secondary" | "accent" | "neutral" | "info" | "success" | "warning" | "error";
};

const Button: React.FC<ButtonProps> = ({
  children,
  type = "button",
  onClick,
  className = "",
  disabled = false,
  color = "primary",
}) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled}
    className={`btn btn-${color} ${className}`}
    style={{fontSize: "10px", padding: "2px 10px"}}
  >
    {children}
  </button>
);

export default Button;
