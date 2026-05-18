import Nav from './components/landing/Nav';
import Hero from './components/landing/Hero';
import SourcesStrip from './components/landing/SourcesStrip';
import HowItWorks from './components/landing/HowItWorks';
import WhatsInside from './components/landing/WhatsInside';
import AskSection from './components/landing/AskSection';
import CtaBanner from './components/landing/CtaBanner';
import Footer from './components/landing/Footer';
import AuthModal from './components/auth/AuthModal';
import { AuthModalProvider } from './contexts/AuthModalContext';

export default function App() {
  return (
    <AuthModalProvider>
      <div className="min-h-screen bg-bg text-text">
        <Nav />
        <main>
          <Hero />
          <SourcesStrip />
          <HowItWorks />
          <WhatsInside />
          <AskSection />
          <CtaBanner />
        </main>
        <Footer />
      </div>
      <AuthModal />
    </AuthModalProvider>
  );
}
