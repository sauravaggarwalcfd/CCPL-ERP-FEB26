import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Scissors, Plus, Copy, X, Save, FileText } from 'lucide-react'
import { useLayout } from '../../context/LayoutContext'
import { bomApi } from '../../services/api'
import { useBomData } from '../../hooks/useBomData'

export default function BOMEditor() {
  const { setTitle } = useLayout()
  const { master, loading: masterLoading, setLoading: setMasterLoading, calculateReadyNeed, calculateGreigeNeed, getArticleOptions, loadMasterData, demoMode } = useBomData()
  const [searchParams, setSearchParams] = useSearchParams()

  const [editor, setEditor] = useState({ mode: 'create', uid: null, curSheet: null, header: {}, combos: [] })
  const [saving, setSaving] = useState(false)
  const [loadingArticle, setLoadingArticle] = useState(false)
  const [showNewArticleModal, setShowNewArticleModal] = useState(false)
  const [newArtNo, setNewArtNo] = useState('')

  useEffect(() => { setTitle('BOM Editor') }, [setTitle])

  // If URL has ?edit=BOM-XXXX, load that BOM for editing
  useEffect(() => {
    const editUid = searchParams.get('edit')
    if (editUid) {
      editBOM(editUid)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const editBOM = async (uid) => {
    try {
      setLoadingArticle(true)
      const res = await bomApi.getBOM(uid)
      const bom = res.data
      setEditor({
        mode: 'edit',
        uid,
        curSheet: bom.header.art_no || bom.header.sheet_name,
        header: bom.header,
        combos: bom.combos
      })
      toast.success(`Editing BOM ${uid}`)
    } catch (err) {
      toast.error('Edit error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoadingArticle(false)
    }
  }

  const onArticleChange = async (sheetName) => {
    if (!sheetName) {
      setEditor({ mode: 'create', uid: null, curSheet: null, header: {}, combos: [] })
      return
    }
    if (sheetName.startsWith('MASTER:')) {
      const artNo = sheetName.substring(7)
      try {
        setLoadingArticle(true)
        const result = await bomApi.createArticleSheet(artNo)
        if (result.data.error) { toast.error(result.data.error); return }
        toast.success(`Sheet "${artNo}" created!`)
        sheetName = result.data.sheet_name
        await loadMasterData()
      } catch (err) {
        toast.error('Create failed: ' + (err.response?.data?.detail || err.message))
        return
      } finally {
        setLoadingArticle(false)
      }
    }
    try {
      setLoadingArticle(true)
      const res = await bomApi.loadArticleBOM(sheetName)
      setEditor({ mode: 'create', uid: null, curSheet: sheetName, header: res.data.header, combos: res.data.combos })
    } catch (err) {
      toast.error('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoadingArticle(false)
    }
  }

  const calculateTotalQty = () => editor.combos.reduce((sum, c) => sum + (parseFloat(c.plan_qty) || 0), 0)

  const saveBOM = async () => {
    if (!editor.curSheet) { toast.error('No article selected!'); return }
    const payload = {
      uid: editor.uid,
      header: {
        art_no: editor.header.art_no, set_no: editor.header.set_no, buyer: editor.header.buyer,
        season: editor.header.season, plan_date: editor.header.plan_date,
        plan_qty: calculateTotalQty(), remarks: editor.header.remarks
      },
      combos: editor.combos.map(c => ({
        combo_sr_no: c.combo_sr_no, combo_name: c.combo_name || c.color_name,
        lot_no: c.lot_no, lot_count: c.lot_count, color_id: c.color_id,
        color_code: c.color_code, color_name: c.color_name, plan_qty: c.plan_qty,
        bom_lines: c.bom_lines.map(l => ({
          fabric_quality: l.fabric_quality, plan_rat_gsm: l.plan_rat_gsm, priority: l.priority,
          component: l.component, avg: l.avg, unit: l.unit, extra_pcs: l.extra_pcs || 0,
          wastage_pcs: l.wastage_pcs || 0, shortage: l.shortage,
          greige_fabric_need: l.greige_fabric_need, fc_no: l.fc_no || ''
        }))
      }))
    }
    try {
      setSaving(true)
      const result = await bomApi.saveBOM(payload)
      toast.success(result.data.message)
      setEditor({ mode: 'create', uid: null, curSheet: null, header: {}, combos: [] })
      setSearchParams({})
    } catch (err) {
      toast.error('Save failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSaving(false)
    }
  }

  // Combo operations
  const addCombo = () => {
    const newCombo = {
      combo_sr_no: editor.combos.length + 1, combo_name: '', lot_no: '', lot_count: 1,
      color_id: '', color_code: '', color_name: '', plan_qty: 0,
      bom_lines: [{ fabric_quality: '', plan_rat_gsm: '', priority: 1, component: '', avg: 0, unit: 'kg', extra_pcs: 0, wastage_pcs: 0, shortage: 0.1, ready_fabric_need: 0, greige_fabric_need: 0, fc_no: '' }]
    }
    setEditor(prev => ({ ...prev, combos: [...prev.combos, newCombo] }))
    toast.success('New color added')
  }

  const copyLastCombo = () => {
    if (editor.combos.length === 0) { addCombo(); return }
    const lastCombo = editor.combos[editor.combos.length - 1]
    const cp = { ...JSON.parse(JSON.stringify(lastCombo)), combo_sr_no: editor.combos.length + 1, color_id: '', color_code: '', color_name: '', combo_name: '' }
    setEditor(prev => ({ ...prev, combos: [...prev.combos, cp] }))
    toast.success('Last color copied!')
  }

  const removeCombo = (idx) => {
    if (editor.combos.length <= 1) { toast.error('Need at least one color'); return }
    if (window.confirm('Remove this color and all its BOM lines?')) {
      const newCombos = editor.combos.filter((_, i) => i !== idx).map((c, i) => ({ ...c, combo_sr_no: i + 1 }))
      setEditor(prev => ({ ...prev, combos: newCombos }))
    }
  }

  const updateCombo = (idx, field, value) => {
    setEditor(prev => {
      const newCombos = [...prev.combos]
      newCombos[idx] = { ...newCombos[idx], [field]: value }
      return { ...prev, combos: newCombos }
    })
  }

  const addBOMLine = (comboIdx) => {
    setEditor(prev => {
      const newCombos = [...prev.combos]
      newCombos[comboIdx] = { ...newCombos[comboIdx], bom_lines: [...newCombos[comboIdx].bom_lines, { fabric_quality: '', plan_rat_gsm: '', priority: newCombos[comboIdx].bom_lines.length + 1, component: '', avg: 0, unit: 'kg', extra_pcs: 0, wastage_pcs: 0, shortage: 0.1, ready_fabric_need: 0, greige_fabric_need: 0, fc_no: '' }] }
      return { ...prev, combos: newCombos }
    })
  }

  const removeBOMLine = (comboIdx, lineIdx) => {
    setEditor(prev => {
      const newCombos = [...prev.combos]
      if (newCombos[comboIdx].bom_lines.length <= 1) { toast.error('Need at least one BOM line'); return prev }
      newCombos[comboIdx] = { ...newCombos[comboIdx], bom_lines: newCombos[comboIdx].bom_lines.filter((_, i) => i !== lineIdx) }
      return { ...prev, combos: newCombos }
    })
  }

  const updateBOMLine = (comboIdx, lineIdx, field, value) => {
    setEditor(prev => {
      const newCombos = [...prev.combos]
      newCombos[comboIdx] = { ...newCombos[comboIdx], bom_lines: newCombos[comboIdx].bom_lines.map((l, i) => i === lineIdx ? { ...l, [field]: value } : l) }
      return { ...prev, combos: newCombos }
    })
  }

  const createNewArticle = async () => {
    if (!newArtNo.trim()) { toast.error('Enter article number'); return }
    try {
      setShowNewArticleModal(false)
      setLoadingArticle(true)
      const result = await bomApi.createArticleSheet(newArtNo.trim())
      if (result.data.error) { toast.error(result.data.error); return }
      toast.success(`Article "${newArtNo}" created!`)
      await loadMasterData()
      await onArticleChange(result.data.sheet_name)
    } catch (err) {
      toast.error('Failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoadingArticle(false)
      setNewArtNo('')
    }
  }

  const isLoading = masterLoading || loadingArticle || saving

  return (
    <div className="p-6 space-y-6">
      {/* Demo Mode Banner */}
      {demoMode && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-2 text-amber-600 text-sm">
          DEMO MODE - Running with sample data. Configure Google Sheets credentials to connect.
        </div>
      )}

      {/* Loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg p-6 shadow-xl flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-gray-700">{saving ? 'Saving BOM...' : 'Loading...'}</span>
          </div>
        </div>
      )}

      {/* Header Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {editor.mode === 'edit' ? `Edit BOM: ${editor.uid}` : 'Select or Create Article'}
          </h2>
          <button
            onClick={saveBOM}
            disabled={!editor.curSheet || saving}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={16} /> Save BOM
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
          <div className="col-span-2">
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Article</label>
            <select
              value={editor.curSheet || ''}
              onChange={(e) => onArticleChange(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">-- Select Article --</option>
              {getArticleOptions().map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Set No.</label>
            <input type="text" value={editor.header.set_no || ''} readOnly className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Season</label>
            <input type="text" value={editor.header.season || ''} readOnly className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Buyer</label>
            <input type="text" value={editor.header.buyer || ''} readOnly className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Total Plan Qty</label>
            <input type="text" value={calculateTotalQty()} readOnly className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-gray-50 font-mono text-right" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Plan Date</label>
            <input
              type="date"
              value={editor.header.plan_date?.split('T')[0] || ''}
              onChange={(e) => setEditor(prev => ({ ...prev, header: { ...prev.header, plan_date: e.target.value } }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Remarks</label>
            <input
              type="text"
              value={editor.header.remarks || ''}
              onChange={(e) => setEditor(prev => ({ ...prev, header: { ...prev.header, remarks: e.target.value } }))}
              placeholder="Optional..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-4">
          <button onClick={() => setShowNewArticleModal(true)} className="flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700">
            <Plus size={14} /> New Article
          </button>
        </div>
      </div>

      {/* Combos */}
      {editor.curSheet ? (
        <>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-700">Color Combos</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{editor.combos.length} Colors</span>
            </div>
            <div className="flex gap-2">
              <button onClick={addCombo} className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg border border-gray-300 hover:bg-gray-50"><Plus size={14} /> Add Color</button>
              <button onClick={copyLastCombo} className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700"><Copy size={14} /> Copy Last</button>
            </div>
          </div>

          {editor.combos.map((combo, comboIdx) => (
            <div key={comboIdx} className="bg-white rounded-lg shadow overflow-hidden">
              {/* Combo Header */}
              <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-sm font-bold">C{comboIdx + 1}</span>
                  <span className="font-medium text-gray-700">{combo.color_name || 'New Color'}</span>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => { const cp = JSON.parse(JSON.stringify(combo)); cp.combo_sr_no = editor.combos.length + 1; cp.color_id = ''; cp.color_code = ''; cp.color_name = ''; cp.combo_name = ''; setEditor(prev => ({ ...prev, combos: [...prev.combos, cp] })); toast.success('Color duplicated') }} className="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50">Copy</button>
                  <button onClick={() => removeCombo(comboIdx)} className="px-2 py-1 text-xs rounded bg-red-50 text-red-600 hover:bg-red-100"><X size={14} /></button>
                </div>
              </div>

              {/* Combo Meta */}
              <div className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Combo Sr No.</label>
                    <input type="text" value={combo.combo_sr_no || ''} onChange={(e) => updateCombo(comboIdx, 'combo_sr_no', e.target.value)} className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Color (from Master)</label>
                    <select
                      value={`${combo.color_id}|${combo.color_code}|${combo.color_name}`}
                      onChange={(e) => { const parts = e.target.value.split('|'); if (parts.length === 3) { updateCombo(comboIdx, 'color_id', parts[0]); updateCombo(comboIdx, 'color_code', parts[1]); updateCombo(comboIdx, 'color_name', parts[2]); updateCombo(comboIdx, 'combo_name', parts[2]) } }}
                      className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
                    >
                      <option value="">-- Select --</option>
                      {master.colors.map((c, i) => <option key={i} value={`${c.id}|${c.code}|${c.name}`}>{c.id}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Color Code</label>
                    <input type="text" value={combo.color_code || ''} onChange={(e) => updateCombo(comboIdx, 'color_code', e.target.value)} className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Color Name</label>
                    <input type="text" value={combo.color_name || ''} onChange={(e) => { updateCombo(comboIdx, 'color_name', e.target.value); updateCombo(comboIdx, 'combo_name', e.target.value) }} className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Lot No.</label>
                    <input type="number" value={combo.lot_no || ''} onChange={(e) => updateCombo(comboIdx, 'lot_no', e.target.value)} className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Plan Qty (Pcs)</label>
                    <input type="number" value={combo.plan_qty || ''} onChange={(e) => updateCombo(comboIdx, 'plan_qty', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                </div>

                {/* BOM Lines Table */}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase" style={{minWidth:'200px'}}>Fabric Quality</th>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase" style={{width:'90px'}}>GSM/Width</th>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase" style={{width:'50px'}}>Prio</th>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase" style={{minWidth:'180px'}}>Component</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'75px'}}>AVG</th>
                        <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase" style={{width:'70px'}}>Unit</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'65px'}}>Extra%</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'65px'}}>Waste%</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'65px'}}>Short%</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'90px'}}>Ready Need</th>
                        <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase" style={{width:'90px'}}>Greige Need</th>
                        <th className="px-2 py-2" style={{width:'40px'}}></th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                      {combo.bom_lines.map((line, lineIdx) => (
                        <tr key={lineIdx} className="hover:bg-gray-50">
                          <td className="px-1 py-1"><input value={line.fabric_quality || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'fabric_quality', e.target.value)} list="fabricList" placeholder="Type fabric..." className="w-full border border-gray-300 rounded px-2 py-1 text-sm" /></td>
                          <td className="px-1 py-1"><input value={line.plan_rat_gsm || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'plan_rat_gsm', e.target.value)} placeholder='180/68"' className="w-full border border-gray-300 rounded px-2 py-1 text-sm" /></td>
                          <td className="px-1 py-1"><input type="number" value={line.priority || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'priority', e.target.value)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-center" /></td>
                          <td className="px-1 py-1"><input value={line.component || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'component', e.target.value)} list="componentList" placeholder="Component..." className="w-full border border-gray-300 rounded px-2 py-1 text-sm" /></td>
                          <td className="px-1 py-1"><input type="number" step="0.001" value={line.avg || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'avg', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right" /></td>
                          <td className="px-1 py-1">
                            <select value={line.unit || 'kg'} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'unit', e.target.value)} className="w-full border border-gray-300 rounded px-1 py-1 text-sm">
                              {['kg', 'Pcs', 'Meter', 'Cuts'].map(u => <option key={u} value={u}>{u}</option>)}
                            </select>
                          </td>
                          <td className="px-1 py-1"><input type="number" step="0.01" value={line.extra_pcs || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'extra_pcs', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right" /></td>
                          <td className="px-1 py-1"><input type="number" step="0.01" value={line.wastage_pcs || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'wastage_pcs', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right" /></td>
                          <td className="px-1 py-1"><input type="number" step="0.01" value={line.shortage || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'shortage', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right" /></td>
                          <td className="px-2 py-1 text-right font-mono text-gray-600 bg-gray-50 rounded">{calculateReadyNeed(combo, line).toFixed(2)}</td>
                          <td className="px-1 py-1">
                            {line.unit === 'Pcs' ? (
                              <input type="number" value={line.greige_fabric_need || ''} onChange={(e) => updateBOMLine(comboIdx, lineIdx, 'greige_fabric_need', parseFloat(e.target.value) || 0)} className="w-full border border-gray-300 rounded px-2 py-1 text-sm text-right" />
                            ) : (
                              <div className="text-right font-mono text-gray-600 bg-gray-50 rounded px-2 py-1">{calculateGreigeNeed(combo, line).toFixed(2)}</div>
                            )}
                          </td>
                          <td className="px-1 py-1"><button onClick={() => removeBOMLine(comboIdx, lineIdx)} className="p-1 text-red-500 hover:bg-red-50 rounded"><X size={14} /></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <button onClick={() => addBOMLine(comboIdx)} className="mt-2 flex items-center gap-1 px-3 py-1.5 text-xs rounded border border-gray-300 hover:bg-gray-50"><Plus size={12} /> Add BOM Line</button>
              </div>
            </div>
          ))}
        </>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400">
          <FileText size={48} className="mb-4" />
          <h3 className="text-lg font-medium text-gray-500">Select an Article to Begin</h3>
          <p className="text-sm mt-1">Choose an existing article from the dropdown, or create a new one.</p>
        </div>
      )}

      {/* Datalists */}
      <datalist id="fabricList">{master.fabrics.map((f, i) => <option key={i} value={f.quality} />)}</datalist>
      <datalist id="componentList">{master.components.map((c, i) => <option key={i} value={c} />)}</datalist>

      {/* New Article Modal */}
      {showNewArticleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowNewArticleModal(false)}>
          <div className="bg-white rounded-lg shadow-xl p-6 w-[420px]" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-4">Create New Article Sheet</h3>
            <div className="mb-4">
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Article Number</label>
              <input type="text" value={newArtNo} onChange={(e) => setNewArtNo(e.target.value)} placeholder="e.g. 4567 HP" autoFocus className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowNewArticleModal(false)} className="px-4 py-2 text-sm rounded-lg border border-gray-300 hover:bg-gray-50">Cancel</button>
              <button onClick={createNewArticle} className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700">Create Sheet</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
