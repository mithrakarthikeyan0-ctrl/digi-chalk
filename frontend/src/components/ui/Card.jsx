import React from 'react';

export const Card = ({ children, className = '', ...props }) => (
  <div className={`card ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ title, actionLabel, actionOnClick }) => (
  <div className="card-title">
    <h2>{title}</h2>
    {actionLabel && (
      <button className="btn btn-outline" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={actionOnClick}>
        {actionLabel}
      </button>
    )}
  </div>
);
