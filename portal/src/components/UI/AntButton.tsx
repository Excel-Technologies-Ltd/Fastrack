import React from 'react';
import { Button } from 'antd';

interface AntButtonProps {
  children: React.ReactNode;
  type?: 'primary' | 'ghost' | 'dashed' | 'link' | 'text' | 'default';
  htmlType?: 'button' | 'submit' | 'reset';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  size?: 'large' | 'middle' | 'small';
  onClick?: () => void;
  style?: React.CSSProperties;
  className?: string;
}

const AntButton: React.FC<AntButtonProps> = ({
  children,
  type = 'default',
  htmlType = 'button',
  loading = false,
  disabled = false,
  icon,
  size = 'middle',
  onClick,
  style,
  className
}) => {
  return (
    <Button
      type={type}
      htmlType={htmlType}
      loading={loading}
      disabled={disabled}
      icon={icon}
      size={size}
      onClick={onClick}
      style={style}
      className={className}
    >
      {children}
    </Button>
  );
};

export default AntButton;
