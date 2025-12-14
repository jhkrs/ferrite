import time
import numpy as np
from eth_account import Account
from eth_account.account import LocalAccount
from eth_account.messages import encode_defunct
import ferrite

# --- Configuration ---
NUM_SAMPLES = 1000
WARMUP_RUNS = 100
KEY = "0x0000000000000000000000000000000000000000000000000000000000000001"
MESSAGE = encode_defunct(text="The quick brown fox jumps over the lazy dog")
MESSAGE_HASH = Account.sign_message(MESSAGE, KEY).message_hash

# --- Benchmark Setup ---


def get_original_signer():
    """
    Temporarily unpatch to get the original signing method.
    """
    import eth_account.account

    return eth_account.account.LocalAccount._sign_hash


def benchmark_function(func, *args):
    """Measures execution time of a function."""
    start = time.perf_counter()
    func(*args)
    end = time.perf_counter()
    return (end - start) * 1000  # Return time in milliseconds


def run_bench(name, target_func, *args):
    """Run warmup and sample collection for a given function."""
    print(f"\nRunning benchmark for: {name}")

    # Warm-up runs
    for _ in range(WARMUP_RUNS):
        target_func(*args)

    # Collect samples
    timings = [benchmark_function(target_func, *args) for _ in range(NUM_SAMPLES)]

    p50 = np.percentile(timings, 50)
    p95 = np.percentile(timings, 95)
    p99 = np.percentile(timings, 99)

    print(f"  P50 (Median): {p50:.4f} ms")
    print(f"  P95: {p95:.4f} ms")
    print(f"  P99: {p99:.4f} ms")

    return {"p50": p50, "p95": p95, "p99": p99}


def benchmark_sign_hash(message_hash, private_key):
    """Benchmark function for signHash operation."""
    return Account._sign_hash(message_hash, private_key)


# --- Main Execution ---

if __name__ == "__main__":
    # 1. Benchmark original eth-account (before patching)
    eth_account_results = run_bench(
        "Original eth-account", benchmark_sign_hash, MESSAGE_HASH, KEY
    )

    # 2. Benchmark ferrite-patched eth-account (after patching)
    ferrite.install()
    ferrite_results = run_bench(
        "Ferrite (Rust-accelerated)", benchmark_sign_hash, MESSAGE_HASH, KEY
    )

    # 3. Report improvements
    print("\n--- Performance Improvements (Ferrite vs. eth-account) ---")

    p50_improvement = eth_account_results["p50"] / ferrite_results["p50"]
    p95_improvement = eth_account_results["p95"] / ferrite_results["p95"]
    p99_improvement = eth_account_results["p99"] / ferrite_results["p99"]

    print(f"  P50 (Median) Improvement: {p50_improvement:.2f}x faster")
    print(f"  P95 Improvement: {p95_improvement:.2f}x faster")
    print(f"  P99 Improvement: {p99_improvement:.2f}x faster")
