import hashlib
import hmac
import os
from base64 import urlsafe_b64encode
from hashlib import sha256
from time import time

from dotenv import load_dotenv

load_dotenv()
PEPPER = os.environ.get("PEPPER")


def hash_value(value: str, salt: str) -> str:
    """
    - Hash a string value using SHA-256 with
      a salt and pepper.
    """
    combined = f"{value}{salt}{PEPPER}".encode()
    return hashlib.sha256(combined).hexdigest()


def verify_value(value: str, hashed_value: str, salt: str) -> bool:
    """
    - Verify a value against a hashed value
      using the same salt and pepper
    """
    return hash_value(value, salt) == hashed_value


def generate_salt() -> str:
    """
    - Generates a random salt.
    """
    return os.urandom(16).hex()


def generate_sha256_hash(string: str) -> str:
    """
    - Generates a sha256 hash to be used for email onboarding.
    - NOTE: Is placed both in activation_link URL and redis cache.
    """
    secret_key = os.urandom(32)
    timestamp = str(int(time())).encode("utf-8")
    message = string.encode("utf-8") + timestamp
    signature = hmac.new(secret_key, message, sha256).digest()
    token = urlsafe_b64encode(message + signature).decode("utf-8")
    return token
