import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { RefreshCw, ChevronDown, ChevronRight, Eye, Unlink, ClipboardList } from 'lucide-react'
import { useLayout } from '../../context/LayoutContext'
import { bomApi } from '../../services/api'

export default function DyeingPlans() {
  const { setTitle } = useLayout()
  const navigate = useNavigate()
  const [plans, setPlans] = useState([])
  const [expanded, setExpanded] = useState({})
  const [planBOMs, setPlanBOMs] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => { setTitle('Dyeing Plans') }, [setTitle])
  useEffect(() => { loadPlans() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const loadPlans = async () => {
    try {
      setLoading(true)
      const res = await bomApi.getPlans()
      setPlans(res.data || [])
    } catch (err) {
      toast.error('Plans load error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const togglePlan = async (dplanNo) => {
    const isExpanding = !expanded[dplanNo]
    setExpanded(prev => ({ ...prev, [dplanNo]: isExpanding }))

    if (isExpanding && !planBOMs[dplanNo]) {
      try {
        const res = await bomApi.listBOMs({ dplan_no: dplanNo })
        setPlanBOMs(prev => ({ ...prev, [dplanNo]: res.data || [] }))
      } catch (err) {
        toast.error('Error: ' + (err.response?.data?.detail || err.message))
      }
    }
  }

  const unallocateSingle = async (uid, dplanNo) => {
    if (!window.confirm(`Unallocate this BOM from ${dplanNo}?`)) return
    try {
      setLoading(true)
      await bomApi.unallocateBOMs([uid])
      toast.success('BOM unallocated')
      setPlanBOMs(prev => { const copy = { ...prev }; delete copy[dplanNo]; return copy })
      loadPlans()
    } catch (err) {
      toast.error('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Dyeing Plans</h2>
          <button onClick={loadPlans} disabled={loading} className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>

        {plans.length > 0 ? (
          <div className="space-y-2">
            {plans.map(plan => (
              <div key={plan.dplan_no} className="border rounded-lg overflow-hidden">
                <button
                  onClick={() => togglePlan(plan.dplan_no)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition text-left"
                >
                  <div className="flex items-center gap-3">
                    {expanded[plan.dplan_no] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    <strong className="text-gray-900">{plan.dplan_no}</strong>
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{plan.bom_count} BOMs</span>
                    <span className="text-sm font-mono text-green-600">Qty: {Number(plan.total_qty).toLocaleString()}</span>
                  </div>
                  <span className="text-xs text-gray-400">{plan.created_by}</span>
                </button>

                {expanded[plan.dplan_no] && (
                  <div className="p-4 border-t">
                    {planBOMs[plan.dplan_no] ? (
                      planBOMs[plan.dplan_no].length > 0 ? (
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                {['BOM ID', 'Article', 'Set No', 'Buyer', 'Combos', 'Plan Qty', 'Actions'].map(h => (
                                  <th key={h} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                              {planBOMs[plan.dplan_no].map(item => (
                                <tr key={item.uid} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 text-sm font-medium text-blue-600">{item.uid}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{item.art_no}</td>
                                  <td className="px-4 py-2 text-sm text-gray-500">{item.set_no}</td>
                                  <td className="px-4 py-2 text-sm text-gray-900">{item.buyer}</td>
                                  <td className="px-4 py-2 text-sm text-gray-500">{item.combo_count}</td>
                                  <td className="px-4 py-2 text-sm font-mono text-gray-900">{Number(item.plan_qty).toLocaleString()}</td>
                                  <td className="px-4 py-2 text-sm">
                                    <div className="flex gap-1">
                                      <button onClick={() => navigate(`/bom/view/${item.uid}`)} className="flex items-center gap-1 px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"><Eye size={12} /> View</button>
                                      <button onClick={() => unallocateSingle(item.uid, plan.dplan_no)} className="flex items-center gap-1 px-2 py-1 text-xs rounded bg-red-50 text-red-600 hover:bg-red-100"><Unlink size={12} /> Unallocate</button>
                                    </div>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-400 py-4 text-center">No BOMs in this plan</p>
                      )
                    ) : (
                      <div className="flex items-center justify-center py-4">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <ClipboardList size={40} className="mb-3" />
            <p className="text-sm">No dyeing plans found</p>
          </div>
        )}
      </div>
    </div>
  )
}
