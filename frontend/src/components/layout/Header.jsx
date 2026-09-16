import React from 'react';
import { Search, Bell, User } from 'lucide-react';
import { IconButton } from '../ui/Button';
import { useApp } from '../../context/AppContext';

export const Header = ({ title, subtitle }) => {
  const { role, notifications } = useApp();
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="topbar">
      <div>
        {subtitle && <div className="caption">{subtitle}</div>}
        {title && <h1 style={{ fontSize: '20px' }}>{title}</h1>}
      </div>
      <div className="topbar-actions">
        <IconButton aria-label="Search">
          <Search size={20} />
        </IconButton>
        <IconButton aria-label="Notifications" style={{ position: 'relative' }}>
          <Bell size={20} />
          {unreadCount > 0 && (
            <span style={{
              position: 'absolute', top: '0', right: '0', 
              width: '8px', height: '8px', background: 'var(--color-crimson)', 
              borderRadius: '50%'
            }}></span>
          )}
        </IconButton>
        <div className="avatar" tabIndex="0" role="button" aria-label="Profile and Settings">
          {role.charAt(0).toUpperCase()}
        </div>
      </div>
    </div>
  );
};
