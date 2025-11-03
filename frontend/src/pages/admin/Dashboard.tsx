import { motion } from 'framer-motion';

interface StatCard {
  title: string;
  value: string;
  icon: string;
  color: string;
}

const stats: StatCard[] = [
  { title: 'Total Users', value: '1', icon: '👥', color: 'from-blue-500 to-cyan-500' },
  { title: 'Total Roles', value: '3', icon: '🎭', color: 'from-purple-500 to-pink-500' },
  { title: 'Permissions', value: '26', icon: '🔐', color: 'from-green-500 to-emerald-500' },
  { title: 'Rate Limits', value: '7', icon: '⚡', color: 'from-orange-500 to-red-500' },
];

export default function Dashboard() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Admin Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Welcome to the admin panel. Manage your application with ease.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center text-2xl`}>
                {stat.icon}
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              {stat.title}
            </h3>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {stat.value}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 mb-8">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all text-left">
            <span className="text-2xl mb-2 block">➕</span>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Create User</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Add a new user to the system</p>
          </button>

          <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-purple-500 dark:hover:border-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all text-left">
            <span className="text-2xl mb-2 block">🎭</span>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Manage Roles</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Configure user roles</p>
          </button>

          <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all text-left">
            <span className="text-2xl mb-2 block">⚡</span>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Rate Limits</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Configure API rate limits</p>
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          System Status
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-3"></div>
              <span className="text-gray-700 dark:text-gray-300">API Server</span>
            </div>
            <span className="text-sm font-medium text-green-600 dark:text-green-400">Operational</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-3"></div>
              <span className="text-gray-700 dark:text-gray-300">Database</span>
            </div>
            <span className="text-sm font-medium text-green-600 dark:text-green-400">Connected</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-3"></div>
              <span className="text-gray-700 dark:text-gray-300">Redis Cache</span>
            </div>
            <span className="text-sm font-medium text-green-600 dark:text-green-400">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}

