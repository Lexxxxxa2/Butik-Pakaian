from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

supplier_ns = Namespace("supplier", description="Manajemen Supplier")

supplier_model = supplier_ns.model("Supplier", {
    "id_supplier": fields.Integer,
    "nama_supplier": fields.String(required=True),
    "no_hp": fields.String(required=True),
    "alamat": fields.String(required=True),
    "email": fields.String(required=True)
})

@supplier_ns.route("")
class Supplier(Resource):

    @supplier_ns.marshal_list_with(supplier_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id_supplier,nama_supplier,no_hp,alamat,email FROM Supplier")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @supplier_ns.expect(supplier_model)
    def post(self):
        d = request.json
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Supplier (nama_supplier,no_hp,alamat,email)
            VALUES (?,?,?,?)
        """, (d["nama_supplier"], d["no_hp"], d["alamat"], d["email"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Supplier ditambahkan"}, 201

    @supplier_ns.expect(supplier_model)
    def put(self):
        d = request.json
        if not d.get("id_supplier") or int(d["id_supplier"]) <= 0:
            return {"error": "id_supplier tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            UPDATE Supplier
            SET nama_supplier=?, no_hp=?, alamat=?, email=?
            WHERE id_supplier=?
        """, (d["nama_supplier"], d["no_hp"], d["alamat"], d["email"], d["id_supplier"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Supplier diperbarui"}

    def delete(self):
        d = request.json
        if not d.get("id_supplier") or int(d["id_supplier"]) <= 0:
            return {"error": "id_supplier tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Supplier WHERE id_supplier=?", (d["id_supplier"],))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Supplier dihapus"}
