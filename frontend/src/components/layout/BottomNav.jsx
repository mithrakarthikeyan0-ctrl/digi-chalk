import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, HelpCircle, Film, User } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const BottomNav = () => {
  const { role } = useApp();
  
  return (
    <nav className="bottomnav" aria-label="Main navigation">
      <NavLink to={`/${role === 'student' ? 'student' : role === 'teacher' ? 'teacher' : role}`} className={({ isActive }) => isActive ? "active" : ""}>
        <Home size={22} />
        Home
      </NavLink>
      {role === 'student' && (
        <>
          <NavLink to="/quiz" className={({ isActive }) => isActive ? "active" : ""}>
            <HelpCircle size={22} />
            Quizzes
          </NavLink>
          <NavLink to="/reels" className={({ isActive }) => isActive ? "active" : ""}>
            <Film size={22} />
            Reels
          </NavLink>
        </>
      )}
      <button>
        <User size={22} />
        Profile
      </button>
    </nav>
  );
};
