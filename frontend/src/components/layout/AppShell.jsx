import React from 'react';
import '../../styles/components.css';

export const AppShell = ({ children }) => {
  return (
    <div className="app-shell">
      {children}
    </div>
  );
};
