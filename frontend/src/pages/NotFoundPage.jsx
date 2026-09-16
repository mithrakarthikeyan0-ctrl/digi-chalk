import React from 'react';
import { Link } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';

export const NotFoundPage = () => {
  return (
    <AppShell>
      <div style={{ padding: '40px 20px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '32px', marginBottom: '16px' }}>404 - Not Found</h1>
        <p style={{ marginBottom: '24px' }}>The page you are looking for doesn't exist.</p>
        <Link to="/" className="btn btn-primary">Go Home</Link>
      </div>
    </AppShell>
  );
};
