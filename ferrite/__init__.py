"""
Ferrite: A high-performance Rust-based signer for eth-account.

This module monkey-patches eth-account to use a Rust-based signer for a significant
performance increase.
"""

import logging
from eth_account import Account
from eth_account.messages import SignableMessage
from eth_account.datastructures import SignedMessage
from .account import patch_eth_account

log = logging.getLogger(__name__)

__all__ = ["sign_message", "sign_hash", "__version__"]
__version__ = "0.1.0"

_patch_applied = False


def install() -> None:
    """
    Applies the monkey patch to eth-account to use the Rust-based signer.

    This function is called automatically when you use `sign_message` or `sign_hash`.
    """
    global _patch_applied
    if not _patch_applied:
        try:
            patch_eth_account()
            _patch_applied = True
            log.info(
                "Successfully patched eth-account with high-performance Rust core."
            )
        except Exception as e:
            log.error(f"Failed to patch eth-account: {e}")
            raise


def sign_message(signable_message: SignableMessage, private_key: str) -> SignedMessage:
    """
    Sign an Ethereum message with the high-performance Rust backend.

    This function has the same interface as eth_account.Account.sign_message.

    Args:
        signable_message: The message to sign.
        private_key: The private key as a hex string.

    Returns:
        The signed message.
    """
    install()
    return Account.sign_message(signable_message, private_key)


def sign_hash(message_hash: bytes, private_key: str) -> SignedMessage:
    """
    Sign a raw message hash with the high-performance Rust backend.

    This function has the same interface as eth_account.Account.signHash.

    Args:
        message_hash: The 32-byte message hash to sign.
        private_key: The private key as a hex string.

    Returns:
        The signed message.
    """
    install()
    return Account.signHash(message_hash, private_key)
