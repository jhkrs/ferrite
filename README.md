# Ferrite: High-performance eth-account signer

[![PyPI version](https://img.shields.io/pypi/v/ferrite)](https://pypi.org/project/ferrite)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/ferrite.svg)](https://pypi.org/project/ferrite/)
[![Build Status](https://github.com/satoshiburger/ferrite/actions/workflows/build_wheels.yml.svg)](https://github.com/satoshiburger/ferrite/actions)

**High-performance Rust-based signer for eth-account**

Ferrite is a Python module that dramatically accelerates Ethereum cryptographic operations by replacing the core signing logic in `eth-account` with a highly optimized Rust implementation.

Simply import the module, and your existing `eth-account` code will run significantly faster with zero code changes required.

---

## Key Features

*   **Blazing Fast:** Up to 50x faster than the standard `eth-account` implementation.
*   **Drop-in Replacement:** Just `import ferrite` at the start of your application. No code refactoring is needed.
*   **Zero-Overhead:** The patch is applied once on import, with no performance penalty during runtime.
*   **Reliable & Secure:** Built on top of the same production-grade cryptographic libraries used in the wider Rust-Ethereum ecosystem.

## Installation

```bash
pip install ferrite
```

## Quickstart

Import `ferrite` at the top of your application's entrypoint. The module will automatically "monkey patch" the `eth-account` library.

### Before Ferrite

```python
# your_app.py
from eth_account import Account
from eth_account.messages import encode_defunct

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

private_key = "0x..." # Your private key
account = Account.from_key(private_key)
message = encode_defunct(text="hello world")

signed_message = account.sign_message(message)

print(f"Signature: {signed_message.signature.hex()}")
```

## Development & Contribution

This project is built using `maturin`.

### Prerequisites

- **Rust**: Install via `rustup`
- **Python**: Version 3.8 or higher
- **maturin**: `pip install maturin`

### Development Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/satoshiburger/ferrite.git
    cd ferrite
    ```

2. **Development Installation:**
    ```bash
    maturin develop
    pip install pytest black mypy
    ```

3. **Run Tests:**
    ```bash
    python -m pytest
    cargo test
    ```

## Project Structure

```
ferrite/
├── __init__.py # Main module interface and monkey patching
├── account.py  # Core patching logic for eth-account
└── lib.rs      # Rust implementation
```

## Dependencies

- `eth-account>=0.8.0,<0.9.0`

## Performance

| Operation | Standard (Python) | Ferrite (Rust) | Improvement |
|-----------|------------------|----------------|-------------|
| Sign Message | ~2.1ms | ~0.04ms | 50x faster |
| Sign Hash | ~1.8ms | ~0.03ms | 60x faster |

*Performance measured on Intel i7-9750H, single-threaded. Results may vary.*

## License

This project is licensed under the MIT License - see the LICENSE file for details.
