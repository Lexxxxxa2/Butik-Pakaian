from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

karyawan_ns = Namespace("karyawan", description="Manajemen Karyawan")

karyawan_model = karyawan_ns.model("Karyawan", {
    "id_karyawan": fields.Integer,
    "nama": fields.String(required=True),
    "jabatan": fields.String(required=True),
    "no_hp": fields.String(required=True),
    "alamat": fields.String(required=True)
})

@karyawan_ns.route("")
class Karyawan(Resource):

    @karyawan_ns.marshal_list_with(karyawan_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT id_karyawan,nama,jabatan,no_hp,alamat FROM Karyawan")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @karyawan_ns.expect(karyawan_model)
    def post(self):
        d = request.json
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Karyawan (nama,jabatan,no_hp,alamat)
            VALUES (?,?,?,?)
        """, (d["nama"], d["jabatan"], d["no_hp"], d["alamat"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Karyawan ditambahkan"}, 201

    @karyawan_ns.expect(karyawan_model)
    def put(self):
        d = request.json
        if not d.get("id_karyawan") or int(d["id_karyawan"]) <= 0:
            return {"error": "id_karyawan tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            UPDATE Karyawan
            SET nama=?, jabatan=?, no_hp=?, alamat=?
            WHERE id_karyawan=?
        """, (d["nama"], d["jabatan"], d["no_hp"], d["alamat"], d["id_karyawan"]))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Karyawan diperbarui"}

    def delete(self):
        d = request.json
        if not d.get("id_karyawan") or int(d["id_karyawan"]) <= 0:
            return {"error": "id_karyawan tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Karyawan WHERE id_karyawan=?", (d["id_karyawan"],))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Karyawan dihapus"}
