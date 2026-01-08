from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

pelanggan_ns = Namespace("pelanggan", description="Manajemen Pelanggan")

pelanggan_model = pelanggan_ns.model("Pelanggan", {
    "id_pelanggan": fields.Integer,
    "nama_pelanggan": fields.String(required=True),
    "no_hp": fields.String(required=True),
    "alamat": fields.String(required=True),
    "email": fields.String(required=True)
})

@pelanggan_ns.route("")
class Pelanggan(Resource):

    @pelanggan_ns.marshal_list_with(pelanggan_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id_pelanggan,nama_pelanggan,no_hp,alamat,email FROM Pelanggan")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @pelanggan_ns.expect(pelanggan_model)
    def post(self):
        d = request.json

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Pelanggan (nama_pelanggan,no_hp,alamat,email)
            VALUES (?,?,?,?)
        """, (d["nama_pelanggan"], d["no_hp"], d["alamat"], d["email"]))
        conn.commit(); cur.close(); conn.close()

        return {"message": "Pelanggan ditambahkan"}, 201

    @pelanggan_ns.expect(pelanggan_model)
    def put(self):
        d = request.json
        if not d.get("id_pelanggan") or int(d["id_pelanggan"]) <= 0:
            return {"error": "id_pelanggan tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            UPDATE Pelanggan
            SET nama_pelanggan=?, no_hp=?, alamat=?, email=?
            WHERE id_pelanggan=?
        """, (d["nama_pelanggan"], d["no_hp"], d["alamat"], d["email"], d["id_pelanggan"]))
        conn.commit(); cur.close(); conn.close()

        return {"message": "Pelanggan diperbarui"}

    def delete(self):
        d = request.json
        if not d.get("id_pelanggan") or int(d["id_pelanggan"]) <= 0:
            return {"error": "id_pelanggan tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Pelanggan WHERE id_pelanggan=?", (d["id_pelanggan"],))
        conn.commit(); cur.close(); conn.close()

        return {"message": "Pelanggan dihapus"}
