import React from 'react';

export const Button = ({ children, variant = 'primary', className = '', block, huge, ...props }) => {
  const baseClass = huge ? 'btn-huge' : 'btn';
  const variantClass = variant !== 'default' ? `btn-${variant}` : '';
  const blockClass = block ? 'btn-block' : '';
  
  return (
    <button className={`${baseClass} ${variantClass} ${blockClass} ${className}`.trim()} {...props}>
      {children}
    </button>
  );
};

export const IconButton = ({ children, className = '', ...props }) => (
  <button className={`btn-icon ${className}`} {...props}>
    {children}
  </button>
);
