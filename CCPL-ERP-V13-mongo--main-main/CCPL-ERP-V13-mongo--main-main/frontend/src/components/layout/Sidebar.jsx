import { Link } from 'react-router-dom'
import { BarChart3, Package, TrendingUp, ShoppingCart, Users, Truck, GitBranch, Settings, LogOut, ChevronDown, Home, Archive, Boxes, FileText, Lock, Mail, FolderTree } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useState } from 'react'

export default function Sidebar() {
  const { logout } = useAuth()
  const [expandedMenu, setExpandedMenu] = useState('Dashboard')

  const toggleMenu = (label) => {
    setExpandedMenu(expandedMenu === label ? null : label)
  }

  const navItems = [
    { 
      to: '/', 
      icon: Home, 
      label: 'Dashboard',
      subItems: []
    },
    {
      icon: Archive,
      label: 'Masters',
      subItems: [
        { to: '/item-categories', label: 'Item Categories', icon: FolderTree },
        { to: '/fabric-category', label: 'Fabric Category' },
        { to: '/item-master', label: 'Item Master' },
        { to: '/variant-master', label: 'Variant Master' },
        { to: '/masters/brands', label: 'Brand Master' },
        { to: '/masters/suppliers', label: 'Supplier Master' },
        { to: '/warehouse-master', label: 'Warehouse Master' },
        { to: '/bin-location-master', label: 'BIN / Location Master' },
        { to: '/tax-hsn-master', label: 'Tax / HSN Master' },
      ]
    },
    { 
      icon: ShoppingCart,
      label: 'Purchase',
      subItems: [
        { to: '/purchase-orders', label: 'Purchase Orders' },
        { to: '/goods-receipt', label: 'Goods Receipt' },
        { to: '/purchase-returns', label: 'Purchase Returns' },
        { to: '/vendor-bills', label: 'Vendor Bills' },
        { to: '/purchase-reports', label: 'Purchase Reports' },
      ]
    },
    { 
      icon: Boxes,
      label: 'Quality',
      subItems: [
        { to: '/quality-checks', label: 'Quality Checks' },
        { to: '/inspections', label: 'Inspections' },
        { to: '/defects', label: 'Defects Management' },
        { to: '/quality-reports', label: 'Quality Reports' },
      ]
    },
    { 
      icon: TrendingUp,
      label: 'Inventory Transactions',
      subItems: [
        { to: '/stock-movements', label: 'Stock Movements' },
        { to: '/stock-adjustments', label: 'Stock Adjustments' },
        { to: '/stock-transfers', label: 'Stock Transfers' },
        { to: '/stock-issue', label: 'Stock Issue' },
        { to: '/stock-levels', label: 'Stock Levels' },
      ]
    },
    { 
      icon: BarChart3,
      label: 'Reports',
      subItems: [
        { to: '/inventory-reports', label: 'Inventory Reports' },
        { to: '/sales-reports', label: 'Sales Reports' },
        { to: '/purchase-reports', label: 'Purchase Reports' },
        { to: '/stock-summary', label: 'Stock Summary' },
        { to: '/aging-analysis', label: 'Aging Analysis' },
      ]
    },
    { 
      icon: Settings,
      label: 'Settings',
      subItems: [
        { to: '/users', label: 'User Management' },
        { to: '/roles', label: 'Role Management' },
        { to: '/file-manager', label: 'File Manager' },
        { to: '/company', label: 'Company Settings' },
        { to: '/email-config', label: 'Email Configuration' },
        { to: '/general-settings', label: 'General Settings' },
      ]
    },
  ]

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen flex flex-col overflow-hidden">
      <div className="p-6 border-b border-gray-800 flex-shrink-0">
        <h2 className="text-xl font-bold">ERP Inventory</h2>
        <p className="text-xs text-gray-400 mt-1">v1.0.0</p>
      </div>
      
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item, idx) => 
          item.subItems && item.subItems.length > 0 ? (
            <div key={idx}>
              <button
                onClick={() => toggleMenu(item.label)}
                className="w-full flex items-center justify-between px-4 py-3 rounded-lg hover:bg-gray-800 transition text-sm font-medium"
              >
                <div className="flex items-center gap-3">
                  {item.icon && <item.icon size={20} />}
                  <span>{item.label}</span>
                </div>
                <ChevronDown 
                  size={16} 
                  className={`transition-transform duration-300 ${expandedMenu === item.label ? 'rotate-180' : ''}`}
                />
              </button>
              
              {expandedMenu === item.label && (
                <div className="mt-1 ml-2 border-l border-gray-700 space-y-1">
                  {item.subItems.map((subitem, sidx) => (
                    <Link 
                      key={sidx}
                      to={subitem.to} 
                      className="block px-4 py-2 ml-2 rounded-lg hover:bg-gray-800 transition text-sm text-gray-300 hover:text-white"
                    >
                      {subitem.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <Link 
              key={idx}
              to={item.to} 
              className="flex items-center px-4 py-3 rounded-lg hover:bg-gray-800 transition gap-3 text-sm font-medium"
            >
              {item.icon && <item.icon size={20} />}
              {item.label}
            </Link>
          )
        )}
      </nav>

      <div className="border-t border-gray-800 p-4 flex-shrink-0">
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 px-4 py-2 text-sm rounded-lg hover:bg-red-600/20 transition text-red-400 font-medium"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )
}
