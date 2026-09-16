import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { CheckCircle } from 'lucide-react';

const QUIZ_DEMO = [
  {
    id: "q1",
    prompt: "What is 3/4 written as a decimal?",
    options: [
      { id: "a", text: "0.34" },
      { id: "b", text: "0.75" },
      { id: "c", text: "1.34" }
    ],
    correctOptionId: "b",
    explanation: "3 divided by 4 equals 0.75."
  },
  {
    id: "q2",
    prompt: "Which fraction is equivalent to 1/2?",
    options: [
      { id: "a", text: "2/4" },
      { id: "b", text: "1/3" },
      { id: "c", text: "3/5" }
    ],
    correctOptionId: "a",
    explanation: "Multiplying numerator and denominator by 2 gives 2/4."
  },
  {
    id: "q3",
    prompt: "Simplify 6/8 to its lowest terms.",
    options: [
      { id: "a", text: "3/5" },
      { id: "b", text: "2/3" },
      { id: "c", text: "3/4" }
    ],
    correctOptionId: "c",
    explanation: "Dividing both 6 and 8 by 2 simplifies to 3/4."
  }
];

export const QuizPage = () => {
  const navigate = useNavigate();
  
  const [current, setCurrent] = useState(0);
  const [score, setScore] = useState(0);
  const [selected, setSelected] = useState(null);
  const [studentAnswers, setStudentAnswers] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [error, setError] = useState("");

  const q = QUIZ_DEMO[current];
  const letterPrefixes = ["A", "B", "C", "D"];
  
  const handleNext = () => {
    if (!selected) {
      setError("Pick an answer first.");
      return;
    }
    
    setIsAnimating(true);
    const isCorrect = selected === q.correctOptionId;
    
    if (isCorrect) setScore(s => s + 1);
    
    setTimeout(() => {
      const newAnswers = [...studentAnswers, {
        questionId: q.id, prompt: q.prompt, selectedId: selected, 
        correctId: q.correctOptionId, isCorrect, explanation: q.explanation
      }];
      setStudentAnswers(newAnswers);
      
      if (current < QUIZ_DEMO.length - 1) {
        setCurrent(c => c + 1);
        setSelected(null);
        setIsAnimating(false);
      } else {
        setShowResults(true);
        // Save to local storage mock history
        const history = JSON.parse(localStorage.getItem('quiz_history') || '[]');
        history.unshift({
          title: "Maths: Fractions Quiz",
          date: new Date().toLocaleDateString(),
          score: Math.round(((isCorrect ? score + 1 : score) / QUIZ_DEMO.length) * 100)
        });
        localStorage.setItem('quiz_history', JSON.stringify(history.slice(0, 5)));
      }
    }, 1200);
  };

  const getOptionStyle = (optId) => {
    if (!isAnimating) {
      return selected === optId ? { borderColor: 'var(--color-indigo)', background: '#EEF2F6', fontWeight: 600 } : {};
    }
    
    // Animating feedback
    if (optId === q.correctOptionId) {
      return { background: '#D1FAE5', borderColor: '#10B981', color: '#065F46' };
    }
    if (selected === optId && !isCorrect(selected)) {
      return { background: '#FEE2E2', borderColor: '#EF4444', color: '#991B1B' };
    }
    return { opacity: 0.5 };
  };
  
  const isCorrect = (optId) => optId === q.correctOptionId;

  const handleRetake = () => {
    setCurrent(0);
    setScore(0);
    setSelected(null);
    setStudentAnswers([]);
    setShowResults(false);
    setIsAnimating(false);
  };

  return (
    <AppShell>
      <Link to="/student" className="back-link" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '20px 20px 0', fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, textDecoration: 'none' }}>
        &larr; Back to lessons
      </Link>
      
      <div className="main">
        {!showResults ? (
          <>
            <div style={{ marginBottom: '8px' }}>
              <div className="row-between">
                <Badge style={{ background: '#E2E8F0', color: 'var(--color-indigo)' }}>Maths &middot; Fractions</Badge>
                <span className="caption">{current + 1} of {QUIZ_DEMO.length}</span>
              </div>
              <h1 style={{ fontSize: '22px', marginTop: '6px' }}>Chalkboard Practice Quiz</h1>
              <p className="caption">Question {current + 1} of {QUIZ_DEMO.length}</p>
              <div className="quiz-progress-bar" style={{ height: '4px', background: 'var(--color-slate-light)', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
                <div style={{ height: '100%', background: 'var(--color-indigo)', width: `${((current + 1) / QUIZ_DEMO.length) * 100}%`, transition: 'width 0.3s ease' }}></div>
              </div>
            </div>

            <Card className="mt-16">
              <h2 style={{ fontSize: '16px', lineHeight: 1.4 }}>{q.prompt}</h2>
              <div className="mt-16" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {q.options.map((opt, idx) => (
                  <button 
                    key={opt.id}
                    className="quiz-option"
                    style={{
                      display: 'flex', alignItems: 'center', gap: '12px', width: '100%', textAlign: 'left',
                      padding: '14px 16px', border: '1px solid var(--color-slate-light)', borderRadius: '12px',
                      background: 'var(--paper-2)', fontFamily: 'inherit', fontSize: '14px',
                      transition: 'all 0.15s ease', cursor: isAnimating ? 'default' : 'pointer',
                      ...getOptionStyle(opt.id)
                    }}
                    onClick={() => { if(!isAnimating) { setSelected(opt.id); setError(""); } }}
                    disabled={isAnimating}
                  >
                    <span style={{
                      width: '28px', height: '28px', borderRadius: '50%', flexShrink: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: selected === opt.id ? 'var(--color-indigo)' : 'var(--paper-dim)',
                      color: selected === opt.id ? '#FBF8F2' : 'var(--color-indigo)',
                      fontWeight: 700, fontSize: '12px'
                    }}>
                      {letterPrefixes[idx]}
                    </span>
                    <span>{opt.text}</span>
                  </button>
                ))}
              </div>
            </Card>
            
            {error && <p style={{ color: 'var(--color-crimson)', fontSize: '13px', fontWeight: 600, minHeight: '20px', marginBottom: '8px', marginTop: '8px' }}>{error}</p>}
            
            <Button variant="primary" block className="mt-16" onClick={handleNext} disabled={isAnimating}>
              {current === QUIZ_DEMO.length - 1 ? "Finish quiz" : "Next question"}
            </Button>
          </>
        ) : (
          <div style={{ textAlign: 'center', paddingTop: '24px' }}>
            <div className="icon-circle" style={{ width: '64px', height: '64px', margin: '0 auto', background: '#D1FAE5', color: 'var(--color-emerald)' }}>
              <CheckCircle size={32} strokeWidth={2.5} />
            </div>
            <p className="caption mt-8">Your Quiz Score</p>
            <p style={{ fontSize: '42px', fontWeight: 800, color: 'var(--color-emerald)', margin: '4px 0' }}>{score} / {QUIZ_DEMO.length}</p>
            
            <p style={{ fontSize: '14px', fontWeight: 600, maxWidth: '280px', margin: '0 auto', color: score === QUIZ_DEMO.length ? 'var(--color-emerald)' : 'var(--color-indigo)' }}>
              {score === QUIZ_DEMO.length ? "Outstanding! Perfect score!" : "Good work! Review the bookmarked board moments to polish."}
            </p>

            <div className="card mt-16" style={{ padding: '12px', border: '1px solid var(--color-slate-light)', textAlign: 'left' }}>
              <h3 style={{ fontSize: '13px', marginBottom: '8px', fontWeight: 700 }}>Question Summary:</h3>
              {studentAnswers.map((ans, i) => (
                <div key={i} style={{ padding: '6px 0', borderTop: '1px solid var(--color-slate-light)', fontSize: '12px' }}>
                  <div>
                    {ans.isCorrect ? <Badge variant="good" style={{ marginRight: '6px' }}>Correct</Badge> : <Badge variant="warn" style={{ marginRight: '6px' }}>Review</Badge>}
                    <strong>Q{i + 1}:</strong> {ans.prompt}
                  </div>
                  <div className="caption mt-8" style={{ color: 'var(--text-secondary)' }}>{ans.explanation}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '24px', maxWidth: '260px', marginLeft: 'auto', marginRight: 'auto' }}>
              <Button variant="outline" block onClick={handleRetake}>Retake quiz</Button>
              <Button variant="outline" block onClick={() => navigate('/replay')}>Review board replay</Button>
              <Button variant="primary" block onClick={() => navigate('/student')}>Back to lessons</Button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};
