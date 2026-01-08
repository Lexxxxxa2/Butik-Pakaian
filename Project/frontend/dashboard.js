// ------ CONFIG ------
const API = "http://127.0.0.1:5000";

const debugEl = document.getElementById("debug");
const tableSelect = document.getElementById("tableSelect");
const extraParam = document.getElementById("extraParam");

const tableHead = document.getElementById("tableHead");
const tableBody = document.getElementById("tableBody");
const formCard = document.getElementById("formCard");
const formFields = document.getElementById("formFields");
const whoamiBadge = document.getElementById("whoamiBadge");

// Tabel yang ada di backend
const TABLES = [
  "produk", "pelanggan", "supplier", "karyawan", "users", "pembelian",
  "detail_pembelian", "transaksi", "detail"
];
// Map primary keys
const PK = {
  produk: "id_produk", pelanggan: "id_pelanggan", supplier: "id_supplier",
  karyawan: "id_karyawan", users: "id_user", pembelian: "id_pembelian",
  detail_pembelian: "id_detail_pembelian", transaksi: "id_transaksi", detail: "id_detail"
};

// ------ Helpers ------
function log(...args) {
  console.log(...args);
  if (debugEl) {
    debugEl.textContent += "\n" + args.join(" ");
    debugEl.scrollTop = debugEl.scrollHeight;
  }
}

function escape(s) {
  if (s == null) return "";
  return String(s)
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

// ------ INIT & DROPDOWN ------
window.onload = () => {
  tableSelect.innerHTML = TABLES.map(t => `<option value="${t}">${t}</option>`).join("");
  onTableChanged();
  whoami();
};

tableSelect.onchange = onTableChanged;

function onTableChanged() {
  const tbl = tableSelect.value;
  if (tbl === "detail_pembelian") {
    extraParam.style.display = "inline-block";
    extraParam.placeholder = "id_pembelian (wajib)";
  } else if (tbl === "detail") {
    extraParam.style.display = "inline-block";
    extraParam.placeholder = "id_transaksi (opsional)";
  } else {
    extraParam.style.display = "none";
    extraParam.value = "";
  }
}

// ------ LOAD TABLE (Fungsi Kritis) ------
async function loadTable() {
  const table = tableSelect.value;
  let url = `${API}/${table}`;
  
  tableHead.innerHTML = "";
  tableBody.innerHTML = `<tr><td colspan="10">Loading...</td></tr>`;
  formCard.style.display = "none";
  
  const param = extraParam.value.trim();
  let queryParam = "";

  if (table === "detail_pembelian") {
    if (!param) {
      tableBody.innerHTML = `<tr><td colspan="10">ID Pembelian wajib untuk Detail Pembelian</td></tr>`;
      return;
    }
    queryParam = `id_pembelian=${param}`;
  } else if (table === "detail" && param !== "") {
    queryParam = `id_transaksi=${param}`;
  }

  if (queryParam) {
     url += `?${queryParam}`;
  }

  log("GET", url);

  try {
    const token = localStorage.getItem('access_token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(url, { 
        credentials: "include",
        headers: headers
    });
    
    const text = await res.text();
    let json;
    try { json = JSON.parse(text); } catch { 
        json = { error: "Response non-JSON", raw: text }; 
    }
    
    if (!res.ok) {
        let errorMessage = json.error || `HTTP Status ${res.status}`;
        if (res.status === 401 || res.status === 403) {
             errorMessage = `Akses Ditolak (${res.status}). Silakan Login/Cek Role.`;
        }
        alert("Gagal memuat data: " + errorMessage);
        tableBody.innerHTML = `<tr><td colspan="10">${errorMessage}</td></tr>`;
        return;
    }

    const data = Array.isArray(json) ? json : [json];

    if (!data.length || (data.length === 1 && Object.keys(data[0]).length === 0)) {
      tableHead.innerHTML = "";
      tableBody.innerHTML = `<tr><td colspan="10">Tidak ada data</td></tr>`;
      return;
    }

    buildTable(data);
    buildForm(data[0]);
  } catch (e) {
      log("FETCH ERROR (Network):", e.message);
      alert("Terjadi kesalahan jaringan/fetch. Pastikan server Flask berjalan.");
      tableBody.innerHTML = `<tr><td colspan="10">Error: Koneksi Gagal atau Server Offline</td></tr>`;
  }
}

