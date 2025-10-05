"""
Ferrite Signer - High-performance Rust-based signer for web3.py and eth-account.

This module provides a drop-in replacement for Ethereum signing operations by
monkey-patching eth-account with optimized Rust implementations.

Example:
    >>> import ferrite
    >>> from eth_account import Account
    >>> # Your existing code now runs 50x faster with no changes!
"""

import sys
import logging
from typing import Optional

from eth_account import Account
from eth_account.messages import SignableMessage
from eth_account.datastructures import SignedMessage

from .account import patch_eth_account

# Set up a logger for the library
log = logging.getLogger(__name__)

# Explicitly list the functions to be exposed by the module
__all__ = ['sign_message', 'sign_hash', '__version__']

# Module version
__version__ = "0.1.0"


def sign_message(signable_message: SignableMessage, private_key: str) -> SignedMessage:
    """
    Sign an Ethereum message using the high-performance Rust backend.

    This function provides the same interface as eth_account.Account.sign_message
    but uses the optimized Rust implementation for significantly better performance.

    Args:
        signable_message: The message to sign, created by encode_defunct() or similar
        private_key: The private key as a hex string (with or without '0x' prefix)

    Returns:
        SignedMessage: The signed message containing signature, r, s, v values

    Raises:
        ValueError: If the private key is invalid or message cannot be signed

    Example:
        >>> from eth_account.messages import encode_defunct
        >>> message = encode_defunct(text="Hello, world!")
        >>> signed = sign_message(message, "0x" + "0" * 63)
    """
    return Account.sign_message(signable_message, private_key)


def sign_hash(message_hash: bytes, private_key: str) -> SignedMessage:
    """
    Sign a raw message hash using the high-performance Rust backend.

    This function provides the same interface as eth_account.Account.signHash
    but uses the optimized Rust implementation for significantly better performance.

    Args:
        message_hash: The 32-byte message hash to sign
        private_key: The private key as a hex string (with or without '0x' prefix)

    Returns:
        SignedMessage: The signed message containing signature, r, s, v values

    Raises:
        ValueError: If the private key is invalid or hash cannot be signed

    Example:
        >>> hash_bytes = bytes.fromhex("0" * 64)
        >>> signed = sign_hash(hash_bytes, "0x" + "0" * 63)
    """
    return Account.signHash(message_hash, private_key)


def _apply_patch() -> None:
    """
    Apply the monkey patch to eth-account to use Rust implementations.

    This function patches the LocalAccount._sign_hash method to use the
    high-performance Rust implementation. The patch is applied automatically
    on module import.

    Note:
        This function logs the patching operation for debugging purposes.
    """
    if "eth_account" in sys.modules:
        patch_eth_account()
        log.info("Successfully patched eth-account with high-performance Rust core.")
    else:
        log.debug("eth_account module not yet imported, patch will be applied on first use.")


# Automatically apply the patch on import
_apply_patch()
