import hashlib


def hash_string(value: str) -> str:
    """
    - Simple repeatable 256 hash generator
    - NOTE: No randomness, salt, pepper, etc.,
      do not use for anything needing security.
    """
    return hashlib.sha256(value.encode()).hexdigest()
