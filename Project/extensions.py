# extensions.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Instance limiter tunggal untuk seluruh aplikasi
# Konfigurasi default limits bisa diubah sesuai kebutuhan
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "10 per minute"],  # contoh
    storage_uri="memory://"
)
