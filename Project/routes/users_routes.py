# routes/users_routes.py
from flask import Blueprint, request, jsonify, g
from config import get_connection
from utils import row_to_dict, rows_to_list, is_admin

users_bp = Blueprint("users_bp", __name__)

@users_bp.route('', methods=['GET'])
def get_all_users():
    """
    GET /users
    Admin/Owner: dapat semua baris (tidak ada kolom email di DB saat ini)
    Non-admin: tetap bisa mendapat list, tapi sensitif handling bisa ditambahkan jika perlu
    """
    conn = get_connection(); cur = conn.cursor()
    # ambil kolom yang benar-benar ada di DB
    cur.execute("SELECT id_user, username, role, id_karyawan, id_pelanggan, tanggal_dibuat FROM Users")
    rows = cur.fetchall()
    data = rows_to_list(cur, rows)
    cur.close(); conn.close()

    # Kalau ingin sembunyikan sesuatu untuk non-admin, lakukan di sini.
    # Saat ini tidak ada kolom 'email', jadi tidak perlu modifikasi.
    return jsonify(data), 200

@users_bp.route('/get', methods=['GET'])
def get_user():
    """
    GET /users/get?id_user=...
    Jika non-admin dan bukan dirinya sendiri, beberapa kolom sensitif dapat disembunyikan.
    """
    id_user = request.args.get("id_user", type=int)
    if id_user is None:
        return jsonify({"error": "id_user wajib"}), 400

    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        "SELECT id_user, username, role, id_karyawan, id_pelanggan, tanggal_dibuat FROM Users WHERE id_user=?",
        (id_user,)
    )
    row = cur.fetchone()
    data = row_to_dict(cur, row) if row else None
    cur.close(); conn.close()

    if not data:
        return jsonify({"error":"User tidak ditemukan"}), 404

    # Jika bukan admin/owner, dan bukan dirinya sendiri, kamu bisa menyembunyikan kolom tertentu.
    if not is_admin():
        jwt_id = getattr(g, "jwt_identity", None)
        # jika jwt_identity tersedia dan berbeda dari id_user, hapus fields sensitif (contoh password_hash)
        if jwt_id is None or str(jwt_id) != str(id_user):
            data.pop("password_hash", None)

    # Jangan kembalikan password_hash ke client kecuali diperlukan (ambang keamanan)
    data.pop("password_hash", None)
    return jsonify(data), 200

@users_bp.route('', methods=['POST'])
def add_user():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")  # NOTE: harus di-hash sebelum simpan
    role = data.get("role")
    id_karyawan = data.get("id_karyawan")
    id_pelanggan = data.get("id_pelanggan")

    if not username or not password or not role:
        return jsonify({"error":"username, password, role wajib diisi"}), 400

    # TODO: gunakan generate_password_hash dari werkzeug untuk hashing password sebelum menyimpan
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Users (username, password_hash, role, id_karyawan, id_pelanggan)
        VALUES (?, ?, ?, ?, ?)
    """, (username, password, role, id_karyawan, id_pelanggan))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"message":"User berhasil ditambahkan"}), 201

@users_bp.route('', methods=['PUT'])
def update_user():
    data = request.get_json() or {}
    id_user = data.get("id_user")
    if not id_user:
        return jsonify({"error":"id_user wajib"}), 400

    # fields to update
    username = data.get("username")
    password = data.get("password")  # idealnya sudah hash
    role = data.get("role")
    id_karyawan = data.get("id_karyawan")
    id_pelanggan = data.get("id_pelanggan")

    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Users SET username=?, password_hash=?, role=?, id_karyawan=?, id_pelanggan=? WHERE id_user=?
    """, (username, password, role, id_karyawan, id_pelanggan, id_user))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"User berhasil diperbarui"}), 200

@users_bp.route('', methods=['PATCH'])
def patch_user():
    data = request.get_json() or {}
    id_user = data.get("id_user")
    if not id_user:
        return jsonify({"error":"id_user wajib"}), 400

    fields = []; vals = []
    for col in ["username","password_hash","role","id_karyawan","id_pelanggan"]:
        # support "password" as input mapping to password_hash
        key = col
        if col == "password_hash" and "password" in data:
            val = data.get("password")
        else:
            val = data.get(col)
        if val is not None:
            fields.append(f"{col}=?"); vals.append(val)

    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400

    vals.append(id_user)
    query = f"UPDATE Users SET {', '.join(fields)} WHERE id_user=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"User berhasil diperbarui"}), 200

@users_bp.route('', methods=['DELETE'])
def delete_user():
    data = request.get_json() or {}
    id_user = data.get("id_user")
    if not id_user:
        return jsonify({"error":"id_user wajib"}), 400
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE id_user=?", (id_user,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"User berhasil dihapus"}), 200
