# Secure password hashing helpers
try:
    from werkzeug.security import generate_password_hash, check_password_hash

    def hash_password(password: str) -> str:
        # PBKDF2:sha256 by default; you can switch via method=...
        return generate_password_hash(password)

    def verify_password(password: str, hash_val: str) -> bool:
        return check_password_hash(hash_val, password)

except Exception:
    # very minimal fallback (not recommended for prod)
    import hashlib

    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(password: str, hash_val: str) -> bool:
        return hash_password(password) == hash_val