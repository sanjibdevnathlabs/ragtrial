import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store tokens in localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Check if user has admin permissions
        // This will be verified server-side, but we check here for UX
        const hasAdminPerms = await checkAdminPermissions(data.access_token);
        
        if (hasAdminPerms) {
          // Redirect to admin dashboard
          navigate('/admin/dashboard');
        } else {
          setError('You do not have permission to access the admin panel.');
          localStorage.clear();
        }
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkAdminPermissions = async (token: string): Promise<boolean> => {
    try {
      // Check if user has any admin-related permissions
      // Admin permissions pattern: role:*, permission:*, user:*, etc.
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        const permissions = userData.permissions || [];
        
        // Check if user has any admin permissions
        const adminPatterns = ['role:', 'permission:', 'user:', 'user_role:', 'user_permission:', 'route_permission:', 'rate_limit:'];
        return permissions.some((perm: string) => 
          adminPatterns.some(pattern => perm.startsWith(pattern))
        );
      }
      return false;
    } catch {
      return false;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 mb-4">
            <span className="text-white font-bold text-3xl">R</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Admin Login</h1>
          <p className="text-gray-400">Sign in to access the admin panel</p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-4 rounded-lg bg-red-500/20 border border-red-500/50 text-red-200 text-sm"
              >
                {error}
              </motion.div>
            )}

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="admin@ragtrial.com"
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
              />
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-gray-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 transition-all"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium hover:from-purple-700 hover:to-blue-700 focus:ring-4 focus:ring-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Links */}
          <div className="mt-6 space-y-2 text-center">
            <div>
              <a
                href="/login"
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                Regular user? Sign in here
              </a>
            </div>
            <div>
              <a
                href="/"
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                ← Back to Home
              </a>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

