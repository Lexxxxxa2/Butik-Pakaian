# routes/generic_routes.py
from flask import Blueprint, request, jsonify
from config import get_connection
from extensions import limiter

generic_bp = Blueprint("generic_bp", __name__)

TABLE_MAP = {
    "produk": {"table": "Produk", "pk": "id_produk"},
    "pelanggan": {"table": "Pelanggan", "pk": "id_pelanggan"},
    "supplier": {"table": "Supplier", "pk": "id_supplier"},
    "karyawan": {"table": "Karyawan", "pk": "id_karyawan"},
    "users": {"table": "Users", "pk": "id_user"},
    "pembelian": {"table": "Pembelian", "pk": "id_pembelian"},
    "detail_pembelian": {"table": "DetailPembelian", "pk": "id_detail_pembelian"},
    "transaksi": {"table": "Transaksi", "pk": "id_transaksi"},
    "detail": {"table": "DetailTransaksi", "pk": "id_detail"}
}

def rows_to_dicts(cur):
    cols = [c[0] for c in cur.description] if cur.description else []
    rows = cur.fetchall()
    out = []
    for r in rows:
        try:
            item = {cols[i]: r[i] for i in range(len(cols))}
        except Exception:
            item = {}
            for i, col in enumerate(cols):
                item[col] = getattr(r, col, None)
        out.append(item)
    return out

@generic_bp.route("/tables", methods=["GET"])
@limiter.limit("5 per minute")
def list_tables():
    return jsonify(list(TABLE_MAP.keys())), 200

@generic_bp.route("/<name>", methods=["GET"])
@limiter.limit("60 per minute")
def get_all_or_by_query(name):
    info = TABLE_MAP.get(name)
    if not info:
        return jsonify({"error": "Unknown table"}), 404

    table = info["table"]
    q = f"SELECT * FROM {table}"
    params = []
    where = []
    for key, val in request.args.items():
        if not key.replace("_", "").isalnum():
            continue
        where.append(f"{key} = ?")
        params.append(val)
    if where:
        q += " WHERE " + " AND ".join(where)

    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(q, tuple(params))
    except Exception as e:
        cur.close(); conn.close()
        return jsonify({"error": str(e)}), 500
    result = rows_to_dicts(cur)
    cur.close(); conn.close()
    return jsonify(result), 200

@generic_bp.route("/<name>", methods=["POST"])
@limiter.limit("10 per minute")
def create_item(name):
    info = TABLE_MAP.get(name)
    if not info:
        return jsonify({"error": "Unknown table"}), 404
    table = info["table"]
    data = request.get_json() or {}
    cols = []; vals = []; params = []
    for k, v in data.items():
        cols.append(k); vals.append("?"); params.append(v)
    if not cols:
        return jsonify({"error": "No data provided"}), 400

    q = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(vals)})"
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(q, tuple(params))
        conn.commit()
        try:
            cur.execute("SELECT @@IDENTITY")
            lastid = cur.fetchone()[0]
            pk = info["pk"]
            cur.execute(f"SELECT * FROM {table} WHERE {pk} = ?", (lastid,))
            new = rows_to_dicts(cur)
        except Exception:
            new = []
    except Exception as e:
        conn.rollback(); cur.close(); conn.close()
        return jsonify({"error": str(e)}), 500
    cur.close(); conn.close()
    return jsonify({"ok": True, "inserted": new}), 201

@generic_bp.route("/<name>", methods=["PUT", "PATCH"])
@limiter.limit("10 per minute")
def update_item(name):
    info = TABLE_MAP.get(name)
    if not info:
        return jsonify({"error": "Unknown table"}), 404
    table = info["table"]; pk = info["pk"]
    data = request.get_json() or {}
    if pk not in data:
        return jsonify({"error": f"{pk} required for update"}), 400
    idv = data.pop(pk)
    if not data:
        return jsonify({"error": "No fields to update"}), 400
    set_clause = ", ".join([f"{k}=?" for k in data.keys()])
    params = list(data.values()) + [idv]
    q = f"UPDATE {table} SET {set_clause} WHERE {pk} = ?"
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(q, tuple(params))
        conn.commit()
    except Exception as e:
        conn.rollback(); cur.close(); conn.close()
        return jsonify({"error": str(e)}), 500
    cur.close(); conn.close()
    return jsonify({"ok": True}), 200

@generic_bp.route("/<name>", methods=["DELETE"])
@limiter.limit("5 per minute")
def delete_item(name):
    info = TABLE_MAP.get(name)
    if not info:
        return jsonify({"error": "Unknown table"}), 404
    table = info["table"]; pk = info["pk"]
    data = request.get_json() or {}
    if pk not in data:
        return jsonify({"error": f"{pk} required to delete"}), 400
    idv = data[pk]
    q = f"DELETE FROM {table} WHERE {pk} = ?"
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute(q, (idv,))
        conn.commit()
    except Exception as e:
        conn.rollback(); cur.close(); conn.close()
        return jsonify({"error": str(e)}), 500
    cur.close(); conn.close()
    return jsonify({"ok": True}), 200
