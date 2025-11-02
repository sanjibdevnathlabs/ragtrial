import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import About from './pages/About'

// Lazy load heavy components to optimize initial bundle size
// DevDocs: markdown libraries (~330 KB compressed)
// ApiDocs: Swagger UI (~200 KB compressed)
// ChatUi: Chat interface with real-time messaging
const DevDocs = lazy(() => import('./pages/DevDocs'))
const ApiDocs = lazy(() => import('./pages/ApiDocs'))
const ChatUi = lazy(() => import('./pages/ChatUi'))

// Auth components
const Login = lazy(() => import('./pages/Login'))
const AdminLogin = lazy(() => import('./pages/admin/AdminLogin'))
import ProtectedRoute from './components/ProtectedRoute'

// User dashboard
const UserDashboard = lazy(() => import('./pages/Dashboard'))

// Admin components
const AdminLayout = lazy(() => import('./components/admin/AdminLayout'))
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'))
const RateLimits = lazy(() => import('./pages/admin/RateLimits'))
const Users = lazy(() => import('./pages/admin/Users'))
const Roles = lazy(() => import('./pages/admin/Roles'))
const Permissions = lazy(() => import('./pages/admin/Permissions'))
const AdminFiles = lazy(() => import('./pages/admin/Files'))

// Loading fallback component
const LoadingFallback = () => (
  <div className="pt-16 min-h-screen flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
      <p className="text-slate-400">Loading...</p>
    </div>
  </div>
)

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: 'easeIn',
    },
  },
}

// Animated routes component
function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <Landing />
            </motion.div>
          }
        />
        <Route
          path="/about"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <About />
            </motion.div>
          }
        />
        <Route
          path="/login"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <Login />
            </motion.div>
          }
        />
        <Route
          path="/admin/login"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <AdminLogin />
            </motion.div>
          }
        />
        <Route
          path="/dashboard"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <ProtectedRoute>
                <UserDashboard />
              </ProtectedRoute>
            </motion.div>
          }
        />
        <Route
          path="/dev-docs"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <DevDocs />
            </motion.div>
          }
        />
        <Route
          path="/docs"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <ApiDocs />
            </motion.div>
          }
        />
        <Route
          path="/langchain/chat"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <ProtectedRoute>
                <ChatUi />
              </ProtectedRoute>
            </motion.div>
          }
        />
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="rate-limits" element={<RateLimits />} />
          <Route path="users" element={<Users />} />
          <Route path="roles" element={<Roles />} />
          <Route path="permissions" element={<Permissions />} />
          <Route path="files" element={<AdminFiles />} />
        </Route>
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="min-h-screen bg-slate-950">
        <Navbar />
        <Suspense fallback={<LoadingFallback />}>
          <AnimatedRoutes />
        </Suspense>
      </div>
    </Router>
  )
}

export default App

