import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { bomApi } from '../services/api'

export function useBomData() {
  const [master, setMaster] = useState({
    articles: [], colors: [], components: [],
    units: ['kg', 'Pcs', 'Meter', 'Cuts'],
    master_articles: [], fabrics: [],
  })
  const [loading, setLoading] = useState(false)
  const [demoMode, setDemoMode] = useState(false)

  const loadMasterData = useCallback(async () => {
    try {
      setLoading(true)
      const statusRes = await bomApi.getStatus()
      setDemoMode(statusRes.data.demo_mode)
      const res = await bomApi.loadMasterData()
      setMaster(res.data)
    } catch (err) {
      toast.error('Failed to load BOM master data: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadMasterData() }, [loadMasterData])

  const calculateReadyNeed = (combo, line) => {
    const pq = parseFloat(combo.plan_qty) || 0
    const avg = parseFloat(line.avg) || 0
    const extra = parseFloat(line.extra_pcs) || 0
    const waste = parseFloat(line.wastage_pcs) || 0
    return (pq + pq * extra + pq * waste) * avg
  }

  const calculateGreigeNeed = (combo, line) => {
    if (line.unit === 'Pcs') return parseFloat(line.greige_fabric_need) || 0
    const readyNeed = calculateReadyNeed(combo, line)
    const shortage = parseFloat(line.shortage) || 0
    return readyNeed * (1 + shortage)
  }

  const getArticleOptions = () => {
    const sheetMap = {}
    master.articles.forEach(a => { sheetMap[a.art_no.trim()] = a })
    const options = []
    const addedArts = new Set()

    master.master_articles.forEach(ma => {
      const artNo = ma.art_no
      const existing = sheetMap[artNo]
      options.push({
        value: existing ? existing.sheet_name : `MASTER:${artNo}`,
        label: existing
          ? `${artNo}${existing.season ? ` (${existing.season})` : ''} \u2714`
          : `${artNo} [New]`
      })
      addedArts.add(artNo)
    })

    master.articles.forEach(a => {
      if (!addedArts.has(a.art_no.trim())) {
        options.push({
          value: a.sheet_name,
          label: `${a.art_no}${a.season ? ` (${a.season})` : ''} \u2714`
        })
      }
    })

    return options
  }

  return {
    master, loading, setLoading, demoMode,
    loadMasterData,
    calculateReadyNeed, calculateGreigeNeed,
    getArticleOptions,
  }
}
