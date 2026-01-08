from flask import Blueprint, request, jsonify, g
from config import get_connection
from utils import row_to_dict, rows_to_list

transaksi_bp = Blueprint("transaksi_bp", __name__)

@transaksi_bp.route('', methods=['GET'])
def get_all_transaksi():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_transaksi, id_pelanggan, total_harga, metode_pembayaran, tanggal FROM Transaksi")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@transaksi_bp.route('/get', methods=['GET'])
def get_transaksi():
    id_transaksi = request.args.get("id_transaksi", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_transaksi, id_pelanggan, total_harga, metode_pembayaran, tanggal FROM Transaksi WHERE id_transaksi=?", (id_transaksi,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Transaksi tidak ditemukan"}), 404
    # ownership check is handled by middleware; here simply return
    return jsonify(data), 200

@transaksi_bp.route('', methods=['POST'])
def add_transaksi():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO Transaksi (id_pelanggan, total_harga, metode_pembayaran, tanggal) VALUES (?, ?, ?, datetime('now'))",
                (data.get("id_pelanggan"), data.get("total_harga"), data.get("metode_pembayaran")))
    conn.commit()
    last_id = cur.lastrowid if hasattr(cur, 'lastrowid') else None
    cur.close(); conn.close()
    return jsonify({"message":"Transaksi berhasil dibuat", "id_transaksi": last_id}), 201

@transaksi_bp.route('', methods=['PUT'])
def update_transaksi():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE Transaksi SET id_pelanggan=?, total_harga=?, metode_pembayaran=? WHERE id_transaksi=?
    """, (data.get("id_pelanggan"), data.get("total_harga"), data.get("metode_pembayaran"), data.get("id_transaksi")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Transaksi berhasil diperbarui"}), 200

@transaksi_bp.route('', methods=['PATCH'])
def patch_transaksi():
    data = request.get_json() or {}
    id_transaksi = data.get("id_transaksi")
    fields = []; vals = []
    for col in ["id_pelanggan","total_harga","metode_pembayaran"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_transaksi)
    query = f"UPDATE Transaksi SET {', '.join(fields)} WHERE id_transaksi=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Transaksi berhasil diperbarui"}), 200

@transaksi_bp.route('', methods=['DELETE'])
def delete_transaksi():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Transaksi WHERE id_transaksi=?", (data.get("id_transaksi"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Transaksi berhasil dihapus"}), 200
