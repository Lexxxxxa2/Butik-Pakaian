from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

users_ns = Namespace("users", description="Manajemen User")

users_model = users_ns.model("User", {
    "id_user": fields.Integer,
    "username": fields.String(required=True),
    "password": fields.String,
    "role": fields.String(required=True),
    "id_karyawan": fields.Integer,
    "id_pelanggan": fields.Integer
})

@users_ns.route("")
class Users(Resource):

    @users_ns.marshal_list_with(users_model)
    def get(self):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id_user,username,role,id_karyawan,id_pelanggan
            FROM Users
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows

    @users_ns.expect(users_model)
    def post(self):
        d = request.json
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO Users (username,password_hash,role,id_karyawan,id_pelanggan)
            VALUES (?,?,?,?,?)
        """, (
            d["username"],
            d["password"],  # sesuai project kamu (belum hashing)
            d["role"],
            d.get("id_karyawan"),
            d.get("id_pelanggan")
        ))
        conn.commit(); cur.close(); conn.close()
        return {"message": "User ditambahkan"}, 201

    @users_ns.expect(users_model)
    def put(self):
        d = request.json
        if not d.get("id_user") or int(d["id_user"]) <= 0:
            return {"error": "id_user tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            UPDATE Users
            SET username=?, role=?, id_karyawan=?, id_pelanggan=?
            WHERE id_user=?
        """, (
            d["username"],
            d["role"],
            d.get("id_karyawan"),
            d.get("id_pelanggan"),
            d["id_user"]
        ))
        conn.commit(); cur.close(); conn.close()
        return {"message": "User diperbarui"}

    def delete(self):
        d = request.json
        if not d.get("id_user") or int(d["id_user"]) <= 0:
            return {"error": "id_user tidak valid"}, 400

        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM Users WHERE id_user=?", (d["id_user"],))
        conn.commit(); cur.close(); conn.close()
        return {"message": "User dihapus"}
