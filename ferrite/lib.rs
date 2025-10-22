/*!
Ferrite: A high-performance Rust-based signer for eth-account.

This crate provides a Rust-based signer for eth-account, exposed to Python via PyO3.
*/

use ethers_core::types::H256;
use ethers_signers::{LocalWallet};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use std::str::FromStr;

/// Signs a 32-byte hash with a private key.
///
/// # Arguments
/// * `hash` - 32-byte message hash to sign.
/// * `private_key` - Hex-encoded private key.
///
/// # Returns
/// A Python dictionary with the signature components:
/// `r`, `s`, `v`, and `signature`.
#[pyfunction]
fn sign_hash(py: Python, hash: &[u8], private_key: &str) -> PyResult<PyObject> {
    if hash.len() != 32 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Hash must be exactly 32 bytes, got {}", hash.len())
        ));
    }

    let wallet = LocalWallet::from_str(private_key).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid private key: {}", e)
        )
    })?;

    let hash_array: [u8; 32] = hash.try_into().unwrap();
    let hash = H256(hash_array);

    let signature = py.allow_threads(|| wallet.sign_hash(hash)).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Signing failed: {}", e)
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
