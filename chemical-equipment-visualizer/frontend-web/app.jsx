const { useState, useEffect, useRef } = React;

const API_URL = 'http://127.0.0.1:8000/api/equipment/';

function App(){
  const [token, setToken] = React.useState(localStorage.getItem('token') || '');
  function saveToken(t){ setToken(t); localStorage.setItem('token', t); }

  function login(e){
    e.preventDefault();
    const form = e.target;
    const u = form.username.value; const p = form.password.value;
    fetch('http://127.0.0.1:8000/api-token-auth/', { method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username:u,password:p}) })
      .then(r=>r.json())
      .then(d=>{ if (d.token){ saveToken(d.token); alert('Login successful'); } else alert('Login failed'); })
      .catch(()=>alert('Login failed'));
  }

  const [data, setData] = useState([]);
  const [next, setNext] = useState(null);
  const [prev, setPrev] = useState(null);
  const [search, setSearch] = useState('');
  const [pressure, setPressure] = useState('');
  const [temperature, setTemperature] = useState('');
  const [material, setMaterial] = useState('');
  const [sortField, setSortField] = useState('');
  const [sortDir, setSortDir] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalItem, setModalItem] = useState(null);

  const pressureRef = useRef();
  const tempRef = useRef();
  const pressureChartRef = useRef(null);
  const tempChartRef = useRef(null);

  const [datasets, setDatasets] = useState([]);

  useEffect(()=>{ fetchData(API_URL); fetchDatasets(); }, []);

  function fetchDatasets(){
    fetch('http://127.0.0.1:8000/api/datasets/')
      .then(r=>r.json())
      .then(d=>{ setDatasets(d || []); })
      .catch(()=>{});
  }

  function fetchData(url){
    setLoading(true);
    fetch(url)
      .then(r=>r.json())
      .then(d=>{
        setData(d.results||[]);
        setNext(d.next);
        setPrev(d.previous);
        setLoading(false);
      })
      .catch(()=>{ setLoading(false); })
  }

  function applyFilters(){
    let params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (pressure) params.push(`pressure__gte=${pressure}`);
    if (temperature) params.push(`temperature__gte=${temperature}`);
    if (material) params.push(`material=${encodeURIComponent(material)}`);
    if (sortField) params.push(`ordering=${sortDir}${sortField}`);
    let u = API_URL + (params.length ? '?' + params.join('&') : '');
    fetchData(u);
  }

  function setSort(field){
    if (sortField === field){
      setSortDir(sortDir === '' ? '-' : '');
    } else {
      setSortField(field);
      setSortDir('');
    }
    setTimeout(applyFilters, 0);
  }

  useEffect(()=>{
    // draw charts
    const labels = data.map(d=>d.name);
    const pressures = data.map(d=>d.pressure);
    const temps = data.map(d=>d.temperature);

    if (pressureChartRef.current) pressureChartRef.current.destroy();
    if (tempChartRef.current) tempChartRef.current.destroy();

    if (pressureRef.current){
      pressureChartRef.current = new Chart(pressureRef.current, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Pressure', data: pressures }] }
      });
    }

    if (tempRef.current){
      tempChartRef.current = new Chart(tempRef.current, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Temperature', data: temps }] }
      });
    }
  }, [data]);

  function openModal(item){ setModalItem(item); }
  function closeModal(){ setModalItem(null); }

  function exportCSV(){
    let params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (pressure) params.push(`pressure__gte=${pressure}`);
    if (temperature) params.push(`temperature__gte=${temperature}`);
    if (material) params.push(`material=${encodeURIComponent(material)}`);
    window.location.href = `http://127.0.0.1:8000/api/equipment/export/csv/?${params.join('&')}`;
  }

  function uploadCSV(){
    const input = document.getElementById('csvFile');
    if (!input.files.length){ alert('Select CSV first'); return; }
    const fd = new FormData();
    fd.append('file', input.files[0]);
    const headers = token ? { 'Authorization': `Token ${token}` } : {};
    fetch('http://127.0.0.1:8000/api/upload/', { method: 'POST', body: fd, headers })
      .then(r=>{
        if (!r.ok) throw new Error('Upload failed');
        return r.json();
      })
      .then(d=>{ alert(`Uploaded; created ${d.created}`); fetchData(API_URL); fetchDatasets(); })
      .catch(()=>alert('Upload failed'))
  }

  const materials = [...new Set(data.map(d=>d.material).filter(Boolean))];

  return (
    <div className="container">
      <h2>Chemical Equipment Visualizer</h2>
      {loading ? <p id="loading">🔄 Loading...</p> : null}

      <div className="filters">
        <input type="file" id="csvFile" accept=".csv" />
        <button onClick={uploadCSV}>⬆ Upload CSV</button>

        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by name" />
        <input value={pressure} onChange={e=>setPressure(e.target.value)} type="number" placeholder="Min Pressure" />
        <input value={temperature} onChange={e=>setTemperature(e.target.value)} type="number" placeholder="Min Temperature" />

        <select value={material} onChange={e=>setMaterial(e.target.value)}>
          <option value="">All Materials</option>
          {materials.map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <button onClick={applyFilters}>Apply</button>

        <form onSubmit={login} style={{display:'inline-block', marginLeft: 10}}>
          <input name="username" placeholder="username" />
          <input name="password" placeholder="password" type="password" />
          <button type="submit">Login</button>
        </form>
      </div>

      <div className="card" style={{textAlign: 'right'}}>
        <button onClick={exportCSV}>⬇ Export CSV</button>
      </div>

      <div className="card">
        <label>Datasets:</label>
        <select id="datasetSelect">
          <option value="">-- Select Dataset --</option>
          {datasets.map(ds => <option key={ds.id} value={ds.id}>{ds.name} ({ds.equipment_count})</option>)}
        </select>
        <button onClick={()=>{
            const s = document.getElementById('datasetSelect').value; if(!s){ alert('Select dataset'); return; }
            // download report
            const headers = token ? { 'Authorization': `Token ${token}` } : {};
            fetch(`http://127.0.0.1:8000/api/datasets/${s}/report/pdf/`, { headers })
              .then(res=>{
                if (res.status === 501) { alert('Server does not support PDF generation (reportlab missing).'); return null; }
                if (res.status === 401 || res.status === 403){ alert('Authentication required for report. Please login.'); return null; }
                return res.blob();
              })
              .then(blob=>{
                if (!blob) return;
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = `dataset_${s}.pdf`; a.click();
              })
              .catch(()=> alert('Failed to download report'));
        }}>Download Report</button>
      </div>

      <div className="card">
        <h3>Pressure (bar)</h3>
        <canvas ref={pressureRef}></canvas>
      </div>

      <div className="card">
        <h3>Temperature (°C)</h3>
        <canvas ref={tempRef}></canvas>
      </div>

      <div className="card">
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
            {data.length === 0 ? <tr><td colSpan={5}>No equipment found</td></tr> : data.map(item=> (
              <tr key={item.id} onClick={()=>openModal(item)}>
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

      <div className="card" style={{textAlign: 'center'}}>
        <button disabled={!prev} onClick={()=>prev && fetchData(prev)}>⬅ Previous</button>
        <button disabled={!next} onClick={()=>next && fetchData(next)}>Next ➡</button>
      </div>

      {modalItem ? (
        <div id="modal" style={{display:'block', position:'fixed', inset:0, background:'rgba(0,0,0,0.5)'}} onClick={closeModal}>
          <div id="modal-content" style={{background:'white', width:400, margin:'100px auto', padding:20}} onClick={e=>e.stopPropagation()}>
            <h3>{modalItem.name}</h3>
            <p><b>Type:</b> {modalItem.type}</p>
            <p><b>Material:</b> {modalItem.material}</p>
            <p><b>Flowrate:</b> {modalItem.flowrate}</p>
            <p><b>Pressure:</b> {modalItem.pressure} bar</p>
            <p><b>Temperature:</b> {modalItem.temperature} °C</p>
            <p><b>Description:</b> {modalItem.description || '—'}</p>
            <button onClick={closeModal}>Close</button>
          </div>
        </div>
      ) : null}

    </div>
  );
}

ReactDOM.render(<App/>, document.getElementById('root'));
