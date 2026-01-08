from flask import Blueprint, request, jsonify
from config import get_connection
from utils import row_to_dict, rows_to_list

detail_pembelian_bp = Blueprint("detail_pembelian_bp", __name__)

@detail_pembelian_bp.route('', methods=['GET'])
def get_detail_pembelian():
    id_pembelian = request.args.get("id_pembelian", type=int)
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id_detail_pembelian, id_pembelian, id_produk, jumlah, harga_beli FROM DetailPembelian WHERE id_pembelian=?", (id_pembelian,))
    rows = cur.fetchall(); data = rows_to_list(cur, rows)
    cur.close(); conn.close()
    if not data:
        return jsonify({"error":"Detail pembelian tidak ditemukan"}), 404
    return jsonify(data), 200

@detail_pembelian_bp.route('', methods=['POST'])
def add_detail_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO DetailPembelian (id_pembelian, id_produk, jumlah, harga_beli) VALUES (?, ?, ?, ?)",
                (data.get("id_pembelian"), data.get("id_produk"), data.get("jumlah"), data.get("harga_beli")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail pembelian berhasil ditambahkan"}), 201

@detail_pembelian_bp.route('', methods=['PUT'])
def update_detail_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE DetailPembelian SET id_pembelian=?, id_produk=?, jumlah=?, harga_beli=? WHERE id_detail_pembelian=?
    """, (data.get("id_pembelian"), data.get("id_produk"), data.get("jumlah"), data.get("harga_beli"), data.get("id_detail_pembelian")))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail pembelian berhasil diperbarui"}), 200

@detail_pembelian_bp.route('', methods=['PATCH'])
def patch_detail_pembelian():
    data = request.get_json() or {}
    id_detail = data.get("id_detail_pembelian")
    fields = []; vals = []
    for col in ["id_pembelian","id_produk","jumlah","harga_beli"]:
        if col in data:
            fields.append(f"{col}=?"); vals.append(data[col])
    if not fields:
        return jsonify({"error":"Tidak ada field untuk diupdate"}), 400
    vals.append(id_detail)
    query = f"UPDATE DetailPembelian SET {', '.join(fields)} WHERE id_detail_pembelian=?"
    conn = get_connection(); cur = conn.cursor()
    cur.execute(query, vals)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail pembelian berhasil diperbarui"}), 200

@detail_pembelian_bp.route('', methods=['DELETE'])
def delete_detail_pembelian():
    data = request.get_json() or {}
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM DetailPembelian WHERE id_detail_pembelian=?", (data.get("id_detail_pembelian"),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message":"Detail pembelian berhasil dihapus"}), 200
