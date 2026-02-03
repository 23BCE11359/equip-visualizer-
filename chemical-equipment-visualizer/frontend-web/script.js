console.log("JS FILE LOADED ✅");

const API_URL = "http://127.0.0.1:8000/api/equipment/";

let currentSort = "";
let sortDirection = "";
let equipmentData = [];

let pressureChart = null;
let temperatureChart = null;

let nextPage = null;
let prevPage = null;

// INPUT REFERENCES
const searchInput = document.getElementById("searchInput");
const pressureInput = document.getElementById("pressureInput");
const temperatureInput = document.getElementById("temperatureInput");
const materialInput = document.getElementById("materialInput");
const loading = document.getElementById("loading");

// BUTTONS
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

/* ================= FETCH DATA ================= */

function fetchData(url) {
    loading.style.display = "block";

    fetch(url)
        .then(res => res.json())
        .then(data => {
            equipmentData = data.results || [];
            nextPage = data.next;
            prevPage = data.previous;

            renderTable(equipmentData);
            drawCharts(equipmentData);
            populateMaterials(equipmentData);
            updateButtons();

            loading.style.display = "none";
        })
        .catch(err => {
            console.error(err);
            loading.innerText = "❌ Failed to load data";
        });
}

fetchData(API_URL);

/* ================= SORTING ================= */

function setSort(field) {
    if (currentSort === field) {
        sortDirection = sortDirection === "" ? "-" : "";
    } else {
        currentSort = field;
        sortDirection = "";
    }
    applyFilters();
}

/* ================= FILTERS ================= */

function applyFilters() {
    let params = [];

    if (searchInput.value)
        params.push(`search=${encodeURIComponent(searchInput.value)}`);

    if (pressureInput.value)
        params.push(`pressure__gte=${pressureInput.value}`);

    if (temperatureInput.value)
        params.push(`temperature__gte=${temperatureInput.value}`);

    if (materialInput.value)
        params.push(`material=${encodeURIComponent(materialInput.value)}`);

    if (currentSort)
        params.push(`ordering=${sortDirection}${currentSort}`);

    let url = API_URL;
    if (params.length) url += "?" + params.join("&");

    fetchData(url);
}

/* ================= PAGINATION ================= */

nextBtn.onclick = () => nextPage && fetchData(nextPage);
prevBtn.onclick = () => prevPage && fetchData(prevPage);

function updateButtons() {
    nextBtn.disabled = !nextPage;
    prevBtn.disabled = !prevPage;
}

/* ================= TABLE ================= */

function renderTable(data) {
    const table = document.getElementById("equipment-table");
    table.innerHTML = "";

    if (data.length === 0) {
        table.innerHTML = "<tr><td colspan='6'>No equipment found</td></tr>";
        return;
    }

    data.forEach(item => {
        table.innerHTML += `
            <tr onclick="openModal(${item.id})">
                <td>${item.name}</td>
                <td>${item.type}</td>
                <td>${item.material}</td>
                <td>${item.pressure}</td>
                <td>${item.temperature}</td>
            </tr>
        `;
    });
}

/* ================= CHARTS ================= */

function drawCharts(data) {
    const labels = data.map(e => e.name);
    const pressures = data.map(e => e.pressure);
    const temps = data.map(e => e.temperature);

    if (pressureChart) pressureChart.destroy();
    if (temperatureChart) temperatureChart.destroy();

    pressureChart = new Chart(document.getElementById("pressureChart"), {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Pressure",
                data: pressures
            }]
        }
    });

    temperatureChart = new Chart(document.getElementById("temperatureChart"), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Temperature",
                data: temps
            }]
        }
    });
}

/* ================= MODAL ================= */

function openModal(id) {
    const item = equipmentData.find(e => e.id === id);
    if (!item) return;

    document.getElementById("modal").style.display = "block";
    document.getElementById("modal-title").textContent = item.name;
    document.getElementById("modal-type").textContent = item.type;
    document.getElementById("modal-material").textContent = item.material;
    document.getElementById("modal-flowrate").textContent = item.flowrate;
    document.getElementById("modal-pressure").textContent = item.pressure;
    document.getElementById("modal-temperature").textContent = item.temperature;
    document.getElementById("modal-description").textContent = item.description || "—";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

/* ================= CSV EXPORT ================= */

function exportCSV() {
    let params = [];

    if (searchInput.value)
        params.push(`search=${encodeURIComponent(searchInput.value)}`);

    if (pressureInput.value)
        params.push(`pressure__gte=${pressureInput.value}`);

    if (temperatureInput.value)
        params.push(`temperature__gte=${temperatureInput.value}`);

    if (materialInput.value)
        params.push(`material=${encodeURIComponent(materialInput.value)}`);

    const url = `http://127.0.0.1:8000/api/equipment/export/csv/?${params.join("&")}`;
    window.location.href = url;
}

/* ================= UPLOAD ================= */

function uploadCSV() {
    const file = document.getElementById('csvFile').files[0];
    if (!file) { alert('Select a CSV file first'); return; }

    const fd = new FormData();
    fd.append('file', file);

    fetch('http://127.0.0.1:8000/api/upload/', {
        method: 'POST',
        body: fd
    })
    .then(res => res.json())
    .then(data => {
        alert(`Uploaded dataset, created: ${data.created}`);
        fetchData(API_URL);
    })
    .catch(err => {
        console.error(err);
        alert('Upload failed');
    });
}

/* ================= HELPERS ================= */

function populateMaterials(data) {
    const set = new Set();
    data.forEach(e => { if (e.material) set.add(e.material); });
    materialInput.innerHTML = '<option value="">All Materials</option>';
    set.forEach(m => { materialInput.innerHTML += `<option value="${m}">${m}</option>`; });
}
