from passlib.context import CryptContext

# Allow bcrypt to silently truncate >72-byte passwords instead of throwing
pwdContext = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    truncate_error=False
)

def hashPassword(password: str) -> str:
    # Hash a plain-text password
    return pwdContext.hash(password)

def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    # Verify a plain-text password against a hashed password
    return pwdContext.verify(plainPassword, hashedPassword)
