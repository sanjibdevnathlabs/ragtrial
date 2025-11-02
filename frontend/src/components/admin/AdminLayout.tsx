import { ReactNode, useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

interface MenuItem {
  path: string;
  label: string;
  icon: string;
}

const menuItems: MenuItem[] = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/admin/users', label: 'Users', icon: '👥' },
  { path: '/admin/roles', label: 'Roles', icon: '🎭' },
  { path: '/admin/permissions', label: 'Permissions', icon: '🔐' },
  { path: '/admin/rate-limits', label: 'Rate Limits', icon: '⚡' },
  { path: '/admin/files', label: 'Files', icon: '📁' },
];

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <motion.aside
        initial={{ width: sidebarOpen ? 256 : 80 }}
        animate={{ width: sidebarOpen ? 256 : 80 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col shadow-lg"
      >
        {/* Logo & Toggle */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
          {sidebarOpen && (
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xl font-bold text-gray-900 dark:text-white"
            >
              Admin Panel
            </motion.h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center px-4 py-3 mb-1 mx-2 rounded-lg transition-all duration-200
                  ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }
                `}
              >
                <span className="text-2xl mr-3">{item.icon}</span>
                {sidebarOpen && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="font-medium"
                  >
                    {item.label}
                  </motion.span>
                )}
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute left-0 w-1 h-8 bg-blue-600 rounded-r-lg"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Profile Section */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
              A
            </div>
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="ml-3"
              >
                <p className="text-sm font-medium text-gray-900 dark:text-white">Admin</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">admin@ragtrial.local</p>
              </motion.div>
            )}
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 shadow-sm">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {menuItems.find((item) => location.pathname.startsWith(item.path))?.label || 'Admin Panel'}
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              🔔
            </button>
            <Link
              to="/"
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              ← Back to Site
            </Link>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

