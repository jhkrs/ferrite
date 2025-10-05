/*!
Ferrite Signer - High-performance Ethereum signing library for Python.

This Rust crate provides optimized ECDSA signature generation for Ethereum operations,
serving as the backend for the Ferrite Python library. Built on ethers-rs for
battle-tested cryptographic primitives and PyO3 for seamless Python integration.

# Features

- High Performance: Optimized Rust implementation with minimal overhead
- Ethereum Compatible: Uses the same cryptographic primitives as ethers-rs
- Python Integration: Seamless PyO3 bindings for Python interoperability
- Memory Safe: Zero-cost abstractions with Rust's memory safety guarantees

# Example Usage

```rust
use ethers_core::types::H256;
use ethers_signers::{LocalWallet, Signer};

// Create a wallet from a private key
let private_key = "0x0123456789abcdef...";
let wallet = LocalWallet::from_str(private_key).unwrap();

// Sign a message hash
let hash = H256::from([0u8; 32]);
let signature = wallet.sign_hash(hash).unwrap();
```
*/

use ethers_core::types::H256;
use ethers_signers::{LocalWallet, Signer};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use std::str::FromStr;

/// Signs a 32-byte hash using a private key with optimized Rust implementation.
///
/// This function provides the core cryptographic operation for the Ferrite library,
/// implementing ECDSA signature generation using the same algorithms as ethers-rs.
/// The function is exposed to Python via PyO3 for high-performance signing operations.
///
/// # Arguments
/// * `py` - Python context (required by PyO3)
/// * `hash` - 32-byte message hash to sign
/// * `private_key` - Hex-encoded private key string (with or without 0x prefix)
///
/// # Returns
/// A Python dictionary containing:
/// * `r` - R component of the ECDSA signature (32 bytes)
/// * `s` - S component of the ECDSA signature (32 bytes)
/// * `v` - Recovery ID (1 byte)
/// * `signature` - Complete signature as bytes
///
/// # Errors
/// Returns a PyValueError if:
/// * The private key format is invalid
/// * The hash is not exactly 32 bytes
/// * The signing operation fails
///
/// # Example
/// ```rust
/// let hash = b"\x00".repeat(32);
/// let private_key = "0x" + &"0".repeat(64);
/// let result = sign_hash(py, &hash, &private_key).unwrap();
/// ```
#[pyfunction]
fn sign_hash(py: Python, hash: &[u8], private_key: &str) -> PyResult<PyObject> {
    // Validate hash length (must be 32 bytes for Ethereum)
    if hash.len() != 32 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Hash must be exactly 32 bytes, got {}", hash.len())
        ));
    }

    // Create wallet from private key
    let wallet = LocalWallet::from_str(private_key).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid private key format: {}. Key must be a valid hex string (with or without 0x prefix).", e)
        )
    })?;

    // Convert hash to H256
    let hash_array: [u8; 32] = hash.try_into().map_err(|_| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Failed to convert hash to 32-byte array"
        )
    })?;
    let hash = H256(hash_array);

    // Perform signing operation with optimized threading
    let signature = py.allow_threads(|| {
        wallet.sign_hash(hash)
    }).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Signing operation failed: {}", e)
        )
    })?;

    let result = PyDict::new(py);
    let mut r_bytes = [0u8; 32];
    signature.r.to_big_endian(&mut r_bytes);
    result.set_item("r", PyBytes::new(py, &r_bytes))?;

    let mut s_bytes = [0u8; 32];
    signature.s.to_big_endian(&mut s_bytes);
    result.set_item("s", PyBytes::new(py, &s_bytes))?;

    result.set_item("v", signature.v)?;
    result.set_item("signature", PyBytes::new(py, &signature.to_vec()))?;

    Ok(result.into())
}

#[pymodule]
fn _ferrite(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sign_hash, m)?)?;
    Ok(())
}
