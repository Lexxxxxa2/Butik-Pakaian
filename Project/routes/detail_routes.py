from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

detail_ns = Namespace("detail", description="Detail Transaksi")

detail_model = detail_ns.model("Detail", {
    "id_detail": fields.Integer,
    "id_transaksi": fields.Integer(required=True),
    "id_produk": fields.Integer(required=True),
    "jumlah": fields.Integer(required=True),
    "harga_satuan": fields.Float(required=True)
})

@detail_ns.route("")
class Detail(Resource):

    @detail_ns.marshal_list_with(detail_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_detail,id_transaksi,id_produk,jumlah,harga_satuan
            FROM DetailTransaksi
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @detail_ns.expect(detail_model)
    def post(self):
        d = request.json
        if int(d["id_transaksi"]) <= 0 or int(d["id_produk"]) <= 0:
            return {"error": "foreign key tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO DetailTransaksi (id_transaksi,id_produk,jumlah,harga_satuan)
            VALUES (?,?,?,?)
        """, (d["id_transaksi"], d["id_produk"], d["jumlah"], d["harga_satuan"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Detail ditambahkan"}, 201

    def delete(self):
        d = request.json
        if not d.get("id_detail") or int(d["id_detail"]) <= 0:
            return {"error": "id_detail tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM DetailTransaksi WHERE id_detail=?", (d["id_detail"],))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Detail dihapus"}
