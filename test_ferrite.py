#!/usr/bin/env python3
"""
Basic tests for Ferrite Signer functionality.

This module provides simple tests to verify that Ferrite's signing
operations work correctly and produce valid signatures.
"""

import pytest
from eth_account import Account
from eth_account.messages import encode_defunct
import ferrite


def test_basic_signing():
    """Test basic message signing functionality."""
    # Test private key (not for production use)
    private_key = "0x" + "0" * 63 + "1"

    # Create test message
    message = encode_defunct(text="Hello, Ferrite!")

    # Sign with Ferrite
    signed_message = Account.sign_message(message, private_key)

    # Verify signature is not empty
    assert signed_message.signature is not None
    assert len(signed_message.signature) > 0

    # Verify signature components exist
    assert signed_message.r > 0
    assert signed_message.s > 0
    assert signed_message.v in [27, 28]  # Valid recovery IDs

    print("✅ Basic signing test passed")


def test_signature_consistency():
    """Test that signatures are deterministic."""
    private_key = "0x" + "0" * 63 + "1"
    message = encode_defunct(text="Consistent test message")

    # Sign the same message twice
    sig1 = Account.sign_message(message, private_key)
    sig2 = Account.sign_message(message, private_key)

    # Signatures should be identical
    assert sig1.signature == sig2.signature
    assert sig1.r == sig2.r
    assert sig1.s == sig2.s
    assert sig1.v == sig2.v

    print("✅ Signature consistency test passed")


def test_different_messages():
    """Test signing different messages produces different signatures."""
    private_key = "0x" + "0" * 63 + "1"

    message1 = encode_defunct(text="Message 1")
    message2 = encode_defunct(text="Message 2")

    sig1 = Account.sign_message(message1, private_key)
    sig2 = Account.sign_message(message2, private_key)

    # Signatures should be different
    assert sig1.signature != sig2.signature

    print("✅ Different messages test passed")


def test_direct_function_access():
    """Test direct access to Ferrite functions."""
    private_key = "0x" + "0" * 63 + "1"
    message = encode_defunct(text="Direct function test")

    # Test direct function access
    signed = ferrite.sign_message(message, private_key)

    assert signed.signature is not None
    assert signed.r > 0
    assert signed.s > 0
    assert signed.v in [27, 28]

    print("✅ Direct function access test passed")


def test_hash_signing():
    """Test raw hash signing functionality."""
    private_key = "0x" + "0" * 63 + "1"

    # Create a 32-byte hash
    message_hash = b"\x00" * 32

    # Sign the hash
    signed = Account.signHash(message_hash, private_key)

    assert signed.signature is not None
    assert signed.r > 0
    assert signed.s > 0
    assert signed.v in [27, 28]

    print("✅ Hash signing test passed")


def test_private_key_formats():
    """Test different private key formats."""
    # Test with 0x prefix
    private_key1 = "0x" + "0" * 63 + "1"

    # Test without 0x prefix
    private_key2 = "0" * 63 + "1"

    message = encode_defunct(text="Key format test")

    sig1 = Account.sign_message(message, private_key1)
    sig2 = Account.sign_message(message, private_key2)

    # Both should work (though they will be different keys)
    assert sig1.signature is not None
    assert sig2.signature is not None

    print("✅ Private key formats test passed")


def run_all_tests():
    """Run all tests and report results."""
    print("Running Ferrite Signer Tests")
    print("=" * 40)

    try:
        test_basic_signing()
        test_signature_consistency()
        test_different_messages()
        test_direct_function_access()
        test_hash_signing()
        test_private_key_formats()

        print("\nAll tests passed!")
        return True

    except Exception as e:
        print(f"\nTest failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
