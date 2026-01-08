# utils.py
from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from decimal import Decimal
import datetime as dt

# -----------------------
# SERIALIZATION HELPERS
# -----------------------
def serialize_value(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.isoformat()
    return v

def row_to_dict(cur, row):
    if row is None:
        return None
    cols = [c[0] for c in cur.description]
    return {col: serialize_value(row[i]) for i, col in enumerate(cols)}

def rows_to_list(cur, rows):
    cols = [c[0] for c in cur.description]
    return [{col: serialize_value(row[i]) for i, col in enumerate(cols)} for row in rows or []]

# -----------------------
# AUTH HELPERS
# -----------------------
def auth_optional():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            g.jwt_claims = {}
            g.jwt_role = None
            g.jwt_identity = None
            try:
                verify_jwt_in_request(optional=True)
                g.jwt_claims = get_jwt() or {}
                g.jwt_role = g.jwt_claims.get("role")
                g.jwt_identity = get_jwt_identity()
            except Exception:
                g.jwt_claims = {}
                g.jwt_role = None
                g.jwt_identity = None
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def is_admin():
    """Admin & Owner dianggap sama"""
    role = getattr(g, "jwt_role", None)
    return role in ("Admin", "Owner") or getattr(g, "is_admin", False)

def has_role(*roles):
    role = getattr(g, "jwt_role", None)
    return role in roles

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = getattr(g, "jwt_role", None)
            if role not in roles:
                return jsonify({"error": "Akses ditolak: role tidak diizinkan"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
