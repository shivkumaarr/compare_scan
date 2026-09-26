#!/usr/bin/env python3
"""
compare_scan.py
Compare Nmap vs RustScan on speed and detected open ports, and generate
a graphical (PNG) comparison report.

IMPORTANT: Only scan targets you own or are explicitly authorized to test.
Unauthorized scanning of systems/networks is illegal in most jurisdictions.
"""

import argparse
import re
import subprocess
import sys
import time

import matplotlib

matplotlib.use("Agg")  # headless-safe backend
import matplotlib.pyplot as plt


def check_tool_installed(tool_name: str) -> bool:
    from shutil import which

    return which(tool_name) is not None


def run_nmap(target: str, extra_args: list[str]) -> tuple[float, set[int], str]:
    cmd = ["nmap", "-p-", "--open"] + extra_args + [target]
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    ports = {int(p) for p in re.findall(r"^(\d+)/tcp\s+open", result.stdout, re.MULTILINE)}
    return elapsed, ports, result.stdout


def run_rustscan(target: str, extra_args: list[str]) -> tuple[float, set[int], str]:
    cmd = ["rustscan", "-a", target] + (["--", *extra_args] if extra_args else [])
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    ports = {int(p) for p in re.findall(r"^(\d+)/tcp\s+open", result.stdout, re.MULTILINE)}
    return elapsed, ports, result.stdout


def build_report(target, nmap_time, nmap_ports, rust_time, rust_ports, output_path):
    common = nmap_ports & rust_ports
    only_nmap = nmap_ports - rust_ports
    only_rust = rust_ports - nmap_ports

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Nmap vs RustScan — target: {target}", fontsize=13)

    # Chart 1: scan duration
    axes[0].bar(["Nmap", "RustScan"], [nmap_time, rust_time], color=["#1f77b4", "#ff7f0e"])
    axes[0].set_ylabel("Time (seconds)")
    axes[0].set_title("Scan Duration")
    for i, v in enumerate([nmap_time, rust_time]):
        axes[0].text(i, v, f"{v:.2f}s", ha="center", va="bottom")

    # Chart 2: port overlap
    labels = ["Common", "Only Nmap", "Only RustScan"]
    values = [len(common), len(only_nmap), len(only_rust)]
    axes[1].bar(labels, values, color=["#2ca02c", "#1f77b4", "#ff7f0e"])
    axes[1].set_ylabel("Number of Ports")
    axes[1].set_title("Open Port Detection")
    for i, v in enumerate(values):
        axes[1].text(i, v, str(v), ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return common, only_nmap, only_rust


def main():
    parser = argparse.ArgumentParser(
        description="Compare Nmap and RustScan speed + results on an authorized target."
    )
    parser.add_argument("target", help="IP address or hostname you are authorized to scan")
    parser.add_argument(
        "-o", "--output", default="comparison_report.png", help="Output PNG file path"
    )
    parser.add_argument(
        "--nmap-args", nargs="*", default=[], help="Extra args passed to nmap (e.g. -sV)"
    )
    parser.add_argument(
        "--rustscan-args", nargs="*", default=[], help="Extra args passed to nmap via rustscan"
    )
    parser.add_argument(
        "--i-have-authorization",
        action="store_true",
        help="Confirm you are authorized to scan this target (required to proceed)",
    )
    args = parser.parse_args()

    if not args.i_have_authorization:
        print(
            "[!] You must pass --i-have-authorization to confirm you own or are "
            "explicitly permitted to scan this target. Aborting.",
            file=sys.stderr,
        )
        sys.exit(1)

    missing = [t for t in ("nmap", "rustscan") if not check_tool_installed(t)]
    if missing:
        print(f"[!] Missing required tool(s): {', '.join(missing)}. Install them first.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Scanning {args.target} with Nmap...")
    nmap_time, nmap_ports, _ = run_nmap(args.target, args.nmap_args)
    print(f"    -> {len(nmap_ports)} open port(s) found in {nmap_time:.2f}s")

    print(f"[*] Scanning {args.target} with RustScan...")
    rust_time, rust_ports, _ = run_rustscan(args.target, args.rustscan_args)
    print(f"    -> {len(rust_ports)} open port(s) found in {rust_time:.2f}s")

    common, only_nmap, only_rust = build_report(
        args.target, nmap_time, nmap_ports, rust_time, rust_ports, args.output
    )

    print("\n=== Summary ===")
    print(f"Common ports:      {sorted(common)}")
    print(f"Only in Nmap:      {sorted(only_nmap)}")
    print(f"Only in RustScan:  {sorted(only_rust)}")
    print(f"\n[+] Graphical report saved to: {args.output}")


if __name__ == "__main__":
    main()
