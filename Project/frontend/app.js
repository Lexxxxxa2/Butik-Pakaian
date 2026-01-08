// ===============================
// CONFIG
// ===============================
const API_BASE = "http://127.0.0.1:5000";

// ===============================
// DEBUG HELPER
// ===============================
function dbg(msg) {
    console.log(msg);
}

// ===============================
// NOTICE HELPER
// ===============================
function showNotice(msg, type = "info") {
    alert(msg); // sederhana dulu
}

// ===============================
// FRONTEND LOGIN LIMITER
// ===============================
let loginCooldown = false;

function startLoginCooldown(btn, delay = 5000) {
    loginCooldown = true;
    btn.disabled = true;

    const originalText = btn.innerText;
    let remain = Math.ceil(delay / 1000);

    btn.innerText = `Tunggu ${remain}s`;

    const timer = setInterval(() => {
        remain--;
        btn.innerText = `Tunggu ${remain}s`;
    }, 1000);

    setTimeout(() => {
        clearInterval(timer);
        btn.disabled = false;
        btn.innerText = originalText;
        loginCooldown = false;
    }, delay);
}

// ===============================
// API FETCH (WITH SESSION)
// ===============================
async function apiFetch(path, options = {}) {
    const res = await fetch(API_BASE + path, {
        method: options.method || "GET",
        credentials: "include", // PENTING untuk session
        headers: {
            "Content-Type": "application/json"
        },
        body: options.body ? JSON.stringify(options.body) : undefined
    });

    let data = {};
    try {
        data = await res.json();
    } catch (_) {}

    if (!res.ok) {
        const err = new Error("API Error");
        err.status = res.status;
        err.data = data;
        throw err;
    }

    return data;
}

// ===============================
// LOGIN FUNCTION
// ===============================
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showNotice("Username dan password wajib diisi", "error");
        return;
    }

    dbg("== FETCH /login ===");

    const data = await apiFetch("/login", {
        method: "POST",
        body: { username, password }
    });

    return data;
}

// ===============================
// LOGIN BUTTON HANDLER
// ===============================
document.getElementById("btnLogin").addEventListener("click", async () => {
    const btn = document.getElementById("btnLogin");

    // Blok spam klik
    if (loginCooldown) {
        dbg("Login ditolak: masih cooldown");
        return;
    }

    // Mulai cooldown 5 detik
    startLoginCooldown(btn, 5000);

    try {
        const data = await login();

        if (data.access_token) {
            dbg("Login sukses");
            showNotice("Login berhasil!", "ok");

            // redirect ke dashboard
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 800);
        } else {
            showNotice("Login berhasil tapi token kosong", "error");
        }

    } catch (err) {
        if (err.status === 429) {
            showNotice("Terlalu banyak percobaan login, tunggu sebentar", "error");
        } else if (err.data?.error) {
            showNotice(err.data.error, "error");
        } else {
            showNotice("Gagal login", "error");
        }

        dbg("ERROR LOGIN:");
        dbg(err);
    }
});
