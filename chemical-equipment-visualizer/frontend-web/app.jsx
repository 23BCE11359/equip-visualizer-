const { useState, useEffect, useRef } = React;

// Get the URL from Vercel (or use localhost if running locally)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const API_URL = `${BASE_URL}/api/equipment/`;
const AUTH_URL = `${BASE_URL}/api-token-auth/`;

function App() {
  // 1. STATE: Manage Token & Auth
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [loginError, setLoginError] = useState('');

  // 2. STATE: Dashboard Data
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
  const [datasets, setDatasets] = useState([]);

  // Refs for Charts
  const pressureRef = useRef();
  const tempRef = useRef();
  const pressureChartRef = useRef(null);
  const tempChartRef = useRef(null);

  // 3. EFFECT: Fetch Data only if Token exists
  useEffect(() => {
    if (token) {
      fetchData(API_URL);
      fetchDatasets();
    }
  }, [token]);

  // 4. AUTH FUNCTIONS
  function handleLogin(e) {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;

    fetch(AUTH_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    .then(r => {
      if (!r.ok) throw new Error('Invalid credentials');
      return r.json();
    })
    .then(d => {
      if (d.token) {
        setToken(d.token);
        localStorage.setItem('token', d.token);
        setLoginError('');
      }
    })
    .catch(err => setLoginError('Login failed: ' + err.message));
  }

  function handleLogout() {
    setToken('');
    localStorage.removeItem('token');
    setData([]);
  }

  // Helper to get Headers
  function getHeaders() {
    return token ? { 
      'Authorization': `Token ${token}`, // Change to 'Bearer ${token}' if using JWT
      'Content-Type': 'application/json'
    } : { 'Content-Type': 'application/json' };
  }

  // 5. DATA FUNCTIONS
  function fetchDatasets() {
    fetch(`${BASE_URL}/api/datasets/`, { headers: getHeaders() })
      .then(r => r.json())
      .then(d => setDatasets(d || []))
      .catch(console.error);
  }

  function fetchData(url) {
    setLoading(true);
    fetch(url, { headers: getHeaders() })
      .then(r => {
        if (r.status === 401) { handleLogout(); throw new Error("Unauthorized"); }
        return r.json();
      })
      .then(d => {
        setData(d.results || []);
        setNext(d.next);
        setPrev(d.previous);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }

  function applyFilters() {
    let params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (pressure) params.push(`pressure__gte=${pressure}`);
    if (temperature) params.push(`temperature__gte=${temperature}`);
    if (material) params.push(`material=${encodeURIComponent(material)}`);
    if (sortField) params.push(`ordering=${sortDir}${sortField}`);
    let u = API_URL + (params.length ? '?' + params.join('&') : '');
    fetchData(u);
  }

  function setSort(field) {
    if (sortField === field) {
      setSortDir(sortDir === '' ? '-' : '');
    } else {
      setSortField(field);
      setSortDir('');
    }
    setTimeout(applyFilters, 0);
  }

  // 6. CHART DRAWING
  useEffect(() => {
    if (!data.length) return;

    const labels = data.map(d => d.name);
    const pressures = data.map(d => d.pressure);
    const temps = data.map(d => d.temperature);

    if (pressureChartRef.current) pressureChartRef.current.destroy();
    if (tempChartRef.current) tempChartRef.current.destroy();

    if (pressureRef.current) {
      pressureChartRef.current = new Chart(pressureRef.current, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Pressure', data: pressures, backgroundColor: 'rgba(255, 99, 132, 0.5)' }] }
      });
    }

    if (tempRef.current) {
      tempChartRef.current = new Chart(tempRef.current, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Temperature', data: temps, borderColor: 'rgba(54, 162, 235, 1)', fill: false }] }
      });
    }
  }, [data]);

  // 7. ACTION HANDLERS
  function openModal(item) { setModalItem(item); }
  function closeModal() { setModalItem(null); }

  // FIX: Use fetch with blob instead of window.location for Export
  function exportCSV() {
    let params = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (pressure) params.push(`pressure__gte=${pressure}`);
    if (temperature) params.push(`temperature__gte=${temperature}`);
    if (material) params.push(`material=${encodeURIComponent(material)}`);
    
    const url = `${BASE_URL}/api/equipment/export/csv/?${params.join('&')}`;

    fetch(url, { headers: getHeaders() })
      .then(r => r.blob())
      .then(blob => {
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'equipment_export.csv';
        link.click();
      })
      .catch(() => alert("Export Failed (Auth Error)"));
  }

  function uploadCSV() {
    const input = document.getElementById('csvFile');
    if (!input.files.length) { alert('Select CSV first'); return; }
    
    const fd = new FormData();
    fd.append('file', input.files[0]);
    
    // Note: Don't set Content-Type header manually for FormData, browser does it with boundary
    const headers = { 'Authorization': `Token ${token}` }; 

    fetch(`${BASE_URL}/api/upload/`, { method: 'POST', body: fd, headers })
      .then(r => {
        if (!r.ok) throw new Error('Upload failed');
        return r.json();
      })
      .then(d => { alert(`Uploaded; created ${d.created}`); fetchData(API_URL); fetchDatasets(); })
      .catch(() => alert('Upload failed'));
  }

  // --- RENDERING ---

  // RENDER: Login Screen (If no token)
  if (!token) {
    return (
      <div className="container" style={{maxWidth: '400px', marginTop: '100px', textAlign:'center'}}>
        <div className="card">
          <h2>🔐 Login Required</h2>
          <form onSubmit={handleLogin}>
            <div style={{marginBottom: 10}}>
              <input name="username" placeholder="Username" style={{width:'100%', padding: 10}} required />
            </div>
            <div style={{marginBottom: 10}}>
              <input name="password" placeholder="Password" type="password" style={{width:'100%', padding: 10}} required />
            </div>
            <button type="submit" style={{width:'100%'}}>Login</button>
            {loginError && <p style={{color:'red', marginTop: 10}}>{loginError}</p>}
          </form>
        </div>
      </div>
    );
  }

  // RENDER: Dashboard (If token exists)
  const materials = [...new Set(data.map(d => d.material).filter(Boolean))];

  return (
    <div className="container">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h2>Chemical Equipment Visualizer</h2>
        <button onClick={handleLogout} style={{background: '#dc3545'}}>Logout</button>
      </div>
      
      {loading ? <p id="loading">🔄 Loading...</p> : null}

      <div className="filters">
        <input type="file" id="csvFile" accept=".csv" />
        <button onClick={uploadCSV}>⬆ Upload CSV</button>

        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name" />
        <input value={pressure} onChange={e => setPressure(e.target.value)} type="number" placeholder="Min Pressure" />
        <input value={temperature} onChange={e => setTemperature(e.target.value)} type="number" placeholder="Min Temperature" />

        <select value={material} onChange={e => setMaterial(e.target.value)}>
          <option value="">All Materials</option>
          {materials.map(m => <option key={m} value={m}>{m}</option>)}
        </select>

        <button onClick={applyFilters}>Apply</button>
      </div>

      <div className="card" style={{ textAlign: 'right' }}>
        <button onClick={exportCSV}>⬇ Export CSV</button>
      </div>

      <div className="card">
        <label>Datasets:</label>
        <select id="datasetSelect" style={{marginLeft: 10, marginRight: 10}}>
          <option value="">-- Select Dataset --</option>
          {datasets.map(ds => <option key={ds.id} value={ds.id}>{ds.name} ({ds.equipment_count})</option>)}
        </select>
        
        <button onClick={() => {
            const s = document.getElementById('datasetSelect').value;
            if (!s) { alert('Select dataset'); return; }
            
            // Download PDF Report
            fetch(`${BASE_URL}/api/datasets/${s}/report/pdf/`, { headers: getHeaders() })
              .then(res => {
                if (res.status === 501) { alert('Server missing PDF library.'); return null; }
                if (res.status === 401 || res.status === 403) { 
                    alert('Session expired. Logging out...'); 
                    handleLogout();
                    return null; 
                }
                if (!res.ok) throw new Error('Download failed');
                return res.blob();
              })
              .then(blob => {
                if (!blob) return;
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `dataset_${s}.pdf`;
                a.click();
              })
              .catch(err => console.error(err));
        }}>Download Report</button>
      </div>

      <div style={{display:'flex', gap: 20}}>
        <div className="card" style={{flex:1}}>
          <h3>Pressure (bar)</h3>
          <canvas ref={pressureRef}></canvas>
        </div>
        <div className="card" style={{flex:1}}>
          <h3>Temperature (°C)</h3>
          <canvas ref={tempRef}></canvas>
        </div>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th onClick={() => setSort('name')}>Name ⬍</th>
              <th onClick={() => setSort('type')}>Type ⬍</th>
              <th onClick={() => setSort('material')}>Material ⬍</th>
              <th onClick={() => setSort('pressure')}>Pressure ⬍</th>
              <th onClick={() => setSort('temperature')}>Temperature ⬍</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan={5}>No equipment found</td></tr> : data.map(item => (
              <tr key={item.id} onClick={() => openModal(item)}>
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

      <div className="card" style={{ textAlign: 'center' }}>
        <button disabled={!prev} onClick={() => prev && fetchData(prev)}>⬅ Previous</button>
        <button disabled={!next} onClick={() => next && fetchData(next)}>Next ➡</button>
      </div>

      {modalItem ? (
        <div id="modal" style={{ display: 'block', position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)' }} onClick={closeModal}>
          <div id="modal-content" style={{ background: 'white', width: 400, margin: '100px auto', padding: 20, borderRadius: 8 }} onClick={e => e.stopPropagation()}>
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

ReactDOM.render(<App />, document.getElementById('root'));