/*!
Ferrite: A high-performance Rust-based signer for eth-account.

This crate provides a Rust-based signer for eth-account, exposed to Python via PyO3.
*/

use ethers_core::types::transaction::eip712::{Eip712, TypedData};
use ethers_core::types::{H256, TransactionRequest};
use ethers_signers::{LocalWallet, Signer};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};


/// Signs a 32-byte hash with a private key.
/// ... (keeping existing comments for brevity in thought, but need to be careful with replace)
// Actually I will just update the imports and add the function at the end.

// Re-declaring imports since I'm replacing the top block or inserting?
// I'll replace the imports first.


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
fn sign_hash(py: Python, hash: &[u8], private_key: &[u8]) -> PyResult<PyObject> {
    if hash.len() != 32 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Hash must be exactly 32 bytes, got {}", hash.len())
        ));
    }

    let wallet = LocalWallet::from_bytes(private_key).map_err(|e| {
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

/// Signs an EIP-712 typed data object with a private key.
///
/// # Arguments
/// * `payload` - JSON string of the EIP-712 TypedData.
/// * `private_key` - 32-byte raw private key.
///
/// # Returns
/// A Python dictionary with the signature components:
/// `r`, `s`, `v`, and `signature`.
#[pyfunction]
fn sign_typed_data(py: Python, payload: &str, private_key: &[u8]) -> PyResult<PyObject> {
    let typed_data: TypedData = serde_json::from_str(payload).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid TypedData JSON: {}", e)
        )
    })?;

    let wallet = LocalWallet::from_bytes(private_key).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid private key: {}", e)
        )
    })?;

    // Encode the typed data according to EIP-712 to get the message hash
    let hash = typed_data.encode_eip712().map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Failed to encode EIP-712 data: {}", e)
        )
    })?;
    let hash = H256::from(hash);

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



/// Signs a transaction object with a private key.
///
/// # Arguments
/// * `payload` - JSON string of the transaction dictionary.
/// * `private_key` - 32-byte raw private key.
///
/// # Returns
/// A Python dictionary with the signature components and raw transaction:
/// `r`, `s`, `v`, `hash`, `rawTransaction` (bytes).
#[pyfunction]
fn sign_transaction(py: Python, payload: &str, private_key: &[u8]) -> PyResult<PyObject> {
    // 1. Parse TransactionRequest
    let request: TransactionRequest = serde_json::from_str(payload).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid Transaction JSON: {}", e)
        )
    })?;

    // 2. Convert to TypedTransaction
    let tx: ethers_core::types::transaction::eip2718::TypedTransaction = request.into();

    // 3. Create Wallet
    let wallet = LocalWallet::from_bytes(private_key).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid private key: {}", e)
        )
    })?;

    // Ensure wallet has the chain_id from the transaction if present (corrects replay protection)
    let chain_id = tx.chain_id().map(|id| id.as_u64()).unwrap_or(1);
    let wallet = wallet.with_chain_id(chain_id);

    // 4. Sign Transaction (using tokio runtime for async ethers call)
    let signature = std::thread::scope(|_| {
        let rt = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to create tokio runtime: {}", e)
                )
            })?;

        rt.block_on(async {
            wallet.sign_transaction(&tx).await.map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Signing failed: {}", e)
                )
            })
        })
    })?;

    // 5. Compute outputs
    let rlp_signed = tx.rlp_signed(&signature);
    let tx_hash = tx.hash(&signature);

    let result = PyDict::new(py);

    let mut r_bytes = [0u8; 32];
    signature.r.to_big_endian(&mut r_bytes);
    result.set_item("r", PyBytes::new(py, &r_bytes))?;

    let mut s_bytes = [0u8; 32];
    signature.s.to_big_endian(&mut s_bytes);
    result.set_item("s", PyBytes::new(py, &s_bytes))?;

    result.set_item("v", signature.v)?;

    // rawTransaction
    result.set_item("rawTransaction", PyBytes::new(py, &rlp_signed))?;
    // hash
    result.set_item("hash", PyBytes::new(py, &tx_hash.as_bytes()))?;

    Ok(result.into())
}

#[pymodule]
fn _ferrite(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sign_hash, m)?)?;
    m.add_function(wrap_pyfunction!(sign_typed_data, m)?)?;
    m.add_function(wrap_pyfunction!(sign_transaction, m)?)?;
    Ok(())
}
