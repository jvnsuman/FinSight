import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, TrendingUp } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function LandingNavbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '#home' },
    { name: 'Features', href: '#features' },
    { name: 'Services', href: '#services' },
    { name: 'Analytics', href: '#analytics' },
    { name: 'About', href: '#about' },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-ink-dark/80 backdrop-blur-md border-b border-white/5 py-4'
          : 'bg-transparent py-6'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <a href="#home" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                <TrendingUp className="text-white w-5 h-5" />
              </div>
              <span className="text-2xl font-bold text-white tracking-tight">FinSight</span>
            </a>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-gray-400 hover:text-white transition-colors text-sm font-medium"
              >
                {link.name}
              </a>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <Link
                to="/dashboard"
                className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium hover:opacity-90 transition-opacity shadow-lg shadow-primary/20"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-white font-medium text-sm transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium text-sm hover:opacity-90 transition-opacity shadow-lg shadow-primary/20"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-gray-300 hover:text-white"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-ink-dark border-b border-ink-light/20 absolute top-full left-0 right-0 px-4 pt-2 pb-6 space-y-4 shadow-xl">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setIsMobileMenuOpen(false)}
              className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-white hover:bg-ink rounded-md"
            >
              {link.name}
            </a>
          ))}
          <div className="pt-4 border-t border-ink-light/20 flex flex-col space-y-3">
            {user ? (
              <Link
                to="/dashboard"
                className="block text-center px-5 py-3 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block text-center px-5 py-3 rounded-lg border border-ink-light text-white font-medium"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="block text-center px-5 py-3 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
