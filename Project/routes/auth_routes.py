# routes/auth_routes.py
from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt, get_jwt_identity
from config import get_connection
import datetime as dt

from extensions import limiter

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi"}), 400

    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id_user, username, password_hash, role, id_karyawan, id_pelanggan
        FROM Users WHERE username=?
    """, (username,))
    user = cur.fetchone()
    cur.close(); conn.close()

    if not user:
        return jsonify({"error": "Username atau password salah"}), 401

    try:
        pw = user.password_hash
        uid = user.id_user
        role = user.role
        id_karyawan = user.id_karyawan
        id_pelanggan = user.id_pelanggan
    except Exception:
        uid = user[0]; pw = user[2]; role = user[3]; id_karyawan = user[4]; id_pelanggan = user[5]

    # NOTE: jika pakai hashing, ganti pengecekan ini
    if pw != password:
        return jsonify({"error": "Username atau password salah"}), 401

    token = create_access_token(identity=str(uid),
                                additional_claims={"role": role, "id_karyawan": id_karyawan, "id_pelanggan": id_pelanggan},
                                expires_delta=dt.timedelta(hours=8))

    session['user'] = {
        "id": str(uid),
        "role": role,
        "id_karyawan": id_karyawan,
        "id_pelanggan": id_pelanggan
    }
    session.permanent = True
    return jsonify({"access_token": token, "role": role}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logout berhasil"}), 200


@auth_bp.route('/whoami', methods=['GET'])
def whoami():
    user_sess = session.get("user")
    if user_sess:
        return jsonify({
            "identity": user_sess.get("id"),
            "claims": {
                "role": user_sess.get("role"),
                "id_karyawan": user_sess.get("id_karyawan"),
                "id_pelanggan": user_sess.get("id_pelanggan")
            }
        }), 200

    try:
        verify_jwt_in_request()
        claims = get_jwt() or {}
        identity = get_jwt_identity()
        return jsonify({"identity": identity, "claims": claims}), 200
    except Exception:
        return jsonify({"error": "Not authenticated"}), 401
