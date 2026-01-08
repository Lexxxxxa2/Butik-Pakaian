# app.py
from flask import Flask, jsonify, g, request, session
from flask_jwt_extended import (
    JWTManager, verify_jwt_in_request,
    get_jwt, get_jwt_identity
)
from config import get_connection
from flask_cors import CORS
from extensions import limiter
import os

# =============================
# SWAGGER
# =============================
from swagger import api

# =============================
# APP SETUP
# =============================
app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-session-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)

# CORS (frontend kamu)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://[::1]:8000",
        "http://[::]:8000"
    ]}}
)

jwt = JWTManager(app)
limiter.init_app(app)

# init swagger
api.init_app(app)

# =============================
# CUSTOM API ERROR
# =============================
class ApiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

# =============================
# DEBUG ROUTES
# =============================
@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    return jsonify({"ok": True}), 200

@app.route("/__routes", methods=["GET"])
def routes():
    return jsonify([
        {
            "rule": str(r),
            "methods": list(r.methods)
        } for r in app.url_map.iter_rules()
    ])

# =============================
# GLOBAL AUTH MIDDLEWARE (TETAP)
# =============================
@app.before_request
def global_auth_middleware():
    path = request.path.rstrip("/") or "/"
    method = request.method.upper()

    # OPTIONS (CORS)
    if method == "OPTIONS":
        return

    # public
    public_paths = {"/", "/login", "/logout", "/ping", "/__routes"}
    public_prefixes = ["/docs", "/openapi.json"]
    if path in public_paths or any(path.startswith(p) for p in public_prefixes):
        return

    # GET produk boleh publik
    if path.startswith("/produk") and method == "GET":
        return

    # reset context
    g.jwt_claims = {}
    g.jwt_role = None
    g.jwt_identity = None
    g.is_admin = False

    # JWT (optional)
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt() or {}
        if claims:
            g.jwt_claims = claims
            g.jwt_role = claims.get("role")
            g.jwt_identity = get_jwt_identity()
            g.is_admin = g.jwt_role in ("Admin", "Owner")
    except Exception:
        pass

    # session fallback
    if not g.jwt_role:
        user = session.get("user")
        if user:
            g.jwt_role = user.get("role")
            g.jwt_identity = user.get("id")
            g.is_admin = g.jwt_role in ("Admin", "Owner")

    # admin full access
    if g.is_admin:
        return

    admin_only = [
        "/produk", "/supplier", "/karyawan",
        "/users", "/pembelian", "/detail", "/detail_pembelian"
    ]

    if method != "GET":
        for p in admin_only:
            if path.startswith(p):
                raise ApiError("Hanya Admin/Owner", 403)

    if not g.jwt_role:
        raise ApiError("Authentication diperlukan", 401)

# =============================
# ERROR HANDLERS
# =============================
@app.errorhandler(ApiError)
def api_error(e):
    return jsonify({"error": e.message}), e.status_code

@app.errorhandler(404)
def not_found(e): return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e): return jsonify({"error": "Internal Server Error"}), 500

# =============================
# REGISTER SWAGGER ROUTES (SEMUA)
# =============================
from routes.auth_routes import auth_ns
from routes.produk_routes import produk_ns
from routes.pelanggan_routes import pelanggan_ns
from routes.supplier_routes import supplier_ns
from routes.karyawan_routes import karyawan_ns
from routes.users_routes import users_ns
from routes.transaksi_routes import transaksi_ns
from routes.detail_routes import detail_ns
from routes.pembelian_routes import pembelian_ns
from routes.detail_pembelian_routes import detail_pembelian_ns

api.add_namespace(auth_ns, path="/")
api.add_namespace(produk_ns, path="/produk")
api.add_namespace(pelanggan_ns, path="/pelanggan")
api.add_namespace(supplier_ns, path="/supplier")
api.add_namespace(karyawan_ns, path="/karyawan")
api.add_namespace(users_ns, path="/users")
api.add_namespace(transaksi_ns, path="/transaksi")
api.add_namespace(detail_ns, path="/detail")
api.add_namespace(pembelian_ns, path="/pembelian")
api.add_namespace(detail_pembelian_ns, path="/detail_pembelian")

# =============================
# RUN
# =============================
if __name__ == "__main__":
    app.run(debug=True)
