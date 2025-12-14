# Ferrite: Rust patch for eth-account

[![PyPI version](https://img.shields.io/pypi/v/ferrite)](https://pypi.org/project/ferrite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/ferrite.svg)](https://pypi.org/project/ferrite/)
[![Build Status](https://github.com/satoshiburger/ferrite/actions/workflows/build_wheels.yml/badge.svg)](https://github.com/satoshiburger/ferrite/actions)

**High-performance Rust patch for eth-account**

Ferrite is a Python module that accelerates Ethereum cryptographic operations by replacing the core signing logic in `eth-account` with a Rust implementation.


## Key Features

*   **Blazing Fast:** Up to 40x faster than the standard `eth-account` implementation.
*   **Drop-in Replacement:** Just `import ferrite` at the start of your application. No code refactoring is needed.
*   **Zero-Overhead:** The patch is applied once on import, with no performance penalty during runtime.
*   **Reliable & Secure:** Built on top of the same production-grade cryptographic libraries used in the wider Rust-Ethereum ecosystem.

## Performance

| Operation | Standard (Python) | Ferrite (Rust) | Improvement |
|-----------|------------------|----------------|-------------|
| Sign Hash | ~3.29ms | ~0.11ms | ~30x faster |
| Sign Typed Data (EIP-712) | ~3.61ms | ~0.14ms | ~26x faster |

*Performance measured on a local development machine.*

## Installation

```bash
pip install ferrite
```

## Quickstart

1. Import `ferrite`.
2. Run `ferrite.install()`.

---

## Development & Contribution

This project is built using `maturin`.

### Prerequisites

- **Rust**: Install via `rustup`
- **Python**: Version 3.8 or higher
- **maturin**: `pip install maturin`

### Development Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/jhkrs/ferrite.git
    cd ferrite
    ```

2. **Development Installation:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Build:**
    ```bash
    maturin develop
    ```

4. **Run Tests:**
    ```bash
    pytest
    ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
