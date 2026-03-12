import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { Home, Network, Search, Shield, Info, Menu, X, HelpCircle } from 'lucide-react'
import { useAppStore } from '../stores/appStore'
import { useSnowflakeHealth } from '../hooks/useSnowflakeHealth'
import ConnectionBanner from './ConnectionBanner'
import CortexChatWidget from './CortexChatWidget'
import clsx from 'clsx'

const navItems = [
  { path: '/', icon: Home, label: 'Dashboard' },
  { path: '/network', icon: Network, label: 'Process Network' },
  { path: '/defects', icon: Search, label: 'Defect Tracing' },
  { path: '/five-whys', icon: HelpCircle, label: '5-Whys Analysis' },
  { path: '/risk', icon: Shield, label: 'Risk Analysis' },
  { path: '/about', icon: Info, label: 'About' },
]

export default function Layout() {
  const { sidebarCollapsed, toggleSidebar, connectionStatus } = useAppStore()
  const location = useLocation()
  
  useSnowflakeHealth()

  const currentPage = navItems.find(item => item.path === location.pathname)?.label || 'Dashboard'

  return (
    <div className="flex h-screen bg-background">
      <aside
        className={clsx(
          'fixed left-0 top-0 h-full bg-card border-r border-border transition-all duration-300 z-50',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-border">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Network className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-text-primary">GNN Trace</span>
            </div>
          )}
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-background transition-colors"
          >
            {sidebarCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
          </button>
        </div>

        <nav className="p-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all',
                  isActive
                    ? 'bg-primary/10 text-primary border-l-2 border-primary'
                    : 'text-text-secondary hover:bg-background hover:text-text-primary'
                )
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {!sidebarCollapsed && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="px-3 py-2 rounded-lg bg-background">
              <div className="flex items-center gap-2 text-xs text-text-secondary">
                <div
                  className={clsx(
                    'w-2 h-2 rounded-full',
                    connectionStatus === 'connected' ? 'bg-success' :
                    connectionStatus === 'disconnected' ? 'bg-critical' : 'bg-warning animate-pulse'
                  )}
                />
                <span>
                  {connectionStatus === 'connected' ? 'Connected to Snowflake' :
                   connectionStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
                </span>
              </div>
            </div>
          </div>
        )}
      </aside>

      <main
        className={clsx(
          'flex-1 transition-all duration-300 overflow-auto',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        {connectionStatus === 'disconnected' && <ConnectionBanner />}
        
        <header className="sticky top-0 z-40 h-16 px-6 flex items-center justify-between bg-background/80 backdrop-blur border-b border-border">
          <h1 className="text-xl font-semibold text-text-primary">{currentPage}</h1>
          <div className="text-sm text-text-secondary">
            GNN Process Traceability
          </div>
        </header>

        <div className="p-6">
          <Outlet />
        </div>
      </main>

      <CortexChatWidget />
    </div>
  )
}
