"""
Core patching logic for eth-account integration.

This module handles the monkey-patching of eth-account's LocalAccount class
to use the high-performance Rust implementation for cryptographic operations.
"""

import logging
from typing import Dict, Any

from eth_account.account import LocalAccount
from eth_account.datastructures import SignedMessage
from hexbytes import HexBytes

# Import the rust function from the compiled module
from _ferrite import sign_hash as rust_sign_hash

# Set up a logger for this module
log = logging.getLogger(__name__)


def _sign_hash_wrapper(self, message_hash: bytes) -> SignedMessage:
    """
    High-performance wrapper for the Rust-based sign_hash function.

    This method replaces the original _sign_hash method on the LocalAccount class,
    providing a drop-in replacement that uses the optimized Rust implementation.

    Args:
        self: The LocalAccount instance containing the private key
        message_hash: The 32-byte message hash to sign

    Returns:
        SignedMessage: The signature containing r, s, v values and the full signature

    Raises:
        Exception: If the Rust signing function fails for any reason

    Note:
        This method maintains full compatibility with the original eth-account interface
        while providing significant performance improvements through Rust optimization.
    """
    try:
        private_key_bytes = self.key
        signature_dict = rust_sign_hash(message_hash, private_key_bytes.hex())

        return SignedMessage(
            messageHash=message_hash,
            r=int.from_bytes(signature_dict['r'], 'big'),
            s=int.from_bytes(signature_dict['s'], 'big'),
            v=signature_dict['v'],
            signature=HexBytes(signature_dict['signature'])
        )
    except Exception as e:
        log.error(f"Error in Rust signing operation: {e}")
        raise


def patch_eth_account() -> None:
    """
    Replace the core signing method on the LocalAccount class with Rust implementation.

    This function performs monkey-patching of the LocalAccount._sign_hash method
    to use the high-performance Rust-based wrapper. By patching this internal method,
    both public methods (signHash and sign_message) automatically benefit from
    the performance improvements.

    Args:
        None

    Returns:
        None

    Raises:
        AttributeError: If LocalAccount class doesn't have the expected structure

    Note:
        This patch is applied automatically when the ferrite module is imported.
        The original method is completely replaced, ensuring zero overhead.

    Example:
        >>> from ferrite.account import patch_eth_account
        >>> patch_eth_account()  # Apply the patch manually if needed
    """
    try:
        # Store the original method for potential restoration
        original_method = getattr(LocalAccount, '_sign_hash', None)

        # Apply the patch
        LocalAccount._sign_hash = _sign_hash_wrapper

        log.debug("Successfully patched LocalAccount._sign_hash with Rust implementation")
        log.debug(f"Original method backed up: {original_method is not None}")

    except Exception as e:
        log.error(f"Failed to patch eth-account: {e}")
        raise
