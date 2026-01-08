# rate_limit.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Instance limiter yang bisa di-init di app.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"],   # <- limit per menit
    storage_uri="memory://"
)
