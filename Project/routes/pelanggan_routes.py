from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

pelanggan_bp = Blueprint("pelanggan_bp", __name__)

@pelanggan_bp.route('', methods=['GET'])
def get_all_pelanggan():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_pelanggan, nama_pelanggan, no_hp, alamat, email FROM Pelanggan")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@pelanggan_bp.route('/get', methods=['GET'])
def get_pelanggan():
    id_pelanggan = request.args.get("id_pelanggan", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_pelanggan, nama_pelanggan, no_hp, alamat, email FROM Pelanggan WHERE id_pelanggan=?", (id_pelanggan,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Pelanggan tidak ditemukan"}), 404
    return jsonify(data), 200

@pelanggan_bp.route('', methods=['POST'])
def add_pelanggan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Pelanggan (nama_pelanggan, no_hp, alamat, email) VALUES (?, ?, ?, ?)",
                (data.get("nama_pelanggan"), data.get("no_hp"), data.get("alamat"), data.get("email")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pelanggan berhasil ditambahkan"}), 201

@pelanggan_bp.route('', methods=['PUT'])
def update_pelanggan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Pelanggan SET nama_pelanggan=?, no_hp=?, alamat=?, email=? WHERE id_pelanggan=?
    """, (data.get("nama_pelanggan"), data.get("no_hp"), data.get("alamat"), data.get("email"), data.get("id_pelanggan")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pelanggan berhasil diperbarui"}), 200

@pelanggan_bp.route('', methods=['PATCH'])
def patch_pelanggan():
    data = request.get_json() or {}
    id_pelanggan = data.get("id_pelanggan")
    fields = []; vals = []
    for col in ["nama_pelanggan","no_hp","alamat","email"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_pelanggan)
    query = f"UPDATE Pelanggan SET {', '.join(fields)} WHERE id_pelanggan=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pelanggan berhasil diperbarui"}), 200

@pelanggan_bp.route('', methods=['DELETE'])
def delete_pelanggan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Pelanggan WHERE id_pelanggan=?", (data.get("id_pelanggan"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pelanggan berhasil dihapus"}), 200
