from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

pembelian_ns = Namespace("pembelian", description="Manajemen Pembelian")

pembelian_model = pembelian_ns.model("Pembelian", {
    "id_pembelian": fields.Integer,
    "id_supplier": fields.Integer(required=True),
    "total_biaya": fields.Float(required=True)
})

@pembelian_ns.route("")
class Pembelian(Resource):

    @pembelian_ns.marshal_list_with(pembelian_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id_pembelian,id_supplier,total_biaya FROM Pembelian")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @pembelian_ns.expect(pembelian_model)
    def post(self):
        d = request.json
        if int(d["id_supplier"]) <= 0:
            return {"error": "id_supplier tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Pembelian (id_supplier,total_biaya,tanggal)
            VALUES (?,?,datetime('now'))
        """, (d["id_supplier"], d["total_biaya"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Pembelian ditambahkan"}, 201

    def delete(self):
        d = request.json
        if not d.get("id_pembelian") or int(d["id_pembelian"]) <= 0:
            return {"error": "id_pembelian tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Pembelian WHERE id_pembelian=?", (d["id_pembelian"],))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Pembelian dihapus"}
