import React, { useEffect, useState, useRef } from 'react'
import Chart from 'chart.js/auto'
import './index.css'

const API_URL = 'http://127.0.0.1:8000/api/equipment/'

export default function App(){
  const [data, setData] = useState([])
  const [next, setNext] = useState(null)
  const [prev, setPrev] = useState(null)
  const [search, setSearch] = useState('')
  const [pressure, setPressure] = useState('')
  const [temperature, setTemperature] = useState('')
  const [material, setMaterial] = useState('')
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalItem, setModalItem] = useState(null)
  const [toast, setToast] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [showOnboard, setShowOnboard] = useState(!localStorage.getItem('seen_onboard'))

  const pressureRef = useRef(null)
  const tempRef = useRef(null)
  const pressureChartRef = useRef(null)
  const tempChartRef = useRef(null)

  useEffect(()=>{ fetchData(API_URL); fetchDatasets(); }, [])

  function fetchData(url){
    setLoading(true)
    fetch(url)
      .then(r=>r.json())
      .then(d=>{ setData(d.results||[]); setNext(d.next); setPrev(d.previous); setLoading(false) })
      .catch(()=>{ setLoading(false); setToast('Could not load equipment. Is the backend running?') })
  }

  function fetchDatasets(){
    fetch('http://127.0.0.1:8000/api/datasets/')
      .then(r=>r.json())
      .then(d=>setDatasets(d||[]))
      .catch(()=>setToast('Could not load datasets'))
  }

  function applyFilters(){
    let params = []
    if (search) params.push(`search=${encodeURIComponent(search)}`)
    if (pressure) params.push(`pressure__gte=${pressure}`)
    if (temperature) params.push(`temperature__gte=${temperature}`)
    if (material) params.push(`material=${encodeURIComponent(material)}`)
    const url = API_URL + (params.length ? '?' + params.join('&') : '')
    fetchData(url)
  }

  function setSort(field){
    if (window.sortField === field) {
      window.sortDir = window.sortDir === '' ? '-' : ''
    } else {
      window.sortField = field
      window.sortDir = ''
    }
    const params = []
    if (window.sortField) params.push(`ordering=${window.sortDir}${window.sortField}`)
    const url = API_URL + (params.length ? '?' + params.join('&') : '')
    fetchData(url)
  }

  useEffect(()=>{
    const labels = data.map(d=>d.name)
    const pressures = data.map(d=>d.pressure)
    const temps = data.map(d=>d.temperature)

    if (pressureChartRef.current) pressureChartRef.current.destroy()
    if (tempChartRef.current) tempChartRef.current.destroy()

    const pressureOptions = { type: 'bar', data: { labels, datasets: [{ label: 'Pressure', data: pressures, backgroundColor: '#FF8A80' }] }, options: { responsive:true, plugins:{ legend:{ display:false }, tooltip:{ mode:'index', intersect:false } }, animation:{ duration:600 } } }
    const tempOptions = { type: 'line', data: { labels, datasets: [{ label: 'Temperature', data: temps, borderColor: '#FFB86B', fill:false, tension:0.2 }] }, options: { responsive:true, plugins:{ tooltip:{ mode:'nearest' } }, animation:{ duration:600 } } }

    if (pressureRef.current){
      pressureChartRef.current = new Chart(pressureRef.current, pressureOptions)
    }
    if (tempRef.current){
      tempChartRef.current = new Chart(tempRef.current, tempOptions)
    }
  }, [data])

  function uploadCSV(file){
    if (!file){ setToast('Please select a CSV file'); return }
    const fd = new FormData(); fd.append('file', file)
    const headers = token ? { 'Authorization': `Token ${token}` } : {}
    setToast('Uploading...')
    fetch('http://127.0.0.1:8000/api/upload/', { method: 'POST', body: fd, headers })
      .then(res=>{ if (!res.ok) throw new Error('Upload failed'); return res.json() })
      .then(d=>{ setToast(`Uploaded — ${d.created} rows`); fetchData(API_URL); fetchDatasets(); setTimeout(()=>setToast(''),3000) })
      .catch(e=>{ setToast(`Upload failed: ${e.message || 'unknown'}`); setTimeout(()=>setToast(''),4000) })
  }

  function handleDrop(e){
    e.preventDefault(); setDragOver(false)
    const f = e.dataTransfer.files && e.dataTransfer.files[0]
    if (f) uploadCSV(f)
  }

  function login(e){
    e.preventDefault();
    const u = e.target.username.value; const p = e.target.password.value
    fetch('http://127.0.0.1:8000/api-token-auth/', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username:u,password:p}) })
      .then(r=>r.json())
      .then(d=>{ if (d.token){ setToken(d.token); localStorage.setItem('token', d.token); setToast('Logged in — token saved'); setTimeout(()=>setToast(''),2000) } else setToast('Login failed') })
      .catch(()=>setToast('Login failed'))
  }

  function downloadReport(dsid){
    const headers = token ? { 'Authorization': `Token ${token}` } : {}
    fetch(`http://127.0.0.1:8000/api/datasets/${dsid}/report/pdf/`, { headers })
      .then(res=>{
        if (res.status === 501) { setToast('Server does not support PDF generation (reportlab missing).'); return null; }
        if (res.status === 401 || res.status === 403){ setToast('Authentication required for report. Please login.'); return null; }
        return res.blob();
      })
      .then(blob=>{
        if (!blob) return; const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `dataset_${dsid}.pdf`; a.click(); setToast('Report downloaded')
      })
      .catch(()=> setToast('Failed to download report'))
  }

  const materials = [...new Set(data.map(d=>d.material).filter(Boolean))]

  return (
    <div className="container">
      <div className="header">
        <div className="brand">
          <div className="logo">CE</div>
          <div>
            <div className="title">Chemical Equipment Visualizer</div>
            <div className="subtitle">Upload CSVs, explore equipment, and generate reports — with a friendly interface.</div>
          </div>
        </div>
        <div className="actions">
          <button className="btn" onClick={()=>document.getElementById('csvFile').click()}>Upload CSV</button>
          <button className="btn secondary" onClick={()=>window.location.href = `http://127.0.0.1:8000/api/equipment/export/csv/`}>Export CSV</button>
        </div>
      </div>

      {showOnboard && (
        <div className="card hero">
          <div className="intro">
            <h1>Welcome 👋</h1>
            <p>Start by uploading a CSV of equipment. You can drag & drop files or click <b>Upload CSV</b>. Try the sample dataset to get familiar.</p>
          </div>
          <div style={{width:240}}>
            <div className="upload-area" onClick={()=>document.getElementById('csvFile').click()}>
              <p style={{margin:0}}>Drop CSV here or click to browse</p>
              <p className="small">We accept comma-separated files matching the template.</p>
            </div>
          </div>
          <button style={{marginLeft:10}} className="btn secondary" onClick={()=>{ localStorage.setItem('seen_onboard','1'); setShowOnboard(false) }}>Got it</button>
        </div>
      )}

      <input id="csvFile" type="file" accept=".csv" style={{display:'none'}} onChange={e=>uploadCSV(e.target.files[0])} />

      <div className="card-grid">
        <div className="card">
          <h3>Pressure</h3>
          <div className="canvas-wrap"><canvas ref={pressureRef}></canvas></div>
        </div>
        <div className="card">
          <h3>Temperature</h3>
          <div className="canvas-wrap"><canvas ref={tempRef}></canvas></div>
        </div>
        <div className="card">
          <h3>Filters</h3>
          <div className="filters">
            <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by name" />
            <input value={pressure} onChange={e=>setPressure(e.target.value)} type="number" placeholder="Min Pressure" />
            <input value={temperature} onChange={e=>setTemperature(e.target.value)} type="number" placeholder="Min Temperature" />
            <select value={material} onChange={e=>setMaterial(e.target.value)}>
              <option value="">All Materials</option>
              {materials.map(m=> <option key={m} value={m}>{m}</option>)}
            </select>
            <button className="btn secondary" onClick={applyFilters}>Apply</button>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Datasets</h3>
        {datasets.length === 0 ? <div className="empty-state">No datasets yet — upload a CSV to get started.</div> : (
          <div style={{display:'flex', gap:12, flexWrap:'wrap'}}>
            {datasets.map(ds=> (
              <div key={ds.id} className="card" style={{minWidth:220}}>
                <strong>{ds.name}</strong>
                <div className="small">{ds.equipment_count} items • uploaded {new Date(ds.uploaded_at).toLocaleString()}</div>
                <div style={{marginTop:10}}>
                  <button className="btn" onClick={()=>downloadReport(ds.id)}>Download Report</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3>Equipment list</h3>
        <div className="table">
          <table>
            <thead>
              <tr>
                <th onClick={()=>setSort('name')}>Name ⬍</th>
                <th onClick={()=>setSort('type')}>Type ⬍</th>
                <th onClick={()=>setSort('material')}>Material ⬍</th>
                <th onClick={()=>setSort('pressure')}>Pressure ⬍</th>
                <th onClick={()=>setSort('temperature')}>Temperature ⬍</th>
              </tr>
            </thead>
            <tbody>
              {data.length === 0 ? <tr><td colSpan={5}>No equipment found — try uploading a sample CSV</td></tr> : data.map(item=> (
                <tr key={item.id} onClick={()=>setModalItem(item)}>
                  <td>{item.name}</td>
                  <td>{item.type}</td>
                  <td>{item.material}</td>
                  <td>{item.pressure}</td>
                  <td>{item.temperature}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modalItem && (
        <div id="modal" style={{display:'block', position:'fixed', inset:0, background:'rgba(0,0,0,0.5)'}} onClick={()=>setModalItem(null)}>
          <div className="modal-inner" onClick={e=>e.stopPropagation()}>
            <h3>{modalItem.name}</h3>
            <p><b>Type:</b> {modalItem.type}</p>
            <p><b>Material:</b> {modalItem.material}</p>
            <p><b>Flowrate:</b> {modalItem.flowrate}</p>
            <p><b>Pressure:</b> {modalItem.pressure} bar</p>
            <p><b>Temperature:</b> {modalItem.temperature} °C</p>
            <p><b>Description:</b> {modalItem.description || '—'}</p>
            <button className="btn secondary" onClick={()=>setModalItem(null)}>Close</button>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}
