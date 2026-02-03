"""
This module handles the monkey-patching of eth-account to use the Rust-based signer.
"""

import json
import logging
from typing import Any, Dict

from eth_account.account import LocalAccount
from eth_account import Account as EthAccount
from eth_account.datastructures import SignedMessage
from hexbytes import HexBytes
from _ferrite import sign_hash as rust_sign_hash  # type: ignore
from _ferrite import sign_typed_data as rust_sign_typed_data  # type: ignore
from _ferrite import sign_transaction as rust_sign_transaction  # type: ignore

log = logging.getLogger(__name__)


def _sign_hash_wrapper(self, message_hash: bytes) -> SignedMessage:
    """Wraps the Rust-based sign_hash function for LocalAccount."""
    try:
        signature_dict = rust_sign_hash(message_hash, self.key)

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
            private_key_bytes = private_key
        else:
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key_bytes = bytes.fromhex(private_key)

        signature_dict = rust_sign_hash(message_hash, private_key_bytes)

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


def _sign_typed_data_wrapper(self, full_message: Dict[str, Any]) -> SignedMessage:
    """Wraps the Rust-based sign_typed_data function for LocalAccount."""
    try:
        json_payload = json.dumps(full_message)
        signature_dict = rust_sign_typed_data(json_payload, self.key)

        return SignedMessage(
            message_hash=HexBytes(b""),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
            signature=HexBytes(signature_dict["signature"]),
        )
    except Exception as e:
        log.error(f"Error in Rust typed data signing operation: {e}")
        raise


def _account_sign_typed_data_wrapper(
    private_key: str, full_message: Dict[str, Any]
) -> SignedMessage:
    """Wraps the Rust-based sign_typed_data function for Account."""
    try:
        if isinstance(private_key, (bytes, bytearray)):
            private_key_bytes = private_key
        else:
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key_bytes = bytes.fromhex(private_key)

        json_payload = json.dumps(full_message)
        signature_dict = rust_sign_typed_data(json_payload, private_key_bytes)

        return SignedMessage(
            message_hash=HexBytes(b""),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
            signature=HexBytes(signature_dict["signature"]),
        )
    except Exception as e:
        log.error(f"Error in Rust typed data signing operation (Account adapter): {e}")
        raise


def _sanitize_transaction(transaction_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes the transaction dictionary for Rust compatibility.
    Converts integer fields to hex strings as expected by ethers-rs U256 deserialization.
    """
    sanitized = transaction_dict.copy()
    fields_to_hex = [
        "value",
        "gas",
        "gasPrice",
        "maxFeePerGas",
        "maxPriorityFeePerGas",
        "nonce",
        "chainId",
    ]

    for field in fields_to_hex:
        if field in sanitized:
            val = sanitized[field]
            if isinstance(val, int):
                sanitized[field] = hex(val)
            elif isinstance(val, str) and not val.startswith("0x") and val.isdigit():
                sanitized[field] = hex(int(val))

    return sanitized


def _sign_transaction_wrapper(self, transaction_dict: Dict[str, Any]) -> SignedMessage:
    """Wraps the Rust-based sign_transaction function for LocalAccount."""
    try:
        sanitized_tx = _sanitize_transaction(transaction_dict)
        json_payload = json.dumps(sanitized_tx)
        signature_dict = rust_sign_transaction(json_payload, self.key)

        from eth_account.datastructures import SignedTransaction

        return SignedTransaction(
            raw_transaction=HexBytes(signature_dict["rawTransaction"]),
            hash=HexBytes(signature_dict["hash"]),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
        )
    except Exception as e:
        log.error(f"Error in Rust transaction signing operation: {e}")
        raise


def _account_sign_transaction_wrapper(
    transaction_dict: Dict[str, Any], private_key: str
) -> SignedMessage:
    """Wraps the Rust-based sign_transaction function for Account."""
    try:
        if isinstance(private_key, (bytes, bytearray)):
            private_key_bytes = private_key
        else:
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            private_key_bytes = bytes.fromhex(private_key)

        sanitized_tx = _sanitize_transaction(transaction_dict)
        json_payload = json.dumps(sanitized_tx)
        signature_dict = rust_sign_transaction(json_payload, private_key_bytes)

        from eth_account.datastructures import SignedTransaction

        return SignedTransaction(
            raw_transaction=HexBytes(signature_dict["rawTransaction"]),
            hash=HexBytes(signature_dict["hash"]),
            r=int.from_bytes(signature_dict["r"], "big"),
            s=int.from_bytes(signature_dict["s"], "big"),
            v=signature_dict["v"],
        )
    except Exception as e:
        log.error(f"Error in Rust transaction signing operation (Account adapter): {e}")
        raise


def patch_eth_account() -> None:
    """
    Replaces the core signing methods on LocalAccount and Account with the Rust implementation.
    """
    try:
        setattr(LocalAccount, "_sign_hash", _sign_hash_wrapper)
        setattr(EthAccount, "_sign_hash", _account_sign_hash_wrapper)

        setattr(LocalAccount, "sign_typed_data", _sign_typed_data_wrapper)
        setattr(EthAccount, "sign_typed_data", _account_sign_typed_data_wrapper)

        setattr(LocalAccount, "sign_transaction", _sign_transaction_wrapper)
        setattr(EthAccount, "sign_transaction", _account_sign_transaction_wrapper)

        log.debug("Patched LocalAccount and Account methods with Rust implementation")
    except Exception as e:
        log.error(f"Failed to patch eth-account: {e}")
        raise
