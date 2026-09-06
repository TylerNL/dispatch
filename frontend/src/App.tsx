import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ChatPage from './components/chat/ChatPage';
import ProfilePage from './pages/ProfilePage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import AuthModal from './components/auth/AuthModal';
import { AuthModalProvider, useAuthModal } from './contexts/AuthModalContext';
import { useAuth } from './contexts/AuthContext';

export default function App() {
  return (
    <AuthModalProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<ChatRoute />} />
        <Route path="/chat/:id" element={<ChatRoute />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Routes>
      <AuthModal />
    </AuthModalProvider>
  );
}

function ChatRoute() {
  const { user, loading } = useAuth();
  const { open } = useAuthModal();

  useEffect(() => {
    if (loading || user) return;
    open('login');
  }, [loading, user, open]);

  if (loading) return null;
  return user ? <ChatPage /> : <LandingPage />;
}
