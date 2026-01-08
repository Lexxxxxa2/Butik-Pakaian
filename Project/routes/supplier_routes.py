from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

supplier_bp = Blueprint("supplier_bp", __name__)

@supplier_bp.route('', methods=['GET'])
def get_all_supplier():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_supplier, nama_supplier, no_hp, alamat, email FROM Supplier")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@supplier_bp.route('/get', methods=['GET'])
def get_supplier():
    id_supplier = request.args.get("id_supplier", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_supplier, nama_supplier, no_hp, alamat, email FROM Supplier WHERE id_supplier=?", (id_supplier,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Supplier tidak ditemukan"}), 404
    return jsonify(data), 200

@supplier_bp.route('', methods=['POST'])
def add_supplier():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Supplier (nama_supplier, no_hp, alamat, email) VALUES (?, ?, ?, ?)",
                (data.get("nama_supplier"), data.get("no_hp"), data.get("alamat"), data.get("email")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Supplier berhasil ditambahkan"}), 201

@supplier_bp.route('', methods=['PUT'])
def update_supplier():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Supplier SET nama_supplier=?, no_hp=?, alamat=?, email=? WHERE id_supplier=?
    """, (data.get("nama_supplier"), data.get("no_hp"), data.get("alamat"), data.get("email"), data.get("id_supplier")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Supplier berhasil diperbarui"}), 200

@supplier_bp.route('', methods=['PATCH'])
def patch_supplier():
    data = request.get_json() or {}
    id_supplier = data.get("id_supplier")
    fields = []; vals = []
    for col in ["nama_supplier","no_hp","alamat","email"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_supplier)
    query = f"UPDATE Supplier SET {', '.join(fields)} WHERE id_supplier=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Supplier berhasil diperbarui"}), 200

@supplier_bp.route('', methods=['DELETE'])
def delete_supplier():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Supplier WHERE id_supplier=?", (data.get("id_supplier"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Supplier berhasil dihapus"}), 200
