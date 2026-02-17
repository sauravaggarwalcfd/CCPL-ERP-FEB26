import { useState, useEffect } from 'react'
import { useLayout } from '../context/LayoutContext'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { DollarSign, Package, ShoppingCart, TrendingUp } from 'lucide-react'
import { reports, inventory } from '../services/api'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { setTitle } = useLayout()
  const [salesData, setSalesData] = useState(null)
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setTitle('Dashboard')
    fetchDashboardData()
  }, [setTitle])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const today = new Date()
      const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

      // Format dates
      const formatDate = (date) => date.toISOString().split('T')[0]

      const [salesRes, stockRes] = await Promise.all([
        reports.salesSummary({
          start_date: formatDate(thirtyDaysAgo),
          end_date: formatDate(today),
        }),
        reports.stockCurrent({ limit: 100 }),
      ])

      setSalesData(salesRes.data)
      setStockData(stockRes.data)
    } catch (error) {
      toast.error('Failed to fetch dashboard data')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{label}</p>
          <p className="text-2xl font-bold mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon size={28} className="text-white" />
        </div>
      </div>
    </div>
  )

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  const summary = salesData?.summary || {}
  const items = stockData?.items || []

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={ShoppingCart}
          label="Total Orders"
          value={summary.total_orders || 0}
          color="bg-blue-500"
        />
        <StatCard
          icon={DollarSign}
          label="Revenue"
          value={`₹${(summary.total_revenue || 0).toFixed(2)}`}
          color="bg-green-500"
        />
        <StatCard
          icon={Package}
          label="Items Sold"
          value={summary.total_items_sold || 0}
          color="bg-purple-500"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Order Value"
          value={`₹${(summary.avg_order_value || 0).toFixed(2)}`}
          color="bg-orange-500"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Sales Trend (Last 30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={generateChartData(salesData?.orders || [])}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="orders" stroke="#3b82f6" />
              <Line type="monotone" dataKey="revenue" stroke="#10b981" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Stock Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Stock Levels</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'In Stock', value: items.filter(i => i.quantity > 0).length },
                  { name: 'Low Stock', value: items.filter(i => i.quantity > 0 && i.quantity <= (i.min_stock_level || 10)).length },
                  { name: 'Out of Stock', value: items.filter(i => i.quantity === 0).length },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                <Cell fill="#10b981" />
                <Cell fill="#f59e0b" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Low Stock Alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Low Stock Alerts</h2>
        {items.filter(i => i.quantity > 0 && i.quantity <= (i.min_stock_level || 10)).length === 0 ? (
          <p className="text-gray-500">No low stock alerts</p>
        ) : (
          <div className="space-y-2">
            {items
              .filter(i => i.quantity > 0 && i.quantity <= (i.min_stock_level || 10))
              .slice(0, 5)
              .map((item) => (
                <div key={item.id} className="flex justify-between items-center p-3 bg-yellow-50 rounded border border-yellow-200">
                  <span className="font-mono text-sm">{item.variant?.sku}</span>
                  <span className="text-sm text-gray-600">Qty: {item.quantity}</span>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  </div>
  )
}

function generateChartData(orders) {
  const byDate = {}
  
  orders.forEach(order => {
    const date = new Date(order.order_date).toLocaleDateString('en-IN')
    if (!byDate[date]) {
      byDate[date] = { date, orders: 0, revenue: 0 }
    }
    byDate[date].orders += 1
    byDate[date].revenue += order.total_amount
  })

  return Object.values(byDate).sort((a, b) => new Date(a.date) - new Date(b.date))
}
