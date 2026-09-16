import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Square, Bookmark } from 'lucide-react';
import { AppShell } from '../components/layout/AppShell';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { Card, CardTitle } from '../components/ui/Card';
import { Button, IconButton } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';

export const TeacherPage = () => {
  const { isSessionActive, setIsSessionActive, sessionSeconds, setSessionSeconds } = useApp();
  const navigate = useNavigate();
  
  const [bookmarks, setBookmarks] = useState([]);
  const [showScores, setShowScores] = useState(true);
  
  // Format seconds to mm:ss
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleToggleSession = () => {
    if (isSessionActive) {
      // Stop session
      setIsSessionActive(false);
      alert(`Session ended. Duration: ${formatTime(sessionSeconds)}`);
    } else {
      // Start session
      setSessionSeconds(0);
      setBookmarks([]);
      setIsSessionActive(true);
    }
  };

  const handleAddBookmark = () => {
    if (!isSessionActive) return;
    setBookmarks([...bookmarks, { time: formatTime(sessionSeconds), note: 'Important moment' }]);
  };

  return (
    <AppShell>
      <Header title="Class 8B &middot; Maths" subtitle="Today's session" />
      
      <div className="main">
        <Button 
          huge 
          className={isSessionActive ? 'is-recording' : ''} 
          onClick={handleToggleSession}
        >
          <div className="icon-circle">
            {isSessionActive ? <Square fill="currentColor" /> : <Play fill="currentColor" />}
          </div>
          <div style={{ textAlign: 'left' }}>
            <span className="label-main">{isSessionActive ? 'Stop Session' : 'Start Session'}</span>
            <span className="label-sub">{isSessionActive ? 'Recording and broadcasting...' : 'One tap to record and broadcast'}</span>
          </div>
        </Button>

        {/* Board Preview */}
        <div className="board-window mt-16" style={{ position: 'relative' }}>
          <div className="board-status">
            <span className={`rec-dot ${isSessionActive ? 'live' : ''}`}></span>
            <span>Session &middot; <span>{formatTime(sessionSeconds)}</span></span>
            <span style={{ marginLeft: 'auto', color: '#94A3B8' }}>Board replay</span>
          </div>
          <canvas height="170" style={{ height: '170px', width: '100%', borderRadius: '8px', background: '#0F172A' }}></canvas>
          <p className="caption" style={{ color: '#94A3B8', marginTop: '8px' }}>26 students watching</p>
          
          <button 
            className="btn"
            style={{ 
              position: 'absolute', top: '28px', right: '28px', width: '44px', height: '44px', 
              borderRadius: '50%', background: 'var(--color-amber)', padding: 0,
              boxShadow: 'var(--shadow-raised)', display: 'flex', alignItems: 'center', justifyContent: 'center' 
            }}
            onClick={handleAddBookmark}
            disabled={!isSessionActive}
          >
            <Bookmark fill="#FBF8F2" color="#FBF8F2" size={20} />
          </button>
        </div>
        
        {bookmarks.length > 0 && (
          <ul style={{ listStyle: 'none', margin: '10px 0 0', padding: 0, fontSize: '12px', color: 'var(--text-secondary)' }}>
            <li style={{ color: 'var(--color-indigo)', fontWeight: 600, paddingBottom: '4px', borderBottom: '1px dashed var(--color-slate-light)' }}>Bookmarks</li>
            {bookmarks.map((bm, i) => (
              <li key={i} style={{ padding: '4px 0', borderBottom: '1px dashed var(--color-slate-light)' }}>
                {bm.time} - {bm.note}
              </li>
            ))}
          </ul>
        )}

        <div 
          className="caption mt-8" 
          style={{ color: 'var(--color-emerald-dark)', fontWeight: 600, cursor: 'pointer' }}
          onClick={() => navigate('/board?role=teacher')}
        >
          Open full board (landscape) &rarr;
        </div>

        {/* Test Scores */}
        <Card className="mt-16">
          <CardTitle 
            title="Test scores" 
            actionLabel={showScores ? "Demo: Clear" : "Demo: Load"} 
            actionOnClick={() => setShowScores(!showScores)} 
          />
          {!showScores ? (
            <div style={{ textAlign: 'center', padding: '24px 12px', color: 'var(--text-secondary)' }}>
              <p style={{ margin: 0, fontSize: '13px', fontWeight: 500 }}>No test scores yet</p>
            </div>
          ) : (
            <div>
              <div className="row-between mt-8"><span style={{ fontWeight: 600, fontSize: '13px' }}>Algebra basics</span><Badge variant="good">78%</Badge></div>
              <div className="row-between mt-8"><span style={{ fontWeight: 600, fontSize: '13px' }}>Fractions quiz</span><Badge variant="warn">58%</Badge></div>
              <div className="row-between mt-8"><span style={{ fontWeight: 600, fontSize: '13px' }}>Geometry basics</span><Badge variant="low">34%</Badge></div>
            </div>
          )}
        </Card>

        {/* Schedule */}
        <Card className="mt-16">
          <h2 style={{ fontSize: '14px', marginBottom: '12px' }}>Today's Schedule</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-slate-light)', paddingBottom: '8px', marginBottom: '8px' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: '13px' }}>Class 8B &middot; Maths</div>
              <div className="caption">10:00 AM - 10:45 AM</div>
            </div>
            <Button variant="primary" style={{ padding: '4px 12px', fontSize: '12px' }}>Start Now</Button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: 0.6 }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: '13px' }}>Class 7A &middot; Geometry</div>
              <div className="caption">11:00 AM - 11:45 AM</div>
            </div>
            <Badge>Upcoming</Badge>
          </div>
        </Card>

      </div>

      <BottomNav />
    </AppShell>
  );
};
