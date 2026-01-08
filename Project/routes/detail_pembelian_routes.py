from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

detail_pembelian_ns = Namespace("detail_pembelian", description="Detail Pembelian")

detail_pembelian_model = detail_pembelian_ns.model("DetailPembelian", {
    "id_detail_pembelian": fields.Integer,
    "id_pembelian": fields.Integer(required=True),
    "id_produk": fields.Integer(required=True),
    "jumlah": fields.Integer(required=True),
    "harga_beli": fields.Float(required=True)
})

@detail_pembelian_ns.route("")
class DetailPembelian(Resource):

    @detail_pembelian_ns.marshal_list_with(detail_pembelian_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_detail_pembelian,id_pembelian,id_produk,jumlah,harga_beli
            FROM DetailPembelian
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @detail_pembelian_ns.expect(detail_pembelian_model)
    def post(self):
        d = request.json
        if int(d["id_pembelian"]) <= 0 or int(d["id_produk"]) <= 0:
            return {"error": "foreign key tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO DetailPembelian (id_pembelian,id_produk,jumlah,harga_beli)
            VALUES (?,?,?,?)
        """, (d["id_pembelian"], d["id_produk"], d["jumlah"], d["harga_beli"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Detail pembelian ditambahkan"}, 201

    def delete(self):
        d = request.json
        if not d.get("id_detail_pembelian") or int(d["id_detail_pembelian"]) <= 0:
            return {"error": "id_detail_pembelian tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute(
            "DELETE FROM DetailPembelian WHERE id_detail_pembelian=?",
            (d["id_detail_pembelian"],)
        )
        conn.commit(); cur.close(); conn.close()
        return {"message": "Detail pembelian dihapus"}
