import React from 'react';

export const Badge = ({ children, variant = 'good', className = '' }) => (
  <span className={`badge badge-${variant} ${className}`}>
    {children}
  </span>
);