// ------ BUILD TABLE & FORM ------
function buildTable(rows) {
  const cols = Object.keys(rows[0]);
  tableHead.innerHTML = `<tr>${cols.map(c => `<th>${c}</th>`).join("")}<th>Aksi</th></tr>`;
  tableBody.innerHTML = rows
    .map(row => {
      const cells = cols.map(c => `<td>${escape(row[c])}</td>`).join("");
      const idVal = row[PK[tableSelect.value]];
      return `
      <tr>
        ${cells}
        <td>
          <button class="btn btn-sm btn-warning" onclick='edit(${JSON.stringify(row)})'>Edit</button>
          <button class="btn btn-sm btn-danger" onclick="hapus('${idVal}')">Hapus</button>
        </td>
      </tr>`;
    })
    .join("");
}

function buildForm(row) {
  formCard.style.display = "block";
  formFields.innerHTML = "";
  Object.keys(row).forEach(col => {
    const inputType = col.toLowerCase().includes('password') ? 'password' : 'text';
    formFields.innerHTML += `
      <div class="col-md-4 mb-2">
        <label>${col}</label>
        <input id="f_${col}" class="form-control" type="${inputType}" value="${escape(row[col] || '')}">
      </div>`;
  });
}

function edit(row) {
  for (const k in row) {
    const el = document.getElementById(`f_${k}`);
    if (el) el.value = row[k];
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function collect() {
  const inputs = formFields.querySelectorAll("input");
  const obj = {};
  inputs.forEach(i => {
    const val = i.value.trim();
    if (val !== "") {
        obj[i.id.replace("f_", "")] = val;
    }
  });
  return obj;
}


// ------ CRUD Functions ------
async function apiCall(method, data) {
  const tbl = tableSelect.value;
  const url = `${API}/${tbl}`;
  const token = localStorage.getItem('access_token');
  const headers = { "Content-Type": "application/json" };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  log(`${method}`, url, data);
  
  const res = await fetch(url, {
    method: method,
    headers: headers,
    credentials: "include",
    body: JSON.stringify(data)
  });

  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = { error: `Response non-JSON for ${method}`, raw: text }; }
  
  if (!res.ok) {
    let errorMessage = json.error || `HTTP Status ${res.status}`;
    if (res.status === 401 || res.status === 403) {
         errorMessage = `Akses Ditolak (${res.status}). Silakan Login/Cek Role.`;
    }
    alert(`Gagal ${method}: ` + errorMessage);
    log(`ERROR ${method}:`, json);
    throw new Error(json.error || `HTTP Status ${res.status}`);
  }

  return json;
}

async function createItem() {
  try {
    const data = collect();
    const result = await apiCall("POST", data);
    alert("Berhasil Tambah. ID Baru: " + (result.inserted && result.inserted[0]?.[PK[tableSelect.value]]) || "Tidak diketahui");
    loadTable();
  } catch {}
}

async function updateItem() {
  try {
    const data = collect();
    if (!data[PK[tableSelect.value]]) return alert("ID wajib diisi untuk PUT Update");
    await apiCall("PUT", data);
    alert("Update (PUT) sukses");
    loadTable();
  } catch {}
}

async function patchItem() {
  try {
    const data = collect();
    if (!data[PK[tableSelect.value]]) return alert("ID wajib diisi untuk PATCH Update");
    await apiCall("PATCH", data);
    alert("Update (PATCH) sukses");
    loadTable();
  } catch {}
}

async function hapus(id) {
  if (!confirm(`Yakin ingin menghapus item dengan ID ${id}?`)) return;
  try {
    const tbl = tableSelect.value;
    await apiCall("DELETE", { [PK[tbl]]: id });
    alert("Hapus berhasil");
    loadTable();
  } catch {}
}

// ------ WHOAMI & LOGOUT ------
async function whoami() {
  try {
    const r = await fetch(`${API}/whoami`, { credentials: "include" });
    const j = await r.json();

    if (r.ok && j.claims) {
      whoamiBadge.textContent = j.claims.role;
    } else {
      whoamiBadge.textContent = "Guest";
    }
  } catch {
     whoamiBadge.textContent = "Guest";
  }
}

async function logout() {
  await fetch(`${API}/logout`, { method: "POST", credentials: "include" });
  localStorage.removeItem('access_token');
  whoamiBadge.textContent = "Guest";
  window.location.href = "index.html"; 
}

// Pasang fungsi ke window
window.loadTable = loadTable;
window.logout = logout;
window.edit = edit;
window.hapus = hapus;
window.createItem = createItem;
window.updateItem = updateItem;
window.patchItem = patchItem;

log("Dashboard script loaded");