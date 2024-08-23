import hashlib
import os

from dotenv import load_dotenv

load_dotenv()
PEPPER = os.environ.get("PEPPER")


def hash_value(value: str, salt: str) -> str:
    """Hash a string value using SHA-256 with a salt and pepper."""
    combined = f"{value}{salt}{PEPPER}".encode()
    return hashlib.sha256(combined).hexdigest()


def verify_value(value: str, hashed_value: str, salt: str) -> bool:
    """Verify a value against a hashed value using the same salt and pepper"""
    return hash_value(value, salt) == hashed_value


def generate_salt() -> str:
    """Generates a random salt."""
    return os.urandom(16).hex()
