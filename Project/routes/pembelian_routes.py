from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

pembelian_bp = Blueprint("pembelian_bp", __name__)

@pembelian_bp.route('', methods=['GET'])
def get_all_pembelian():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_pembelian, id_supplier, total_biaya, tanggal FROM Pembelian")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@pembelian_bp.route('/get', methods=['GET'])
def get_pembelian():
    id_pembelian = request.args.get("id_pembelian", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_pembelian, id_supplier, total_biaya, tanggal FROM Pembelian WHERE id_pembelian=?", (id_pembelian,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Pembelian tidak ditemukan"}), 404
    return jsonify(data), 200

@pembelian_bp.route('', methods=['POST'])
def add_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Pembelian (id_supplier, total_biaya, tanggal) VALUES (?, ?, datetime('now'))",
                (data.get("id_supplier"), data.get("total_biaya")))
    conn.commit()
    last_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
    cur.close(); conn.close()
    return jsonify({"message":"Pembelian berhasil dibuat", "id_pembelian": last_id}), 201

@pembelian_bp.route('', methods=['PUT'])
def update_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE Pembelian SET id_supplier=?, total_biaya=? WHERE id_pembelian=?",
                (data.get("id_supplier"), data.get("total_biaya"), data.get("id_pembelian")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pembelian berhasil diperbarui"}), 200

@pembelian_bp.route('', methods=['PATCH'])
def patch_pembelian():
    data = request.get_json() or {}
    id_pembelian = data.get("id_pembelian")
    fields = []; vals = []
    for col in ["id_supplier","total_biaya"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_pembelian)
    query = f"UPDATE Pembelian SET {', '.join(fields)} WHERE id_pembelian=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pembelian berhasil diperbarui"}), 200

@pembelian_bp.route('', methods=['DELETE'])
def delete_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Pembelian WHERE id_pembelian=?", (data.get("id_pembelian"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Pembelian berhasil dihapus"}), 200
