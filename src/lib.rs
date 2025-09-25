use ethers_core::types::{
    transaction::eip2718::TypedTransaction, Eip1559TransactionRequest, TransactionRequest, U256, H160,
};
use ethers_signers::{LocalWallet, Signer};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use std::str::FromStr;

/// Signs an EIP-1559 (Type 2) or Legacy (Type 0) transaction.
#[pyfunction]
fn sign_transaction(py: Python, tx_dict: &PyDict, private_key: &str) -> PyResult<PyObject> {
    let wallet = LocalWallet::from_str(private_key).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid private key: {}", e))
    })?;

    let tx: TypedTransaction = if tx_dict.contains("maxFeePerGas")? {
        // EIP-1559 Transaction
        let mut eip1559_tx = Eip1559TransactionRequest::new();
        if let Ok(Some(to)) = tx_dict.get_item("to") { eip1559_tx = eip1559_tx.to(H160::from_str(to.extract::<&str>()?).unwrap()); }
        if let Ok(Some(value)) = tx_dict.get_item("value") { eip1559_tx = eip1559_tx.value(U256::from_dec_str(value.to_string().as_str()).unwrap()); }
        if let Ok(Some(nonce)) = tx_dict.get_item("nonce") { eip1559_tx = eip1559_tx.nonce(nonce.extract::<u64>()?); }
        if let Ok(Some(gas)) = tx_dict.get_item("gas") { eip1559_tx = eip1559_tx.gas(U256::from(gas.extract::<u64>()?)); }
        if let Ok(Some(data)) = tx_dict.get_item("data") {
            let data_str: &str = data.extract()?;
            eip1559_tx = eip1559_tx.data(hex::decode(data_str.strip_prefix("0x").unwrap_or(data_str)).unwrap());
        }
        if let Ok(Some(chain_id)) = tx_dict.get_item("chainId") { eip1559_tx = eip1559_tx.chain_id(chain_id.extract::<u64>()?); }
        if let Ok(Some(max_fee)) = tx_dict.get_item("maxFeePerGas") { eip1559_tx = eip1559_tx.max_fee_per_gas(U256::from_dec_str(max_fee.to_string().as_str()).unwrap()); }
        if let Ok(Some(priority_fee)) = tx_dict.get_item("maxPriorityFeePerGas") { eip1559_tx = eip1559_tx.max_priority_fee_per_gas(U256::from_dec_str(priority_fee.to_string().as_str()).unwrap()); }
        TypedTransaction::Eip1559(eip1559_tx)
    } else {
        // Legacy Transaction
        let mut legacy_tx = TransactionRequest::new();
        if let Ok(Some(to)) = tx_dict.get_item("to") { legacy_tx = legacy_tx.to(H160::from_str(to.extract::<&str>()?).unwrap()); }
        if let Ok(Some(value)) = tx_dict.get_item("value") { legacy_tx = legacy_tx.value(U256::from_dec_str(value.to_string().as_str()).unwrap()); }
        if let Ok(Some(nonce)) = tx_dict.get_item("nonce") { legacy_tx = legacy_tx.nonce(nonce.extract::<u64>()?); }
        if let Ok(Some(gas)) = tx_dict.get_item("gas") { legacy_tx = legacy_tx.gas(U256::from(gas.extract::<u64>()?)); }
        if let Ok(Some(gas_price)) = tx_dict.get_item("gasPrice") { legacy_tx = legacy_tx.gas_price(U256::from_dec_str(gas_price.to_string().as_str()).unwrap()); }
        if let Ok(Some(data)) = tx_dict.get_item("data") {
            let data_str: &str = data.extract()?;
            legacy_tx = legacy_tx.data(hex::decode(data_str.strip_prefix("0x").unwrap_or(data_str)).unwrap());
        }
        if let Ok(Some(chain_id)) = tx_dict.get_item("chainId") { legacy_tx = legacy_tx.chain_id(chain_id.extract::<u64>()?); }
        TypedTransaction::Legacy(legacy_tx)
    };

    let signature = py.allow_threads(|| wallet.sign_transaction_sync(&tx).unwrap());

    let raw_tx = tx.rlp_signed(&signature);
    let tx_hash = tx.hash(&signature);

    let result = PyDict::new(py);
    result.set_item("rawTransaction", PyBytes::new(py, &raw_tx))?;
    result.set_item("hash", PyBytes::new(py, tx_hash.as_bytes()))?;

    let mut r_bytes = [0u8; 32];
    signature.r.to_big_endian(&mut r_bytes);
    result.set_item("r", PyBytes::new(py, &r_bytes))?;

    let mut s_bytes = [0u8; 32];
    signature.s.to_big_endian(&mut s_bytes);
    result.set_item("s", PyBytes::new(py, &s_bytes))?;

    result.set_item("v", signature.v)?;

    Ok(result.into())
}

#[pymodule]
fn ferrite(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sign_transaction, m)?)?;
    Ok(())
}