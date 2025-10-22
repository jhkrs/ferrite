from typing import Dict, Any, TypedDict

class SignatureDict(TypedDict):
    r: bytes
    s: bytes
    v: int
    signature: bytes

def sign_hash(message_hash: bytes, private_key_hex: str) -> SignatureDict: ...
