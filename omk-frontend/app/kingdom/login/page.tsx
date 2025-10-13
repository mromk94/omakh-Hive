'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { API_ENDPOINTS } from '@/lib/constants';
import { motion } from 'framer-motion';
import { Crown, Lock, Mail } from 'lucide-react';

export default function KingdomLogin() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Real backend authentication
      const response = await fetch(`${API_ENDPOINTS.AUTH}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        // Store real JWT token and user data
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Check if user is admin
        if (data.user.role === 'admin') {
          router.push('/kingdom');
        } else {
          setError('Access denied. Admin privileges required.');
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
      } else {
        setError(data.detail || 'Invalid credentials');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="bg-gray-900/50 backdrop-blur-xl border border-yellow-900/30 rounded-2xl p-8">
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-full flex items-center justify-center mb-4">
              <Crown className="w-10 h-10 text-black" />
            </div>
            <h1 className="text-3xl font-bold text-yellow-500">Kingdom</h1>
            <p className="text-gray-400 text-sm mt-2">Admin Portal Access</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="king@omakh.io"
                  required
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-11 pr-4 py-3 text-white focus:outline-none focus:border-yellow-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-11 pr-4 py-3 text-white focus:outline-none focus:border-yellow-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 disabled:from-gray-700 disabled:to-gray-700 text-black font-bold rounded-lg transition-all"
            >
              {loading ? 'Authenticating...' : 'Enter Kingdom'}
            </button>
          </form>

          {/* Admin Info */}
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <p className="text-xs text-blue-300 font-semibold mb-2">Admin Login:</p>
            <p className="text-xs text-gray-400">Email: king@omakh.io</p>
            <p className="text-xs text-gray-400">Password: Admin2025!!</p>
          </div>

          {/* Security Notice */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              🔐 Secured by Queen AI • All actions are logged
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
