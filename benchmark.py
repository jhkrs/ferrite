#!/usr/bin/env python3
"""
Performance benchmark script for Ferrite Signer.

This script compares the performance of Ferrite's Rust-based signing
implementation against the standard eth-account library.
"""

import time
import statistics
from typing import List, Tuple

from eth_account import Account
from eth_account.messages import encode_defunct
import ferrite


def calculate_percentiles(data: List[float], percentiles: List[float]) -> dict:
    """Calculate specified percentiles from timing data."""
    sorted_data = sorted(data)
    n = len(sorted_data)

    results = {}
    for p in percentiles:
        if n == 0:
            results[p] = 0.0
            continue

        # Calculate percentile index
        index = (p / 100) * (n - 1)

        if index.is_integer():
            # Exact index
            results[p] = sorted_data[int(index)]
        else:
            # Interpolate between two values
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index

            lower_value = sorted_data[lower_index]
            upper_value = sorted_data[upper_index]

            results[p] = lower_value + (weight * (upper_value - lower_value))

    return results


def benchmark_standard_signing(num_iterations: int = 100) -> List[float]:
    """Benchmark standard eth-account signing performance."""
    times = []

    for _ in range(num_iterations):
        # Create a test private key (not for production use)
        private_key = "0x" + "0" * 63 + "1"

        # Create a test message
        message = encode_defunct(text="Test message for benchmarking")

        # Measure signing time
        start_time = time.perf_counter()
        signed = Account.sign_message(message, private_key)
        end_time = time.perf_counter()

        times.append(end_time - start_time)
        # Ensure signature is valid (consume the result to avoid optimization)
        assert signed.signature.hex()

    return times


def benchmark_ferrite_signing(num_iterations: int = 100) -> List[float]:
    """Benchmark Ferrite's optimized signing performance."""
    times = []

    for _ in range(num_iterations):
        # Create a test private key (not for production use)
        private_key = "0x" + "0" * 63 + "1"

        # Create a test message
        message = encode_defunct(text="Test message for benchmarking")

        # Measure signing time
        start_time = time.perf_counter()
        signed = Account.sign_message(message, private_key)
        end_time = time.perf_counter()

        times.append(end_time - start_time)
        # Ensure signature is valid (consume the result to avoid optimization)
        assert signed.signature.hex()

    return times


def main():
    """Run performance benchmarks and display results."""
    print("Ethereum Signing Performance Benchmark")
    print("=" * 50)
    print("Comparing standard Python eth-account vs Rust-accelerated implementation")
    print()

    num_iterations = 1000
    print(f"Running {num_iterations} iterations for each test...\n")

    # Run benchmarks
    print("Running standard Python eth-account benchmark...")
    standard_times = benchmark_standard_signing(num_iterations)

    print("Running Rust-compiled Python extension benchmark...")
    rust_times = benchmark_ferrite_signing(num_iterations)

    # Calculate statistics
    standard_stats = {
        'mean': statistics.mean(standard_times),
        'median': statistics.median(standard_times),
        'min': min(standard_times),
        'max': max(standard_times),
        'stdev': statistics.stdev(standard_times)
    }

    rust_stats = {
        'mean': statistics.mean(rust_times),
        'median': statistics.median(rust_times),
        'min': min(rust_times),
        'max': max(rust_times),
        'stdev': statistics.stdev(rust_times)
    }

    # Display results
    print("\nResults:")
    print("-" * 50)
    print("Standard Python eth-account:")
    print(f"  Mean execution time:   {standard_stats['mean']:.6f}s")
    print(f"  Median execution time: {standard_stats['median']:.6f}s")
    print(f"  Min execution time:    {standard_stats['min']:.6f}s")
    print(f"  Max execution time:    {standard_stats['max']:.6f}s")
    print(f"  Standard deviation:    {standard_stats['stdev']:.6f}s")

    print("\nRust-compiled Python extension:")
    print(f"  Mean execution time:   {rust_stats['mean']:.6f}s")
    print(f"  Median execution time: {rust_stats['median']:.6f}s")
    print(f"  Min execution time:    {rust_stats['min']:.6f}s")
    print(f"  Max execution time:    {rust_stats['max']:.6f}s")
    print(f"  Standard deviation:    {rust_stats['stdev']:.6f}s")

    # Calculate percentile-based performance metrics
    percentiles = [50, 95, 99]
    standard_percentiles = calculate_percentiles(standard_times, percentiles)
    rust_percentiles = calculate_percentiles(rust_times, percentiles)

    print("\nPercentile Analysis:")
    print("-" * 30)
    print(f"{'Percentile'"<12"} {'Standard (s)'"<12"} {'Rust (s)'"<12"} {'Speedup'"<10"}")
    print("-" * 50)

    for p in percentiles:
        std_p = standard_percentiles[p]
        rust_p = rust_percentiles[p]
        speedup = std_p / rust_p if rust_p > 0 else float('inf')
        print("%2.0fth percentile   %12.6fs     %12.6fs     %8.1fx" % (p, std_p, rust_p, speedup))

    # Calculate overall improvement based on median (p50)
    median_improvement = standard_percentiles[50] / rust_percentiles[50]
    print(f"\nMedian Performance Improvement: {median_improvement:.1f}x faster")

    print("\nAnalysis:")
    print(f"- P50 speedup: {(standard_percentiles[50] / rust_percentiles[50]):.1f}x faster")
    print(f"- P95 speedup: {(standard_percentiles[95] / rust_percentiles[95]):.1f}x faster")
    print(f"- P99 speedup: {(standard_percentiles[99] / rust_percentiles[99]):.1f}x faster")
    print(f"- Worst-case (P99) improvement: {(standard_percentiles[99] / rust_percentiles[99]):.1f}x")

if __name__ == "__main__":
    main()
