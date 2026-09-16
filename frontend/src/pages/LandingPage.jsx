import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, GraduationCap, Users, BarChart3 } from 'lucide-react';
import { AppShell } from '../components/layout/AppShell';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { setRole } = useApp();

  const handleRoleSelect = (role) => {
    setRole(role);
    if (role === 'teacher') navigate('/teacher');
    else if (role === 'student') navigate('/student');
    else if (role === 'parent') navigate('/parent');
    else if (role === 'headmaster') navigate('/headmaster');
  };

  return (
    <AppShell>
      <div className="topbar" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '4px', paddingTop: '36px' }}>
        <div className="row-between" style={{ width: '100%', alignItems: 'flex-end' }}>
          <h1 style={{ fontSize: '28px', letterSpacing: '-0.02em' }}>Digi-Chalk</h1>
          <Badge variant="good" style={{ fontSize: '10px', border: '1px solid rgba(16, 185, 129, 0.4)', boxShadow: '0 2px 4px rgba(16, 185, 129, 0.1)' }}>
            Low-Bandwidth 2G/3G Ready
          </Badge>
        </div>
        <p className="caption" style={{ fontSize: '13px' }}>
          Pick your portal to continue &middot; Samarthya Smart Classroom
        </p>
      </div>

      <div className="main">
        <div className="role-grid">
          <div className="role-card" onClick={() => handleRoleSelect('teacher')} style={{ cursor: 'pointer' }}>
            <div className="icon-circle" style={{ background: '#FEF3C7', color: '#92400E' }}>
              <BookOpen size={20} strokeWidth={2} />
            </div>
            <div>
              <div className="role-title">Teacher</div>
              <div className="role-desc">Start sessions, bookmark topics, view scores</div>
            </div>
          </div>

          <div className="role-card" onClick={() => handleRoleSelect('student')} style={{ cursor: 'pointer' }}>
            <div className="icon-circle" style={{ background: '#D1FAE5', color: '#065F46' }}>
              <GraduationCap size={20} strokeWidth={2} />
            </div>
            <div>
              <div className="role-title">Student</div>
              <div className="role-desc">Lessons, quizzes, recaps and live board</div>
            </div>
          </div>

          <div className="role-card" onClick={() => handleRoleSelect('parent')} style={{ cursor: 'pointer' }}>
            <div className="icon-circle" style={{ background: '#E2E4DD', color: '#1E293B' }}>
              <Users size={20} strokeWidth={2} />
            </div>
            <div>
              <div className="role-title">Parent / guardian</div>
              <div className="role-desc">Progress summaries and test scores</div>
            </div>
          </div>

          <div className="role-card" onClick={() => handleRoleSelect('headmaster')} style={{ cursor: 'pointer' }}>
            <div className="icon-circle" style={{ background: '#FEE2E2', color: '#991B1B' }}>
              <BarChart3 size={20} strokeWidth={2} />
            </div>
            <div>
              <div className="role-title">Admin</div>
              <div className="role-desc">School-wide performance overview</div>
            </div>
          </div>
        </div>

        <p className="caption" style={{ textAlign: 'center', marginTop: '12px' }}>
          INTEGRATION: replace these links with real sign-in
        </p>
      </div>
    </AppShell>
  );
};
