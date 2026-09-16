import React, { createContext, useContext, useState, useEffect } from 'react';
import { INITIAL_NOTIFICATIONS } from '../data/demoData';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Read initial from localStorage or use defaults
  const readLocal = (key, def) => {
    try {
      const val = localStorage.getItem(`digichalk_${key}`);
      return val ? JSON.parse(val) : def;
    } catch (e) {
      return def;
    }
  };

  const setLocal = (key, val) => {
    try {
      localStorage.setItem(`digichalk_${key}`, JSON.stringify(val));
    } catch (e) {
      console.warn("LocalStorage failed", e);
    }
  };

  const [role, setRoleState] = useState(() => readLocal('user_role', 'student'));
  const [lang, setLangState] = useState(() => readLocal('lang', 'en'));
  const [textSize, setTextSizeState] = useState(() => readLocal('textSize', false));
  const [lowBandwidth, setLowBandwidthState] = useState(() => readLocal('lowBandwidth', false));
  const [notifications, setNotificationsState] = useState(() => readLocal('notifications', INITIAL_NOTIFICATIONS));
  const [selectedChild, setSelectedChild] = useState('aditi');
  
  // Session/Timer state
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);

  // Update localStorage when state changes
  const setRole = (r) => { setRoleState(r); setLocal('user_role', r); };
  const setLang = (l) => { setLangState(l); setLocal('lang', l); };
  const setTextSize = (s) => { setTextSizeState(s); setLocal('textSize', s); };
  const setLowBandwidth = (b) => { setLowBandwidthState(b); setLocal('lowBandwidth', b); };
  const setNotifications = (n) => { setNotificationsState(n); setLocal('notifications', n); };

  const markNotifRead = (id) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  };
  const clearNotifs = () => setNotifications([]);

  // Global Timer effect
  useEffect(() => {
    let interval = null;
    if (isSessionActive) {
      interval = setInterval(() => {
        setSessionSeconds((s) => s + 1);
      }, 1000);
    } else if (!isSessionActive && sessionSeconds !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isSessionActive, sessionSeconds]);

  // Apply global text size
  useEffect(() => {
    if (textSize) {
      document.body.classList.add('text-large');
    } else {
      document.body.classList.remove('text-large');
    }
  }, [textSize]);

  const resetAllData = () => {
    const keys = Object.keys(localStorage);
    keys.forEach(k => {
      if (k.startsWith('digichalk_')) {
        localStorage.removeItem(k);
      }
    });
    window.location.reload();
  };

  const value = {
    role, setRole,
    lang, setLang,
    textSize, setTextSize,
    lowBandwidth, setLowBandwidth,
    notifications, setNotifications, markNotifRead, clearNotifs,
    selectedChild, setSelectedChild,
    isSessionActive, setIsSessionActive,
    sessionSeconds, setSessionSeconds,
    resetAllData
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
