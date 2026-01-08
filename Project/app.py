# app.py
from flask import Flask, jsonify, g, request, session
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, get_jwt_identity
from config import get_connection
import os
from flask_cors import CORS
from rate_limit import limiter
import datetime as dt

# import limiter instance dari extensions (hindari circular import)
from extensions import limiter

# =============================
# APP SETUP
# =============================
app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-session-secret')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)

# Dev CORS: izinkan IPv4/localhost/IPv6 dev origins — hanya untuk development
CORS(app,
     supports_credentials=True,
     resources={r"/*": {"origins": [
         "http://127.0.0.1:8000",
         "http://localhost:8000",
         "http://[::1]:8000",
         "http://[::]:8000"
     ]}})

jwt = JWTManager(app)

# inisialisasi limiter dengan app (late binding)
limiter.init_app(app)


# =============================
# CUSTOM API ERROR
# =============================
class ApiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

# =============================
# DEBUG / UTILITY ROUTES
# =============================
@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    origin = request.headers.get("Origin")
    return jsonify({"ok": True, "origin": origin, "path": request.path}), 200

@app.route("/__routes", methods=["GET"])
def _routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "rule": str(rule),
            "endpoint": rule.endpoint,
            "methods": sorted([m for m in rule.methods if m not in ("HEAD","OPTIONS")])
        })
    return jsonify(routes)

# =============================
# GLOBAL AUTH MIDDLEWARE
# =============================
@app.before_request
def global_auth_middleware():
    path = request.path
    if path.endswith('/') and path != '/':
        path = path[:-1]
    method = request.method.upper()

    # allow OPTIONS through (CORS preflight)
    if method == "OPTIONS":
        return

    public_paths = {"/login", "/register", "/logout", "/ping", "/__routes", "/"}
    public_prefixes = ["/static", "/docs", "/openapi.json"]
    if path in public_paths or any(path.startswith(p) for p in public_prefixes):
        return
    if path.startswith("/produk") and method == "GET":
        return

    # reset context
    g.jwt_claims = {}
    g.jwt_role = None
    g.jwt_identity = None
    g.is_admin = False

    # try JWT (optional)
    token_used = False
    try:
        try:
            verify_jwt_in_request(optional=True)
        except TypeError:
            try:
                verify_jwt_in_request()
            except Exception:
                pass
        try:
            claims = get_jwt() or {}
            if claims:
                g.jwt_claims = claims
                g.jwt_role = claims.get("role")
                g.jwt_identity = get_jwt_identity()
                g.is_admin = g.jwt_role in ("Admin", "Owner")
                token_used = True
        except Exception:
            pass
    except Exception:
        pass

    # fallback to session
    if not token_used:
        user_sess = session.get("user")
        if user_sess:
            g.jwt_claims = {
                "role": user_sess.get("role"),
                "id_karyawan": user_sess.get("id_karyawan"),
                "id_pelanggan": user_sess.get("id_pelanggan")
            }
            g.jwt_role = user_sess.get("role")
            g.jwt_identity = user_sess.get("id")
            g.is_admin = g.jwt_role in ("Admin", "Owner")

    # Authorization
    if g.jwt_role in ("Admin", "Owner"):
        return

    admin_only = [
        "/produk", "/supplier", "/karyawan", "/users",
        "/pembelian", "/detail_pembelian", "/detail"
    ]
    if method != "GET":
        for prefix in admin_only:
            if path.startswith(prefix):
                raise ApiError("Akses ditolak: hanya Admin/Owner yang boleh melakukan operasi ini", 403)

    if g.jwt_role == "Pelanggan":
        if path.startswith("/pelanggan") and method == "GET":
            id_q = request.args.get("id_pelanggan", type=int)
            id_token = g.jwt_claims.get("id_pelanggan")
            if id_q is None or id_token is None or int(id_q) != int(id_token):
                raise ApiError("Akses ditolak: pelanggan hanya dapat melihat data diri sendiri", 403)
            return

        if path.startswith("/transaksi") and method == "GET":
            id_transaksi = request.args.get("id_transaksi", type=int)
            if id_transaksi is None:
                raise ApiError("id_transaksi wajib untuk pelanggan", 400)

            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT id_pelanggan FROM Transaksi WHERE id_transaksi=?", (id_transaksi,))
            row = cur.fetchone()
            cur.close(); conn.close()

            if not row:
                raise ApiError("Transaksi tidak ditemukan", 404)
            db_id_pelanggan = row[0]
            id_token = g.jwt_claims.get("id_pelanggan")
            if id_token is None or int(db_id_pelanggan) != int(id_token):
                raise ApiError("Akses ditolak: bukan pemilik transaksi", 403)
            return

        raise ApiError("Akses ditolak untuk role Pelanggan pada resource ini", 403)

    if g.jwt_role == "Kasir":
        if path.startswith("/transaksi") and method == "POST":
            return
        if path.startswith("/pelanggan") and method == "GET":
            return
        if path.startswith("/transaksi") and method == "GET":
            return
        raise ApiError("Akses ditolak untuk role Kasir pada resource ini", 403)

    if not g.jwt_role:
        raise ApiError("Authentication diperlukan untuk operasi ini", 401)

    raise ApiError("Akses ditolak", 403)

# =============================
# ERROR HANDLERS
# =============================
@app.errorhandler(ApiError)
def handle_api_error(e): return jsonify({"error": e.message}), e.status_code

@app.errorhandler(400)
def bad_request(e): return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(401)
def unauthorized(e): return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(e): return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(e): return jsonify({"error": "Not Found"}), 404

# rate limit response
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Terlalu banyak permintaan (Rate Limit Exceeded). Coba lagi nanti."}), 429

@app.errorhandler(Exception)
def internal_error(e): return jsonify({"error": str(e)}), 500

# =============================
# REGISTER BLUEPRINTS (import di sini supaya limiter sudah inisialisasi)
# =============================
from routes.auth_routes import auth_bp
from routes.produk_routes import produk_bp
from routes.pelanggan_routes import pelanggan_bp
from routes.supplier_routes import supplier_bp
from routes.karyawan_routes import karyawan_bp
from routes.users_routes import users_bp
from routes.transaksi_routes import transaksi_bp
from routes.detail_routes import detail_bp
from routes.pembelian_routes import pembelian_bp
from routes.detail_pembelian_routes import detail_pembelian_bp
from routes.generic_routes import generic_bp

app.register_blueprint(auth_bp)
app.register_blueprint(produk_bp, url_prefix='/produk')
app.register_blueprint(pelanggan_bp, url_prefix='/pelanggan')
app.register_blueprint(supplier_bp, url_prefix='/supplier')
app.register_blueprint(karyawan_bp, url_prefix='/karyawan')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(transaksi_bp, url_prefix='/transaksi')
app.register_blueprint(detail_bp, url_prefix='/detail')
app.register_blueprint(pembelian_bp, url_prefix='/pembelian')
app.register_blueprint(detail_pembelian_bp, url_prefix='/detail_pembelian')
app.register_blueprint(generic_bp, url_prefix='')

# =============================
# RUN APP
# =============================
if __name__ == "__main__":
    app.run(debug=True)
