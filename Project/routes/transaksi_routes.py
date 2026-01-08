from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

transaksi_ns = Namespace("transaksi", description="Manajemen Transaksi")

transaksi_model = transaksi_ns.model("Transaksi", {
    "id_transaksi": fields.Integer,
    "id_pelanggan": fields.Integer(required=True),
    "total_harga": fields.Float(required=True),
    "metode_pembayaran": fields.String(required=True)
})

@transaksi_ns.route("")
class Transaksi(Resource):

    @transaksi_ns.marshal_list_with(transaksi_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_transaksi,id_pelanggan,total_harga,metode_pembayaran
            FROM Transaksi
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @transaksi_ns.expect(transaksi_model)
    def post(self):
        d = request.json
        if int(d["id_pelanggan"]) <= 0:
            return {"error": "id_pelanggan tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Transaksi (id_pelanggan,total_harga,metode_pembayaran,tanggal)
            VALUES (?,?,?,datetime('now'))
        """, (d["id_pelanggan"], d["total_harga"], d["metode_pembayaran"]))
        conn.commit(); cur.close(); conn.close()

        return {"message": "Transaksi ditambahkan"}, 201

    def delete(self):
        d = request.json
        if not d.get("id_transaksi") or int(d["id_transaksi"]) <= 0:
            return {"error": "id_transaksi tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Transaksi WHERE id_transaksi=?", (d["id_transaksi"],))
        conn.commit(); cur.close(); conn.close()

        return {"message": "Transaksi dihapus"}
