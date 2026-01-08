from flask_restx import Namespace, Resource, fields
from flask import request, session
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt, get_jwt_identity
from config import get_connection
import datetime as dt

auth_ns = Namespace(
    "auth",
    description="Autentikasi User"
)

# =============================
# SWAGGER MODELS
# =============================
login_model = auth_ns.model("LoginRequest", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

login_response = auth_ns.model("LoginResponse", {
    "access_token": fields.String,
    "role": fields.String
})

whoami_response = auth_ns.model("WhoAmI", {
    "identity": fields.String,
    "claims": fields.Raw
})

# =============================
# /login
# =============================
@auth_ns.route("/login")
class Login(Resource):

    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(login_response)
    def post(self):
        """Login user"""
        data = request.json
        username = data.get("username")
        password = data.get("password")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_user, password_hash, role, id_karyawan, id_pelanggan
            FROM Users WHERE username=?
        """, (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            auth_ns.abort(401, "Username atau password salah")

        uid, pw, role, id_karyawan, id_pelanggan = (
            user[0], user[1], user[2], user[3], user[4]
        )

        # ⚠️ plaintext (sesuai kondisi project kamu sekarang)
        if pw != password:
            auth_ns.abort(401, "Username atau password salah")

        token = create_access_token(
            identity=str(uid),
            additional_claims={
                "role": role,
                "id_karyawan": id_karyawan,
                "id_pelanggan": id_pelanggan
            },
            expires_delta=dt.timedelta(hours=8)
        )

        # session untuk frontend
        session["user"] = {
            "id": str(uid),
            "role": role,
            "id_karyawan": id_karyawan,
            "id_pelanggan": id_pelanggan
        }

        return {
            "access_token": token,
            "role": role
        }

# =============================
# /logout
# =============================
@auth_ns.route("/logout")
class Logout(Resource):

    def post(self):
        """Logout user"""
        session.pop("user", None)
        return {"message": "Logout berhasil"}

# =============================
# /whoami
# =============================
@auth_ns.route("/whoami")
class WhoAmI(Resource):

    @auth_ns.marshal_with(whoami_response)
    def get(self):
        """Cek user yang sedang login"""
        user_sess = session.get("user")
        if user_sess:
            return {
                "identity": user_sess.get("id"),
                "claims": {
                    "role": user_sess.get("role"),
                    "id_karyawan": user_sess.get("id_karyawan"),
                    "id_pelanggan": user_sess.get("id_pelanggan")
                }
            }

        try:
            verify_jwt_in_request()
            return {
                "identity": get_jwt_identity(),
                "claims": get_jwt()
            }
        except Exception:
            auth_ns.abort(401, "Not authenticated")
