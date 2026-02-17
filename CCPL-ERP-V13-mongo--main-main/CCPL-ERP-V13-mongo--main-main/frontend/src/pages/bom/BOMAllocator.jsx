import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { RefreshCw, Link, Package } from 'lucide-react'
import { useLayout } from '../../context/LayoutContext'
import { bomApi } from '../../services/api'

export default function BOMAllocator() {
  const { setTitle } = useLayout()
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState([])
  const [dplanInput, setDplanInput] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { setTitle('Allocate BOMs') }, [setTitle])
  useEffect(() => { loadAllocateList() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const loadAllocateList = async () => {
    try {
      setLoading(true)
      const result = await bomApi.importBOMs()
      setItems(result.data.items || [])
      setSelected([])
    } catch (err) {
      toast.error('Load error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const toggleRow = (uid) => {
    setSelected(prev => prev.includes(uid) ? prev.filter(u => u !== uid) : [...prev, uid])
  }

  const toggleAll = (checked) => {
    setSelected(checked ? items.map(i => i.uid) : [])
  }

  const doAllocate = async () => {
    if (!dplanInput.trim()) { toast.error('Enter D.Plan number'); return }
    if (selected.length === 0) { toast.error('Select BOMs first'); return }
    try {
      setLoading(true)
      const result = await bomApi.allocateBOMs(selected, dplanInput)
      toast.success(result.data.message)
      loadAllocateList()
    } catch (err) {
      toast.error('Allocate failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Select BOMs to Allocate</h2>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700 whitespace-nowrap">D.Plan No:</label>
              <input
                type="text"
                value={dplanInput}
                onChange={(e) => setDplanInput(e.target.value)}
                placeholder="e.g. 2609 DP"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-40 focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={doAllocate}
              disabled={selected.length === 0 || !dplanInput.trim() || loading}
              className="flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Link size={14} /> Allocate{selected.length > 0 ? ` (${selected.length})` : ''}
            </button>
            <button onClick={loadAllocateList} disabled={loading} className="flex items-center gap-1 px-3 py-2 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50">
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        {items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={selected.length === items.length && items.length > 0}
                      onChange={(e) => toggleAll(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                  </th>
                  {['BOM ID', 'Article', 'Buyer', 'Combos', 'Plan Qty'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {items.map(item => (
                  <tr key={item.uid} className={`hover:bg-gray-50 ${selected.includes(item.uid) ? 'bg-blue-50' : ''}`}>
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selected.includes(item.uid)}
                        onChange={() => toggleRow(item.uid)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-blue-600">{item.uid}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.art_no}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.buyer}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{item.combo_count}</td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{Number(item.plan_qty).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <Package size={40} className="mb-3" />
            <p className="text-sm">No unallocated BOMs to allocate</p>
          </div>
        )}
      </div>
    </div>
  )
}
