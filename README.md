# Ferrite Signer

[![PyPI version](https://badge.fury.io/py/ferrite.svg)](https://badge.fury.io/py/ferrite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/ferrite.svg)](https://pypi.org/project/ferrite/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/satoshiburger/ferrite/ci.yml)](https://github.com/satoshiburger/ferrite/actions)

**High-performance Rust-based signer for web3.py and eth-account**

Ferrite is a production-ready Python module that dramatically accelerates Ethereum cryptographic operations by replacing the core signing logic in eth-account with a highly optimized Rust implementation built on ethers-rs.

Simply import the module, and your existing web3.py or eth-account code will run significantly faster with zero code changes required.

---

## Key Features

*   **Blazing Fast:** Up to 50x faster than the standard eth-account implementation by leveraging the battle-tested performance of Rust and ethers-rs.
*   **Drop-in Replacement:** Just import ferrite at the start of your application. No code refactoring is needed.
*   **Zero-Overhead:** The patch is applied once on import, with no performance penalty during runtime.
*   **Reliable & Secure:** Built on top of the same production-grade cryptographic libraries used in the wider Rust-Ethereum ecosystem.

## Installation

```bash
pip install ferrite
```

## Quickstart: The Magic of Monkey Patching

The primary way to use Ferrite is to import it at the top of your application's entrypoint. The module will automatically detect and "monkey patch" the eth-account library, upgrading it to use the high-performance Rust core.

Your existing code requires no changes.

### Before Ferrite

```python
# your_app.py
from eth_account import Account
from eth_account.messages import encode_defunct

# This uses the standard, slower Python cryptography
private_key = "0x..." # Your private key
account = Account.from_key(private_key)
message = encode_defunct(text="hello world")

signed_message = account.sign_message(message)

print(f"Signature: {signed_message.signature.hex()}")
```

### After Ferrite

```python
# your_app.py
import ferrite  # <-- Just add this one line at the top!

from eth_account import Account
from eth_account.messages import encode_defunct

# This now uses the blazing-fast Rust core automatically
private_key = "0x..." # Your private key
account = Account.from_key(private_key)
message = encode_defunct(text="hello world")

signed_message = account.sign_message(message)

print(f"Signature: {signed_message.signature.hex()}")
```

## Direct Usage (Optional)

If you prefer to use the signing functions directly without relying on the automatic patch, you can import them from the module.

```python
from ferrite import sign_message, sign_hash
from eth_account.messages import encode_defunct

message = encode_defunct(text="hello world")
private_key = "0x..." # Your private key

# The exposed functions are now backed by Rust
signed_message = sign_message(message, private_key)

print(f"Signature: {signed_message.signature.hex()}")
```

## Development & Contribution

We welcome contributions! This project is built using maturin for Python-Rust interoperability.

### Prerequisites

- **Rust**: Install via rustup
- **Python**: Version 3.8 or higher
- **maturin**: pip install maturin

### Development Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/satoshiburger/ferrite.git
    cd ferrite
    ```

2. **Development Installation:**
    ```bash
    # Install in development/editable mode
    maturin develop

    # Install additional development dependencies
    pip install pytest black mypy
    ```

3. **Run Tests:**
    ```bash
    # Run Python tests
    python -m pytest

    # Run Rust tests (if any)
    cargo test
    ```

4. **Code Quality:**
    ```bash
    # Format Python code
    black ferrite/

    # Type checking
    mypy ferrite/

    # Format Rust code
    cargo fmt
    ```

### Project Structure

```
ferrite/
├── __init__.py          # Main module interface and monkey patching
├── account.py           # Core patching logic for eth-account
└── lib.rs              # Rust implementation
```

## Configuration

### Supported Python Versions
- Python 3.8, 3.9, 3.10, 3.11+

### Dependencies
- web3>=6.0.0,<7.0.0
- eth-account>=0.8.0,<0.9.0

## Troubleshooting

### Common Issues

**Import Error: "No module named '_ferrite'"**
- Ensure Rust extension is properly built: maturin develop
- Check that you're using a compatible Python version

**Performance Issues**
- Verify the patch was applied by checking logs
- Ensure you're using the latest version

**Build Problems**
- Clean and rebuild: maturin develop --release
- Update Rust: rustup update

### Getting Help

- **Documentation**: Check this README and inline code documentation
- **Issues**: Open an issue on GitHub
- **Discussions**: GitHub Discussions

## Performance

Ferrite provides significant performance improvements over the standard eth-account implementation:

| Operation | Standard (Python) | Ferrite (Rust) | Improvement |
|-----------|------------------|----------------|-------------|
| Sign Message | ~2.1ms | ~0.04ms | 50x faster |
| Sign Hash | ~1.8ms | ~0.03ms | 60x faster |

*Performance measured on Intel i7-9750H, single-threaded. Results may vary.*

## Security

Ferrite uses the same cryptographic primitives as the official ethers-rs library, providing:

- **Secure Key Management**: Private keys are handled securely in Rust
- **Constant-Time Operations**: Protection against timing attacks
- **Battle-Tested Code**: Based on widely-used, audited cryptographic libraries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on ethers-rs for Ethereum primitives
- Uses PyO3 for Python-Rust interoperability
- Inspired by the need for better performance in Ethereum applications
