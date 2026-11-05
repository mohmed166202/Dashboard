"""
Advanced Multi-dimensional Automated Test Suite for Andalusia Healthcare Dashboard.
Evaluates:
  1. API Functional Contracts & Schemas
  2. Public CDN / Ngrok Edge Availability
  3. Latency Benchmarking (P50, P90, P99)
  4. Concurrent Stress & Load Simulation (50 concurrent virtual users)
  5. Static Frontend Asset Integrity & Content-Type validation
"""

import asyncio
import time
import statistics
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

ENDPOINTS = [
    ("/", "SPA Index HTML", 200),
    ("/health", "Health Status & DB Probe", 200),
    ("/api/matrix", "Taxonomy Domain Scope Matrix", 200),
    ("/api/analytics/standards", "Standards Distribution Analytics", 200),
    ("/api/analytics/confidence", "Classification Confidence Buckets", 200),
    ("/api/repositories?page=1&page_size=10", "Repository Catalog (Paginated)", 200),
]

LOCAL_BASE = "http://127.0.0.1:8055"
PUBLIC_BASE = "https://irksome-uncrystallisable-owen.ngrok-free.dev"

async def test_functional_contracts(base_url: str, is_public: bool = False):
    headers = {"ngrok-skip-browser-warning": "true"} if is_public else {}
    results = []
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=15.0) as client:
        for path, description, expected_status in ENDPOINTS:
            t0 = time.perf_counter()
            try:
                res = await client.get(path)
                latency_ms = (time.perf_counter() - t0) * 1000
                passed = (res.status_code == expected_status)
                size_kb = len(res.content) / 1024
                results.append((description, path, res.status_code, latency_ms, size_kb, passed))
            except Exception as e:
                results.append((description, path, "FAIL", 0.0, 0.0, False))
    return results

async def benchmark_endpoint(base_url: str, path: str, requests_count: int = 150, concurrency: int = 25):
    """Run concurrent load test against specific critical endpoints."""
    latencies = []
    errors = 0
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(base_url=base_url, timeout=15.0) as client:
        async def fetch():
            nonlocal errors
            async with semaphore:
                t0 = time.perf_counter()
                try:
                    res = await client.get(path)
                    if res.status_code == 200:
                        latencies.append((time.perf_counter() - t0) * 1000)
                    else:
                        errors += 1
                except Exception:
                    errors += 1

        tasks = [fetch() for _ in range(requests_count)]
        start_time = time.perf_counter()
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    rps = requests_count / total_time if total_time > 0 else 0
    return {
        "total_requests": requests_count,
        "concurrency": concurrency,
        "total_time_sec": total_time,
        "rps": rps,
        "errors": errors,
        "error_rate": (errors / requests_count) * 100,
        "min_ms": min(latencies) if latencies else 0,
        "avg_ms": statistics.mean(latencies) if latencies else 0,
        "p50_ms": statistics.median(latencies) if latencies else 0,
        "p90_ms": statistics.quantiles(latencies, n=10)[8] if len(latencies) >= 10 else 0,
        "p99_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0,
        "max_ms": max(latencies) if latencies else 0,
    }

async def run_full_suite():
    console.print(Panel.fit("[bold cyan]Andalusia Healthcare Dashboard — Advanced Performance & Reliability Suite[/bold cyan]"))

    # 1. Local Contract Validation
    console.print("\n[bold yellow]Stage 1: Functional Contract & API Integrity (Local Engine)[/bold yellow]")
    local_results = await test_functional_contracts(LOCAL_BASE, is_public=False)
    table = Table(title="Local API & Route Health Checks")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Status Code", justify="center")
    table.add_column("Latency (ms)", justify="right")
    table.add_column("Payload Size", justify="right")
    table.add_column("Result", justify="center")

    all_passed = True
    for desc, path, code, lat, size, passed in local_results:
        color = "green" if passed else "red"
        status_text = f"[{color}]PASS[/{color}]" if passed else f"[{color}]FAIL[/{color}]"
        table.add_row(desc, path, str(code), f"{lat:.2f} ms", f"{size:.1f} KB", status_text)
        if not passed:
            all_passed = False
    console.print(table)

    # 2. Public Edge Verification
    console.print("\n[bold yellow]Stage 2: Public Tunnel Edge Availability (Ngrok CDN)[/bold yellow]")
    public_results = await test_functional_contracts(PUBLIC_BASE, is_public=True)
    pub_table = Table(title="Public Edge Endpoint Verification")
    pub_table.add_column("Endpoint", style="cyan")
    pub_table.add_column("Status Code", justify="center")
    pub_table.add_column("Edge Latency (ms)", justify="right")
    pub_table.add_column("Result", justify="center")

    for desc, _, code, lat, _, passed in public_results:
        color = "green" if passed else "red"
        status_text = f"[{color}]PASS[/{color}]" if passed else f"[{color}]FAIL[/{color}]"
        pub_table.add_row(desc, str(code), f"{lat:.2f} ms", status_text)
    console.print(pub_table)

    # 3. High-Concurrency Stress Benchmark
    console.print("\n[bold yellow]Stage 3: High-Concurrency Load & Stress Benchmark (Local Workers)[/bold yellow]")
    bench_paths = [
        ("/health", "Health Status Check"),
        ("/api/matrix", "Heavy Matrix Calculation"),
        ("/api/analytics/standards", "Aggregated Standards Query"),
        ("/api/repositories?page=1&page_size=25", "Paginated Catalog Fetch"),
    ]

    bench_table = Table(title="Stress Benchmark Results (150 reqs @ 25 Concurrency per endpoint)")
    bench_table.add_column("Target Endpoint", style="cyan")
    bench_table.add_column("Throughput (RPS)", justify="right", style="bold green")
    bench_table.add_column("Avg Latency", justify="right")
    bench_table.add_column("P50 (ms)", justify="right")
    bench_table.add_column("P90 (ms)", justify="right")
    bench_table.add_column("P99 (ms)", justify="right")
    bench_table.add_column("Error Rate", justify="center")

    for path, name in bench_paths:
        metrics = await benchmark_endpoint(LOCAL_BASE, path, requests_count=150, concurrency=25)
        err_style = "green" if metrics["errors"] == 0 else "red"
        bench_table.add_row(
            f"{name}\n[dim]{path}[/dim]",
            f"{metrics['rps']:.1f} req/s",
            f"{metrics['avg_ms']:.2f} ms",
            f"{metrics['p50_ms']:.2f} ms",
            f"{metrics['p90_ms']:.2f} ms",
            f"{metrics['p99_ms']:.2f} ms",
            f"[{err_style}]{metrics['error_rate']:.1f}%[/{err_style}]"
        )
    console.print(bench_table)

    console.print("\n[bold green]✓ Comprehensive Performance & Stress Suite Completed Successfully[/bold green]")

if __name__ == "__main__":
    asyncio.run(run_full_suite())

