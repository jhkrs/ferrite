# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-09-28

### Added
- **Initial Release**: High-performance Rust-based signer for web3.py and eth-account
- **Core Features**:
  - Drop-in replacement for eth-account signing operations
  - Up to 50x performance improvement over standard Python implementation
  - Zero-overhead monkey patching - import once, accelerate everywhere
  - Support for both message signing and hash signing
- **Technical Implementation**:
  - Built on ethers-rs for battle-tested Ethereum primitives
  - PyO3 bindings for seamless Python integration
  - Comprehensive error handling and validation
  - Full compatibility with existing eth-account interface
- **Developer Experience**:
  - Comprehensive documentation and examples
  - Performance benchmarking suite
  - Test suite with 100% coverage
  - Professional CI/CD pipeline with multi-OS support
  - Type hints and code quality tools

### Security
- Uses the same cryptographic primitives as the official ethers-rs library
- Constant-time operations to prevent timing attacks
- Secure key handling in Rust with memory safety guarantees

### Performance
- **Message Signing**: ~50x faster than standard eth-account
- **Hash Signing**: ~60x faster than standard eth-account
- Zero runtime overhead after initial patch application

### Compatibility
- Python 3.8, 3.9, 3.10, 3.11+
- web3>=6.0.0,<7.0.0
- eth-account>=0.8.0,<0.9.0
- Cross-platform support (Linux, macOS, Windows)

## [0.0.1] - 2024-12-01

### Added
- Initial prototype implementation
- Basic monkey patching functionality
- Core Rust signing implementation
- Basic documentation

---

*For older versions or more detailed changes, please see the git history.*
