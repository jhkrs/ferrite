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


@pytest.fixture
def private_key():
    """Provides a basic, consistent private key for testing."""
    return "0x" + "0" * 63 + "1"


def test_basic_signing(private_key):
    """Test basic message signing functionality."""
    message = encode_defunct(text="Hello, Ferrite!")
    signed_message = Account.sign_message(message, private_key)

    assert signed_message.signature is not None
    assert len(signed_message.signature) > 0
    assert signed_message.r > 0
    assert signed_message.s > 0
    assert signed_message.v in [27, 28]


def test_signature_consistency(private_key):
    """Test that signatures are deterministic."""
    message = encode_defunct(text="Consistent test message")

    sig1 = Account.sign_message(message, private_key)
    sig2 = Account.sign_message(message, private_key)

    assert sig1.signature == sig2.signature
    assert sig1.r == sig2.r
    assert sig1.s == sig2.s
    assert sig1.v == sig2.v


def test_different_messages(private_key):
    """Test signing different messages produces different signatures."""
    message1 = encode_defunct(text="Message 1")
    message2 = encode_defunct(text="Message 2")

    sig1 = Account.sign_message(message1, private_key)
    sig2 = Account.sign_message(message2, private_key)

    assert sig1.signature != sig2.signature


def test_direct_function_access(private_key):
    """Test direct access to Ferrite functions."""
    message = encode_defunct(text="Direct function test")
    signed = ferrite.sign_message(message, private_key)

    assert signed.signature is not None
    assert signed.r > 0
    assert signed.s > 0
    assert signed.v in [27, 28]


def test_hash_signing(private_key):
    """Test raw hash signing functionality."""
    message_hash = b"\x00" * 32
    signed = Account._sign_hash(message_hash, private_key)

    assert signed.signature is not None
    assert signed.r > 0
    assert signed.s > 0
    assert signed.v in [27, 28]


def test_private_key_formats():
    """Test different private key formats."""
    private_key1 = "0x" + "0" * 63 + "1"
    private_key2 = "0" * 63 + "1"
    message = encode_defunct(text="Key format test")

    sig1 = Account.sign_message(message, private_key1)
    sig2 = Account.sign_message(message, private_key2)

    assert sig1.signature is not None
    assert sig2.signature is not None
