from flask_restx import Namespace, Resource, fields
from flask import request
from config import get_connection

produk_ns = Namespace(
    "produk",
    description="Manajemen Data Produk"
)

# =============================
# SWAGGER MODEL
# =============================
produk_model = produk_ns.model("Produk", {
    "id_produk": fields.Integer(required=False),
    "nama_produk": fields.String(required=True),
    "kategori": fields.String(required=True),
    "ukuran": fields.String(required=True),
    "warna": fields.String(required=True),
    "harga": fields.Float(required=True),
    "stok": fields.Integer(required=True)
})

produk_update_model = produk_ns.model("ProdukUpdate", {
    "id_produk": fields.Integer(required=True),
    "nama_produk": fields.String,
    "kategori": fields.String,
    "ukuran": fields.String,
    "warna": fields.String,
    "harga": fields.Float,
    "stok": fields.Integer
})

# =============================
# /produk
# =============================
@produk_ns.route("")
class ProdukList(Resource):

    @produk_ns.marshal_list_with(produk_model)
    def get(self):
        """Menampilkan semua produk"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_produk, nama_produk, kategori, ukuran, warna, harga, stok
            FROM Produk
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @produk_ns.expect(produk_model)
    def post(self):
        """Menambahkan produk baru"""
        data = request.json

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Produk (nama_produk, kategori, ukuran, warna, harga, stok)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["nama_produk"],
            data["kategori"],
            data["ukuran"],
            data["warna"],
            data["harga"],
            data["stok"]
        ))
        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Produk berhasil ditambahkan"}, 201

    @produk_ns.expect(produk_update_model)
    def put(self):
        """Update seluruh data produk (PUT)"""
        data = request.json

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Produk
            SET nama_produk=?, kategori=?, ukuran=?, warna=?, harga=?, stok=?
            WHERE id_produk=?
        """, (
            data.get("nama_produk"),
            data.get("kategori"),
            data.get("ukuran"),
            data.get("warna"),
            data.get("harga"),
            data.get("stok"),
            data.get("id_produk")
        ))
        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Produk berhasil diperbarui"}, 200

    @produk_ns.expect(produk_update_model)
    def patch(self):
        """Update sebagian data produk (PATCH)"""
        data = request.json
        id_produk = data.get("id_produk")

        fields = []
        values = []

        for col in ["nama_produk", "kategori", "ukuran", "warna", "harga", "stok"]:
            if col in data:
                fields.append(f"{col}=?")
                values.append(data[col])

        if not fields:
            return {"error": "Tidak ada field untuk diupdate"}, 400

        values.append(id_produk)

        query = f"""
            UPDATE Produk SET {', '.join(fields)}
            WHERE id_produk=?
        """

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Produk berhasil diperbarui sebagian"}, 200

    @produk_ns.expect(
        produk_ns.model("DeleteProduk", {
            "id_produk": fields.Integer(required=True)
        })
    )
    def delete(self):
        """Menghapus produk"""
        data = request.json

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM Produk WHERE id_produk=?",
            (data["id_produk"],)
        )
        conn.commit()
        cur.close()
        conn.close()

        return {"message": "Produk berhasil dihapus"}, 200
