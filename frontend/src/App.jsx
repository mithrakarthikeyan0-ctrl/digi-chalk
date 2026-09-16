import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';

import { LandingPage } from './pages/LandingPage';
import { TeacherPage } from './pages/TeacherPage';
import { StudentPage } from './pages/StudentPage';
import { ParentPage } from './pages/ParentPage';
import { HeadmasterPage } from './pages/HeadmasterPage';
import { QuizPage } from './pages/QuizPage';
import { ReplayPage } from './pages/ReplayPage';
import { BoardPage } from './pages/BoardPage';
import { NotFoundPage } from './pages/NotFoundPage';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/teacher" element={<TeacherPage />} />
          <Route path="/student" element={<StudentPage />} />
          <Route path="/parent" element={<ParentPage />} />
          <Route path="/headmaster" element={<HeadmasterPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/replay" element={<ReplayPage />} />
          <Route path="/board" element={<BoardPage />} />
          
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
