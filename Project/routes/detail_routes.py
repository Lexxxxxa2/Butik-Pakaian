from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

detail_bp = Blueprint("detail_bp", __name__)

@detail_bp.route('', methods=['GET'])
def get_all_detail():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_detail, id_transaksi, id_produk, jumlah, harga_satuan FROM DetailTransaksi")
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    return jsonify(data), 200

@detail_bp.route('/get', methods=['GET'])
def get_detail():
    id_detail = request.args.get("id_detail", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_detail, id_transaksi, id_produk, jumlah, harga_satuan FROM DetailTransaksi WHERE id_detail=?", (id_detail,))
    row = cur.fetchone(); data = row_to_dict(cur, row)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Detail transaksi tidak ditemukan"}), 404
    return jsonify(data), 200

@detail_bp.route('', methods=['POST'])
def add_detail():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO DetailTransaksi (id_transaksi, id_produk, jumlah, harga_satuan) VALUES (?, ?, ?, ?)",
                (data.get("id_transaksi"), data.get("id_produk"), data.get("jumlah"), data.get("harga_satuan")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail transaksi berhasil ditambahkan"}), 201

@detail_bp.route('', methods=['PUT'])
def update_detail():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE DetailTransaksi SET id_transaksi=?, id_produk=?, jumlah=?, harga_satuan=? WHERE id_detail=?
    """, (data.get("id_transaksi"), data.get("id_produk"), data.get("jumlah"), data.get("harga_satuan"), data.get("id_detail")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail transaksi berhasil diperbarui"}), 200

@detail_bp.route('', methods=['PATCH'])
def patch_detail():
    data = request.get_json() or {}
    id_detail = data.get("id_detail")
    fields = []; vals = []
    for col in ["id_transaksi","id_produk","jumlah","harga_satuan"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_detail)
    query = f"UPDATE DetailTransaksi SET {', '.join(fields)} WHERE id_detail=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail transaksi berhasil diperbarui"}), 200

@detail_bp.route('', methods=['DELETE'])
def delete_detail():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM DetailTransaksi WHERE id_detail=?", (data.get("id_detail"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail transaksi berhasil dihapus"}), 200
