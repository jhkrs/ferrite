import pytest
from eth_account import Account
from eth_account.messages import encode_typed_data
import ferrite

# Use the example from EIP-712 spec
# https://eips.ethereum.org/EIPS/eip-712

EIP712_EXAMPLE = {
    "types": {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
            {"name": "chainId", "type": "uint256"},
            {"name": "verifyingContract", "type": "address"},
        ],
        "Person": [
            {"name": "name", "type": "string"},
            {"name": "wallet", "type": "address"},
        ],
        "Mail": [
            {"name": "from", "type": "Person"},
            {"name": "to", "type": "Person"},
            {"name": "contents", "type": "string"},
        ],
    },
    "primaryType": "Mail",
    "domain": {
        "name": "Ether Mail",
        "version": "1",
        "chainId": 1,
        "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
    },
    "message": {
        "from": {"name": "Cow", "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"},
        "to": {"name": "Bob", "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"},
        "contents": "Hello, Bob!",
    },
}


@pytest.fixture
def private_key():
    return "0x" + "0" * 63 + "1"


def test_sign_typed_data_function(private_key):
    """Test the exposed verify_typed_data function directly."""
    # Sign with ferrite
    signed = ferrite.sign_typed_data(EIP712_EXAMPLE, private_key)

    assert signed["signature"] is not None
    assert len(signed["signature"]) > 0
    assert signed["v"] in [27, 28]


def test_monkey_patch_integration(private_key):
    """Test that Account.sign_typed_data uses our implementation."""
    # Ensure patch is installed
    ferrite.install()

    # eth_account's sign_typed_data expects the full dictionary as 'full_message' kwarg usually,
    # or just the dict as argument.
    # Signature: sign_typed_data(private_key, full_message)
    signed = Account.sign_typed_data(private_key, EIP712_EXAMPLE)

    assert signed.signature is not None
    assert signed.r > 0
    assert signed.s > 0


def test_correctness(private_key):
    """
    Verify the signature correctness by recovering the signer address.
    """
    ferrite.install()

    # 1. Sign using Ferrite (via patched Account)
    signed = Account.sign_typed_data(private_key, EIP712_EXAMPLE)

    # 2. Recover address using eth_account (independent verification)
    # encode_typed_data creates a SignableMessage
    signable_message = encode_typed_data(full_message=EIP712_EXAMPLE)

    recovered_address = Account.recover_message(
        signable_message, signature=signed.signature
    )

    # 3. Derive expected address
    account = Account.from_key(private_key)
    expected_address = account.address

    assert recovered_address == expected_address
