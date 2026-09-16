import React, { useRef, useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2, Undo, Maximize, Circle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { IconButton } from '../components/ui/Button';

// Mock initial strokes for demo
const STROKE_DEMO = [
  { path: "M20 60 Q 70 30 130 65 T 250 55", color: "#F1F5F9" },
  { path: "M25 110 L 160 110", color: "#FCD34D" },
];

export const BoardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const role = searchParams.get('role') || 'student';
  const { isSessionActive } = useApp();
  
  const canvasRef = useRef(null);
  const [activeColor, setActiveColor] = useState('#F1F5F9'); // chalk-white
  const [strokes, setStrokes] = useState([...STROKE_DEMO]);
  const [drawing, setDrawing] = useState(false);
  const [currentPath, setCurrentPath] = useState('');

  // INTEGRATION: replace local demo stroke events with authenticated WebSocket events.
  
  useEffect(() => {
    // Redraw on strokes change
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Resize observer or manual set size
    const resizeCanvas = () => {
      const ratio = window.devicePixelRatio || 1;
      const cssWidth = canvas.clientWidth;
      const cssHeight = canvas.clientHeight;
      canvas.width = cssWidth * ratio;
      canvas.height = cssHeight * ratio;
      ctx.scale(ratio, ratio);
      redrawStrokes();
    };

    const redrawStrokes = () => {
      const cssWidth = canvas.clientWidth;
      const cssHeight = canvas.clientHeight;
      ctx.clearRect(0, 0, cssWidth, cssHeight);
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      
      strokes.forEach(stroke => {
        const p = new Path2D(stroke.path);
        ctx.strokeStyle = stroke.color;
        ctx.stroke(p);
      });
      
      // Draw current path if any
      if (currentPath) {
        const p = new Path2D(currentPath);
        ctx.strokeStyle = activeColor;
        ctx.stroke(p);
      }
    };
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    return () => window.removeEventListener('resize', resizeCanvas);
  }, [strokes, currentPath, activeColor]);

  // Try landscape lock
  useEffect(() => {
    try {
      if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock("landscape").catch(() => {});
      }
    } catch (e) {
      // Ignored
    }
  }, []);

  const getCanvasCoords = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const handlePointerDown = (e) => {
    if (role !== 'teacher') return;
    setDrawing(true);
    const pos = getCanvasCoords(e);
    setCurrentPath(`M${pos.x} ${pos.y}`);
  };

  const handlePointerMove = (e) => {
    if (!drawing || role !== 'teacher') return;
    const pos = getCanvasCoords(e);
    setCurrentPath(prev => prev + ` L ${pos.x} ${pos.y}`);
  };

  const handlePointerUp = () => {
    if (!drawing || role !== 'teacher') return;
    setDrawing(false);
    if (currentPath) {
      setStrokes([...strokes, { path: currentPath, color: activeColor }]);
      setCurrentPath('');
    }
  };

  const handleClear = () => {
    if (window.confirm('Clear all strokes on the board?')) {
      setStrokes([]);
    }
  };
  
  const handleUndo = () => {
    if (strokes.length > 0) {
      setStrokes(strokes.slice(0, -1));
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {});
    } else {
      document.exitFullscreen();
    }
  };

  return (
    <div style={{ height: '100vh', background: 'var(--board-bg)', display: 'flex', flexDirection: 'column' }}>
      {/* Rotate Guard (CSS only shows in portrait) */}
      <div className="rotate-guard">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><path d="M12 18h.01"/></svg>
        <h2>Please rotate your device</h2>
        <p>The live board works best in landscape orientation.</p>
      </div>

      <div className="board-full" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '12px' }}>
        {/* Header toolbar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--chalk-white)' }}>
            <IconButton onClick={() => navigate(-1)} style={{ color: 'var(--chalk-white)', background: 'rgba(255,255,255,0.1)' }}>
              <ArrowLeft size={18} />
            </IconButton>
            <div>
              <div style={{ fontWeight: 600 }}>Class 8B &middot; Maths</div>
              <div style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className={`rec-dot ${isSessionActive ? 'live' : ''}`}></span>
                {isSessionActive ? 'Connecting...' /* Simulate connecting state for demo */ : 'Offline'}
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>{role === 'teacher' ? 'Broadcasting' : 'Viewing'} as {role}</span>
            <IconButton onClick={toggleFullscreen} style={{ color: 'var(--chalk-white)', background: 'rgba(255,255,255,0.1)' }}>
              <Maximize size={16} />
            </IconButton>
          </div>
        </div>

        {/* Canvas area */}
        <div style={{ flex: 1, position: 'relative', borderRadius: '12px', background: 'var(--board-bg-alt)', overflow: 'hidden' }}>
          <canvas 
            ref={canvasRef}
            style={{ width: '100%', height: '100%', touchAction: 'none' }}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerOut={handlePointerUp}
          />
          
          {/* Teacher Floating Toolbar */}
          {role === 'teacher' && (
            <div style={{ 
              position: 'absolute', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
              background: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(4px)',
              padding: '8px 16px', borderRadius: 'var(--radius-pill)', display: 'flex', gap: '16px', alignItems: 'center'
            }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                {['#F1F5F9', '#FCD34D', '#6EE7B7'].map(color => (
                  <button 
                    key={color}
                    style={{ 
                      width: '24px', height: '24px', borderRadius: '50%', background: color, 
                      border: `2px solid ${activeColor === color ? 'white' : 'transparent'}`,
                      boxShadow: activeColor === color ? '0 0 0 2px var(--color-indigo)' : 'none',
                      cursor: 'pointer' 
                    }}
                    onClick={() => setActiveColor(color)}
                    aria-label={`Select color ${color}`}
                  />
                ))}
              </div>
              <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.2)' }} />
              <IconButton onClick={handleUndo} style={{ color: 'white', padding: 0, width: '28px', height: '28px' }} aria-label="Undo">
                <Undo size={16} />
              </IconButton>
              <IconButton onClick={handleClear} style={{ color: '#FCA5A5', padding: 0, width: '28px', height: '28px' }} aria-label="Clear Board">
                <Trash2 size={16} />
              </IconButton>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
