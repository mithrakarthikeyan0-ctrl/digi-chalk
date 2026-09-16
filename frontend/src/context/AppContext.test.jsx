import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { expect, test } from 'vitest';
import { AppProvider, useApp } from './AppContext';

const TestComponent = () => {
  const { role, setRole, lowBandwidth, setLowBandwidth } = useApp();
  
  return (
    <div>
      <div data-testid="role">{role}</div>
      <button onClick={() => setRole('teacher')}>Set Teacher</button>
      <div data-testid="low-bandwidth">{lowBandwidth ? 'Yes' : 'No'}</div>
      <button onClick={() => setLowBandwidth(!lowBandwidth)}>Toggle Bandwidth</button>
    </div>
  );
};

test('AppContext provides initial state and updates correctly', () => {
  render(
    <AppProvider>
      <TestComponent />
    </AppProvider>
  );

  // Initial state from demo data
  expect(screen.getByTestId('role').textContent).toBe('student');
  expect(screen.getByTestId('low-bandwidth').textContent).toBe('No');

  // Update role
  act(() => {
    screen.getByText('Set Teacher').click();
  });
  expect(screen.getByTestId('role').textContent).toBe('teacher');

  // Toggle bandwidth
  act(() => {
    screen.getByText('Toggle Bandwidth').click();
  });
  expect(screen.getByTestId('low-bandwidth').textContent).toBe('Yes');
});
