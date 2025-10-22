"""
This module handles the monkey-patching of eth-account to use the Rust-based signer.
"""

import logging
from typing import Any

from eth_account.account import LocalAccount
from eth_account import Account as EthAccount
from eth_account.datastructures import SignedMessage
from hexbytes import HexBytes
from _ferrite import sign_hash as rust_sign_hash  # type: ignore

log = logging.getLogger(__name__)


def _sign_hash_wrapper(self, message_hash: bytes) -> SignedMessage:
    """Wraps the Rust-based sign_hash function for LocalAccount."""
    try:
        private_key_hex = self.key.hex()
        if not private_key_hex.startswith("0x"):
            private_key_hex = "0x" + private_key_hex

        signature_dict = rust_sign_hash(message_hash, private_key_hex)

        return SignedMessage(
            message_hash=HexBytes(message_hash),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
            signature=HexBytes(signature_dict["signature"]),
        )
    except Exception as e:
        log.error(f"Error in Rust signing operation: {e}")
        raise


def _account_sign_hash_wrapper(message_hash: bytes, private_key: str) -> SignedMessage:
    """Wraps the Rust-based sign_hash function for Account."""
    try:
        if isinstance(private_key, (bytes, bytearray)):
            private_key_hex = private_key.hex()
        else:
            private_key_hex = str(private_key)

        if not private_key_hex.startswith("0x"):
            private_key_hex = "0x" + private_key_hex

        signature_dict = rust_sign_hash(message_hash, private_key_hex)

        return SignedMessage(
            message_hash=HexBytes(message_hash),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
            signature=HexBytes(signature_dict["signature"]),
        )
    except Exception as e:
        log.error(f"Error in Rust signing operation (Account adapter): {e}")
        raise


def patch_eth_account() -> None:
    """
    Replaces the core signing methods on LocalAccount and Account with the Rust implementation.
    """
    try:
        # Use setattr to avoid mypy errors about assigning to methods on imported types
        setattr(LocalAccount, "_sign_hash", _sign_hash_wrapper)  # type: ignore[arg-type]
        # eth-account's Account class may expose signHash; we adapt the function name here
        setattr(EthAccount, "_sign_hash", _account_sign_hash_wrapper)  # type: ignore[arg-type]
        log.debug(
            "Patched LocalAccount._sign_hash and Account._sign_hash with Rust implementation"
        )
    except Exception as e:
        log.error(f"Failed to patch eth-account: {e}")
        raise
