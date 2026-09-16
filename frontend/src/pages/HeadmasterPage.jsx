import React from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Header } from '../components/layout/Header';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const HeadmasterPage = () => {
  return (
    <AppShell>
      <Header title="Admin Dashboard" subtitle="School-wide overview" />
      
      <div className="main">
        {/* Date Selector */}
        <div className="row-between mb-16">
          <span style={{ fontWeight: 600, fontSize: '14px' }}>Date Range</span>
          <select className="form-input" style={{ width: 'auto', padding: '4px 8px' }}>
            <option>This Week</option>
            <option>Last Week</option>
            <option>This Month</option>
          </select>
        </div>

        {/* Aggregate Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Card>
            <div className="caption">Avg Attendance</div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-emerald)' }}>92%</div>
            <div className="caption" style={{ color: 'var(--color-emerald-dark)' }}>+2% vs last week</div>
          </Card>
          <Card>
            <div className="caption">Avg Test Score</div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-indigo)' }}>74%</div>
            <div className="caption" style={{ color: 'var(--color-slate)' }}>Consistent</div>
          </Card>
        </div>

        {/* Classes Table */}
        <Card className="mt-16">
          <div className="row-between mb-12">
            <h2 style={{ fontSize: '14px' }}>Class Performance</h2>
            <Button variant="outline" style={{ padding: '4px 8px', fontSize: '11px' }}>Export CSV</Button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['8B', '7A', '6C'].map((cls, i) => (
              <div key={cls} className="row-between" style={{ padding: '8px 0', borderBottom: '1px dashed var(--color-slate-light)' }}>
                <span style={{ fontWeight: 600, fontSize: '13px' }}>Class {cls}</span>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <Badge variant={i === 0 ? 'good' : 'warn'}>Att: {90 - i * 5}%</Badge>
                  <Badge variant={i === 0 ? 'good' : 'low'}>Score: {78 - i * 12}%</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
        
        <p className="caption" style={{ textAlign: 'center', marginTop: '16px' }}>
          Individual student data is hidden in Admin view.
        </p>
      </div>
    </AppShell>
  );
};
