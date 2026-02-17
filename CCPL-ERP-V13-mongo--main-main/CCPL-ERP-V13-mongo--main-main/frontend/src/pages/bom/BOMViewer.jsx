import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Printer, Edit, FileText } from 'lucide-react'
import { useLayout } from '../../context/LayoutContext'
import { bomApi } from '../../services/api'

export default function BOMViewer() {
  const { setTitle } = useLayout()
  const { uid } = useParams()
  const navigate = useNavigate()
  const [viewer, setViewer] = useState({ uid: null, data: null })
  const [loading, setLoading] = useState(false)

  useEffect(() => { setTitle('View BOM') }, [setTitle])

  useEffect(() => {
    if (uid) loadBOM(uid)
  }, [uid]) // eslint-disable-line react-hooks/exhaustive-deps

  const loadBOM = async (bomUid) => {
    try {
      setLoading(true)
      const res = await bomApi.getBOM(bomUid)
      setViewer({ uid: bomUid, data: res.data })
    } catch (err) {
      toast.error('View error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!viewer.data) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-20 text-gray-400">
          <FileText size={48} className="mb-4" />
          <h3 className="text-lg font-medium text-gray-500">No BOM Selected</h3>
          <p className="text-sm mt-1">Click "View" on any BOM from the Pool or Plans pages.</p>
        </div>
      </div>
    )
  }

  const { header, combos } = viewer.data

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            BOM: {header.art_no} <span className="text-gray-400 text-sm font-normal">{header.uid}</span>
          </h2>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate(`/bom/editor?edit=${viewer.uid}`)} className="flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700">
            <Edit size={16} /> Edit
          </button>
          <button onClick={() => window.print()} className="flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50">
            <Printer size={16} /> Print
          </button>
        </div>
      </div>

      {/* Meta */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {[
            ['Article', header.art_no],
            ['Set No.', header.set_no],
            ['Season', header.season],
            ['Buyer', header.buyer],
            ['Plan Qty', header.plan_qty],
            ['Status', header.status],
            ['D.Plan', header.dplan_no || '\u2014'],
          ].map(([label, val]) => (
            <div key={label}>
              <label className="block text-xs font-medium text-gray-500 uppercase">{label}</label>
              <div className="mt-1 text-sm font-medium text-gray-900">{val}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Combos */}
      {combos.map((c, ci) => (
        <div key={ci} className="bg-white rounded-lg shadow overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-sm font-bold">C{ci + 1}</span>
              <span className="font-medium text-gray-700">{c.color_name}</span>
              <span className="text-xs text-gray-400">{c.color_id}</span>
            </div>
            <span className="text-sm font-mono text-green-600">Qty: {Number(c.plan_qty).toLocaleString()}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {['Fabric Quality', 'GSM', 'Component', 'AVG', 'Unit', 'Extra%', 'Waste%', 'Short%', 'Ready Need', 'Greige Need'].map(h => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {c.bom_lines.map((l, li) => (
                  <tr key={li} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{l.fabric_quality}</td>
                    <td className="px-3 py-2">{l.plan_rat_gsm}</td>
                    <td className="px-3 py-2">{l.component}</td>
                    <td className="px-3 py-2 text-right font-mono">{l.avg}</td>
                    <td className="px-3 py-2">{l.unit}</td>
                    <td className="px-3 py-2 text-right font-mono">{l.extra_pcs ? Number(l.extra_pcs).toFixed(2) : ''}</td>
                    <td className="px-3 py-2 text-right font-mono">{l.wastage_pcs ? Number(l.wastage_pcs).toFixed(2) : ''}</td>
                    <td className="px-3 py-2 text-right font-mono">{l.shortage ? Number(l.shortage).toFixed(2) : ''}</td>
                    <td className="px-3 py-2 text-right font-mono text-green-700">{l.ready_fabric_need ? Number(l.ready_fabric_need).toFixed(2) : ''}</td>
                    <td className="px-3 py-2 text-right font-mono text-green-700">{l.greige_fabric_need ? Number(l.greige_fabric_need).toFixed(2) : ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}
