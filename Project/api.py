# api.py
from flask_restx import Api

api = Api(
    title="API Manajemen Butik Pakaian",
    version="1.0",
    description="Dokumentasi API Backend Sistem Manajemen Butik Pakaian",
    doc="/"   # Swagger UI muncul di /
)
