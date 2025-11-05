from passlib.context import CryptContext

# Allow bcrypt to silently truncate >72-byte passwords instead of throwing
try:
    pwdContext = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        truncate_error=False  # supported in Passlib >=1.7.4
    )
except TypeError:
    # fallback for older versions of Passlib that don’t support truncate_error
    pwdContext = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto"
    )

def hashPassword(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwdContext.hash(password)

def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    """Verify a plain-text password against a hashed password"""
    return pwdContext.verify(plainPassword, hashedPassword)
