import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { RefreshCw, Search, Eye, Edit, Package } from 'lucide-react'
import { useLayout } from '../../context/LayoutContext'
import { bomApi } from '../../services/api'

export default function BOMPool() {
  const { setTitle } = useLayout()
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { setTitle('BOM Pool') }, [setTitle])
  useEffect(() => { loadPool() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const loadPool = async () => {
    try {
      setLoading(true)
      const result = await bomApi.importBOMs()
      setItems(result.data.items || [])
      if (result.data.imported > 0) {
        toast.success(`${result.data.imported} new BOM(s) auto-imported`)
      }
    } catch (err) {
      toast.error('Pool load error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const filtered = items.filter(item => {
    if (!searchTerm) return true
    const q = searchTerm.toLowerCase()
    return `${item.art_no} ${item.buyer} ${item.season || ''} ${item.set_no || ''} ${item.uid}`.toLowerCase().includes(q)
  })

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Unallocated BOMs</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search by article, buyer, season..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm w-72 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button onClick={loadPool} disabled={loading} className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        {filtered.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['BOM ID', 'Article', 'Set No', 'Season', 'Buyer', 'Combos', 'Plan Qty', 'Created', 'Actions'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filtered.map(item => (
                  <tr key={item.uid} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-blue-600">{item.uid}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.art_no}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.set_no}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.season}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.buyer}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.combo_count}</td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{Number(item.plan_qty).toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex gap-1">
                        <button onClick={() => navigate(`/bom/view/${item.uid}`)} className="flex items-center gap-1 px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"><Eye size={12} /> View</button>
                        <button onClick={() => navigate(`/bom/editor?edit=${item.uid}`)} className="flex items-center gap-1 px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"><Edit size={12} /> Edit</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <Package size={40} className="mb-3" />
            <p className="text-sm">No unallocated BOMs found</p>
          </div>
        )}
      </div>
    </div>
  )
}
