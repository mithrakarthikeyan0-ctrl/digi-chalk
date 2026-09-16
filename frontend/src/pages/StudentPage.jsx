import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { Card, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';
import { PARENT_CHILDREN_DEMO, MOCK_LESSONS } from '../data/demoData';

export const StudentPage = () => {
  const { lowBandwidth, setLowBandwidth, isSessionActive } = useApp();
  const [activeTab, setActiveTab] = useState('maths');
  const [notes, setNotes] = useState(() => localStorage.getItem('digichalk_student_notes') || '');
  
  const student = PARENT_CHILDREN_DEMO.aditi; // Mock current student
  const navigate = useNavigate();

  const handleNotesSave = () => {
    localStorage.setItem('digichalk_student_notes', notes);
    alert('Notes saved locally');
  };

  return (
    <AppShell>
      <Header title={`Hi, ${student.name}`} subtitle={`${student.grade} \u00B7 Roll No. 14`} />
      
      <div className="main">
        {/* Search & Streak */}
        <div className="row-between mb-16">
          <div style={{ flex: 1, marginRight: '12px' }}>
            <input type="text" className="form-input" placeholder="Search lessons..." style={{ padding: '8px 12px', height: '36px' }} />
          </div>
          <Badge variant="good" style={{ display: 'flex', gap: '6px', alignItems: 'center', height: '36px' }}>
            <span>12 Day Streak</span>
          </Badge>
        </div>

        {/* Continue Learning */}
        <div className="card mb-16" style={{ background: 'var(--color-indigo)', color: '#FBF8F2', border: 'none' }}>
          <div className="caption" style={{ color: '#CBD5C9' }}>Continue learning</div>
          <h2 style={{ fontSize: '16px', margin: '4px 0 12px', color: '#FBF8F2' }}>Science: Ecosystems</h2>
          <div className="bar-track mb-8" style={{ background: 'rgba(255,255,255,0.2)' }}>
            <div className="bar-fill" style={{ width: '65%', background: '#FCD34D' }}></div>
          </div>
          <div className="row-between">
            <span className="caption" style={{ color: '#CBD5C9' }}>24 min left</span>
            <Button style={{ background: '#FBF8F2', color: 'var(--color-indigo)', padding: '4px 12px', fontSize: '12px', minHeight: 'auto' }}>Resume</Button>
          </div>
        </div>

        {/* Subject Chips */}
        <div className="chip-row">
          {['maths', 'science', 'english', 'social'].map(subject => (
            <button
              key={subject}
              type="button"
              className="chip"
              aria-pressed={activeTab === subject}
              onClick={() => setActiveTab(subject)}
              style={{ textTransform: 'capitalize' }}
            >
              {subject}
            </button>
          ))}
        </div>

        {/* Low-Bandwidth Toggle */}
        <Card className="row-between" style={{ marginTop: '16px' }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: '13px' }}>Low-bandwidth mode</div>
            <div className="caption">Vector strokes only, audio muted</div>
          </div>
          <label className="switch">
            <input type="checkbox" checked={lowBandwidth} onChange={(e) => setLowBandwidth(e.target.checked)} />
            <span className="track"></span>
            <span className="thumb"></span>
          </label>
        </Card>

        {lowBandwidth && (
          <Card style={{ background: '#FEF3C7', borderColor: '#F59E0B', padding: '10px 14px', display: 'flex', gap: '8px', alignItems: 'center', marginTop: '16px' }}>
            <span className="rec-dot" style={{ background: '#D97706' }}></span>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#92400E' }}>2G/Low-Data Mode Active: Audio muted to save 90% bandwidth. High-efficiency chalk strokes only.</span>
          </Card>
        )}

        {/* Lesson Card */}
        <Card style={{ marginTop: '16px' }}>
          <CardTitle title="Fractions - chapter 4" actionLabel="Save" actionOnClick={() => alert('Saved')} />
          <div style={{ display: 'flex', gap: '12px', cursor: 'pointer' }} onClick={() => navigate('/replay')}>
            <div style={{ width: '64px', height: '48px', borderRadius: '8px', background: 'var(--board-bg)', flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div className="caption">48 min &middot; Maths</div>
              <div className="bar-track mt-8" style={{ position: 'relative' }}>
                <div className="bar-fill good" style={{ width: '40%' }}></div>
                <span className="bookmark-dot" style={{ left: '62%' }}></span>
                <span className="bookmark-dot" style={{ left: '81%' }}></span>
              </div>
            </div>
          </div>
        </Card>

        {/* Live Lesson Status */}
        <div style={{ marginTop: '16px' }}>
          {isSessionActive ? (
            <Card style={{ background: 'var(--color-crimson)', borderColor: 'var(--color-crimson)', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="rec-dot live" style={{ background: '#FBF8F2' }}></span>
              <span style={{ flex: 1 }}>
                <span style={{ display: 'block', fontWeight: 700, fontSize: '13px', color: '#FBF8F2' }}>Live now — Class 8B Maths</span>
                <span className="caption" style={{ color: '#FEE2E2' }}>Chalkboard stream</span>
              </span>
              <Button style={{ background: '#FBF8F2', color: 'var(--color-crimson)', padding: '8px 16px' }} onClick={() => navigate('/board?role=student')}>Join</Button>
            </Card>
          ) : (
            <Card style={{ border: '1px dashed var(--color-slate)', background: 'var(--paper-dim)', padding: '14px 16px' }}>
              <div className="row-between">
                <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-secondary)' }}>No Live Board Active</span>
                <Badge variant="low" style={{ background: 'var(--color-slate-light)', color: 'var(--color-slate)' }}>Offline</Badge>
              </div>
            </Card>
          )}
        </div>

        {/* Notes */}
        <Card style={{ marginTop: '16px' }}>
          <h2 style={{ fontSize: '14px', marginBottom: '8px' }}>My Notes</h2>
          <textarea 
            className="form-input" 
            rows="4" 
            placeholder="Type your personal study notes here..."
            value={notes}
            onChange={e => setNotes(e.target.value)}
          />
          <div className="row-between mt-8">
            <Button variant="outline" style={{ padding: '4px 12px', minHeight: 'auto', fontSize: '12px' }} onClick={handleNotesSave}>Save</Button>
          </div>
        </Card>
      </div>

      <BottomNav />
    </AppShell>
  );
};
