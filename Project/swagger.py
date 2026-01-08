from flask_restx import Api

authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Masukkan token JWT dengan format: Bearer <token>"
    }
}

api = Api(
    title="API Sistem Informasi Butik Pakaian",
    version="1.0",
    description="Dokumentasi REST API menggunakan Swagger (Flask-RESTX)",
    doc="/docs",
    authorizations=authorizations,
    security="Bearer"
)
