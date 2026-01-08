from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

karyawan_bp = Blueprint("karyawan_bp", __name__)

@karyawan_bp.route('', methods=['GET'])
def get_all_karyawan():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_karyawan, nama, jabatan, no_hp, alamat FROM Karyawan")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@karyawan_bp.route('/get', methods=['GET'])
def get_karyawan():
    id_karyawan = request.args.get("id_karyawan", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_karyawan, nama, jabatan, no_hp, alamat FROM Karyawan WHERE id_karyawan=?", (id_karyawan,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Karyawan tidak ditemukan"}), 404
    return jsonify(data), 200

@karyawan_bp.route('', methods=['POST'])
def add_karyawan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Karyawan (nama, jabatan, no_hp, alamat) VALUES (?, ?, ?, ?)",
                (data.get("nama"), data.get("jabatan"), data.get("no_hp"), data.get("alamat")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Karyawan berhasil ditambahkan"}), 201

@karyawan_bp.route('', methods=['PUT'])
def update_karyawan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Karyawan SET nama=?, jabatan=?, no_hp=?, alamat=? WHERE id_karyawan=?
    """, (data.get("nama"), data.get("jabatan"), data.get("no_hp"), data.get("alamat"), data.get("id_karyawan")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Karyawan berhasil diperbarui"}), 200

@karyawan_bp.route('', methods=['PATCH'])
def patch_karyawan():
    data = request.get_json() or {}
    id_karyawan = data.get("id_karyawan")
    fields = []; vals = []
    for col in ["nama","jabatan","no_hp","alamat"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_karyawan)
    query = f"UPDATE Karyawan SET {', '.join(fields)} WHERE id_karyawan=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Karyawan berhasil diperbarui"}), 200

@karyawan_bp.route('', methods=['DELETE'])
def delete_karyawan():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Karyawan WHERE id_karyawan=?", (data.get("id_karyawan"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Karyawan berhasil dihapus"}), 200
