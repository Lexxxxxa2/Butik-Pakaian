# routes/produk_routes.py
from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list, is_admin

produk_bp = Blueprint("produk_bp", __name__)

@produk_bp.route('', methods=['GET'])
def get_all_produk():
    conn = get_connection(); cur = conn.cursor()
    # gunakan kolom yang pasti ada di DB: sesuaikan bila DB-mu pakai nama lain
    cur.execute("SELECT id_produk, nama_produk, kategori, ukuran, warna, harga, stok FROM Produk")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    if not is_admin():
        # tidak ada 'detail' lagi, jadi tidak perlu sembunyikan
        pass
    return jsonify(data), 200

@produk_bp.route('/get', methods=['GET'])
def get_produk():
    id_produk = request.args.get("id_produk", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_produk, nama_produk, kategori, ukuran, warna, harga, stok FROM Produk WHERE id_produk=?", (id_produk,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error": "Produk tidak ditemukan"}), 404
    return jsonify(data), 200

@produk_bp.route('', methods=['POST'])
def add_produk():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Produk (nama_produk, kategori, ukuran, warna, harga, stok)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.get("nama_produk"), data.get("kategori"), data.get("ukuran"),
          data.get("warna"), data.get("harga"), data.get("stok")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Produk berhasil ditambahkan"}), 201

@produk_bp.route('', methods=['PUT'])
def update_produk():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Produk SET nama_produk=?, kategori=?, ukuran=?, warna=?, harga=?, stok=?
        WHERE id_produk=?
    """, (data.get("nama_produk"), data.get("kategori"), data.get("ukuran"),
          data.get("warna"), data.get("harga"), data.get("stok"),
          data.get("id_produk")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Produk berhasil diperbarui"}), 200

@produk_bp.route('', methods=['PATCH'])
def patch_produk():
    data = request.get_json() or {}
    id_produk = data.get("id_produk")
    fields = []; vals = []
    for col in ["nama_produk","kategori","ukuran","warna","harga","stok"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_produk)
    query = f"UPDATE Produk SET {', '.join(fields)} WHERE id_produk=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Produk berhasil diperbarui"}), 200

@produk_bp.route('', methods=['DELETE'])
def delete_produk():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Produk WHERE id_produk=?", (data.get("id_produk"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Produk berhasil dihapus"}), 200
