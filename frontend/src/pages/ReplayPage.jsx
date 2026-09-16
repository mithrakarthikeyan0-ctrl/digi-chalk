import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Play, Pause } from 'lucide-react';
import { AppShell } from '../components/layout/AppShell';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';

// Mock initial strokes for demo
const STROKE_DEMO = [
  { path: "M20 60 Q 70 30 130 65 T 250 55", color: "#F1F5F9" },
  { path: "M25 110 L 160 110", color: "#FCD34D" },
  { path: "M25 140 Q 90 165 160 135 T 300 145", color: "#6EE7B7" }
];

export const ReplayPage = () => {
  const { lowBandwidth, setLowBandwidth } = useApp();
  const navigate = useNavigate();
  
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const totalSeconds = 48 * 60; // 48 mins
  
  const canvasRef = useRef(null);
  const trackRef = useRef(null);

  // Format mm:ss
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  // Playback loop
  useEffect(() => {
    let interval;
    if (playing) {
      interval = setInterval(() => {
        setElapsed(prev => {
          const next = prev + 5; // Fast forward for demo
          if (next >= totalSeconds) {
            setPlaying(false);
            return totalSeconds;
          }
          return next;
        });
      }, 100); // 100ms interval for smooth demo fast forward
    }
    return () => clearInterval(interval);
  }, [playing]);

  // Canvas drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const render = () => {
      const ratio = window.devicePixelRatio || 1;
      const cssWidth = canvas.clientWidth || 320;
      const cssHeight = canvas.clientHeight || 180;
      canvas.width = cssWidth * ratio;
      canvas.height = cssHeight * ratio;
      ctx.scale(ratio, ratio);
      ctx.clearRect(0, 0, cssWidth, cssHeight);
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      const progressPct = elapsed / totalSeconds;
      const visibleCount = Math.max(1, Math.ceil(STROKE_DEMO.length * Math.min(Math.max(progressPct, 0.05), 1.0)));

      for (let i = 0; i < visibleCount && i < STROKE_DEMO.length; i++) {
        const stroke = STROKE_DEMO[i];
        const p = new Path2D(stroke.path);
        ctx.strokeStyle = stroke.color;
        ctx.stroke(p);
      }
    };
    
    render();
    window.addEventListener('resize', render);
    return () => window.removeEventListener('resize', render);
  }, [elapsed]);

  const handleScrub = (e) => {
    const rect = trackRef.current.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const frac = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    setElapsed(Math.round(totalSeconds * frac));
  };

  const handleJump = (frac) => {
    setElapsed(Math.round(totalSeconds * frac));
  };

  const progressPct = (elapsed / totalSeconds) * 100;

  return (
    <AppShell>
      <Link to="/student" className="back-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '20px 20px 0', fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, textDecoration: 'none' }}>
        &larr; Back to lessons
      </Link>
      
      <div className="main">
        <div>
          <div className="row-between">
            <Badge variant="good">Class 8B &middot; Maths</Badge>
            <span className="caption">Synced Telemetry</span>
          </div>
          <h1 style={{ fontSize: '22px', marginTop: '6px' }}>Fractions &mdash; chapter 4</h1>
          <p className="caption">Replay vector chalkboard strokes synced with teacher audio</p>
        </div>

        <div className="board-window mt-8">
          <div className="board-status">
            <span className="rec-dot live" style={{ background: 'var(--chalk-mint)' }}></span>
            <span>Chalkboard Replay</span>
            <span style={{ marginLeft: 'auto', color: 'var(--chalk-white)', fontWeight: 600 }}>{formatTime(elapsed)} / {formatTime(totalSeconds)}</span>
          </div>
          <canvas ref={canvasRef} style={{ width: '100%', height: '180px' }}></canvas>
        </div>

        <div className="scrubber" style={{ position: 'relative', height: '12px', margin: '16px 4px 8px' }}>
          <div 
            ref={trackRef}
            style={{ height: '8px', background: 'rgba(0,0,0,0.1)', cursor: 'pointer', borderRadius: '4px', overflow: 'hidden' }}
            onPointerDown={(e) => { e.target.setPointerCapture(e.pointerId); handleScrub(e); }}
            onPointerMove={(e) => { if(e.buttons === 1) handleScrub(e); }}
          >
            <div className="good" style={{ width: `${progressPct}%`, height: '100%', background: 'var(--color-emerald)', transition: playing ? 'width 0.1s linear' : 'none' }}></div>
          </div>
          <div style={{ position: 'absolute', top: '50%', transform: 'translate(-50%, -50%)', left: `${progressPct}%`, width: '16px', height: '16px', background: 'var(--color-emerald)', borderRadius: '50%', boxShadow: '0 2px 4px rgba(0,0,0,0.2)', pointerEvents: 'none' }}></div>
          
          <span className="bookmark-dot" style={{ left: '38%', top: '0px' }} onClick={() => handleJump(0.38)}></span>
          <span className="bookmark-dot" style={{ left: '66%', top: '0px' }} onClick={() => handleJump(0.66)}></span>
        </div>

        <Card className="mt-16">
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <button 
              onClick={() => setPlaying(!playing)}
              style={{ width: '44px', height: '44px', borderRadius: '50%', border: 'none', background: 'var(--color-emerald)', color: '#FBF8F2', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            >
              {playing ? <Pause fill="currentColor" size={20} /> : <Play fill="currentColor" size={20} />}
            </button>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '13px' }}>Full lesson replay</div>
              <div className="caption">Tap play or scrub timeline to jump through notes</div>
            </div>
            <label className="switch">
              <input type="checkbox" checked={lowBandwidth} onChange={e => setLowBandwidth(e.target.checked)} />
              <span className="track"></span>
              <span className="thumb"></span>
            </label>
          </div>
          
          {lowBandwidth && (
            <div className="mt-8">
              <span className="low-data-tag">Low-data active: Audio muted, vector strokes only</span>
            </div>
          )}
        </Card>

        <Card className="mt-16">
          <div className="card-title">
            <h2 style={{ fontSize: '15px' }}>Teacher Bookmarks</h2>
            <span className="caption">2 key topics</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }} className="mt-8">
            <button className="bookmark-pill" onClick={() => handleJump(0.38)} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '12px', border: '1px solid var(--color-slate-light)', background: 'var(--paper-2)', textAlign: 'left', cursor: 'pointer' }}>
              <span className="bookmark-dot" style={{ position: 'static', display: 'inline-block' }}></span>
              <strong style={{ color: 'var(--color-amber)' }}>18:14</strong>
              <span>&middot; Equivalent fractions diagram</span>
            </button>
            <button className="bookmark-pill" onClick={() => handleJump(0.66)} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '12px', border: '1px solid var(--color-slate-light)', background: 'var(--paper-2)', textAlign: 'left', cursor: 'pointer' }}>
              <span className="bookmark-dot" style={{ position: 'static', display: 'inline-block' }}></span>
              <strong style={{ color: 'var(--color-amber)' }}>31:40</strong>
              <span>&middot; Simplifying to lowest terms</span>
            </button>
          </div>
        </Card>

        <Card className="mt-16 row-between" style={{ background: 'var(--paper-dim)' }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: '13px' }}>Ready to test yourself?</div>
            <div className="caption">Take the 3-question quiz</div>
          </div>
          <button className="btn btn-primary" style={{ padding: '8px 16px' }} onClick={() => navigate('/quiz')}>Take quiz</button>
        </Card>
      </div>
    </AppShell>
  );
};
