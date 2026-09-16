import React from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Header } from '../components/layout/Header';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { PARENT_CHILDREN_DEMO } from '../data/demoData';
import { useApp } from '../context/AppContext';

export const ParentPage = () => {
  const { selectedChild, setSelectedChild, lang } = useApp();
  const childData = PARENT_CHILDREN_DEMO[selectedChild];

  return (
    <AppShell>
      <Header title="Parent Portal" subtitle="Sunrise Public School" />
      
      <div className="main">
        {/* Child Selector */}
        <div className="chip-row">
          {Object.keys(PARENT_CHILDREN_DEMO).map(key => (
            <button 
              key={key} 
              className="chip" 
              aria-pressed={selectedChild === key}
              onClick={() => setSelectedChild(key)}
            >
              {PARENT_CHILDREN_DEMO[key].name}
            </button>
          ))}
        </div>

        {/* Weekly Summary */}
        <Card className="mt-16">
          <h2 style={{ fontSize: '14px', marginBottom: '8px' }}>Weekly Learning Summary</h2>
          <p className="caption" style={{ color: 'var(--text-primary)' }}>
            {lang === 'ta' ? childData.summaryTa : childData.summaryEn}
          </p>
        </Card>

        {/* Test Scores */}
        <Card className="mt-16">
          <h2 style={{ fontSize: '14px', marginBottom: '12px' }}>Recent Test Scores</h2>
          {childData.scores.map((score, idx) => (
            <div key={idx} className="row-between mt-8">
              <span style={{ fontWeight: 600, fontSize: '13px' }}>{score.label}</span>
              <Badge variant={score.value >= 75 ? 'good' : score.value >= 60 ? 'warn' : 'low'}>
                {score.value}%
              </Badge>
            </div>
          ))}
        </Card>

        {/* Recent Alert */}
        <Card className="mt-16">
          <div className="row-between">
            <span className="caption" style={{ color: 'var(--color-emerald-dark)', fontWeight: 700 }}>Alert &middot; {childData.alertTime}</span>
            <Badge variant="good">Delivered</Badge>
          </div>
          <p style={{ fontSize: '12px', marginTop: '6px' }}>{childData.recentAlert}</p>
        </Card>
      </div>
    </AppShell>
  );
};
