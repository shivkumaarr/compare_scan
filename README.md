# Nmap vs RustScan Comparison Tool

A small Python utility that runs **Nmap** and **RustScan** against the same
target, measures scan duration, compares the open ports each tool detects,
and generates a graphical (PNG) report.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ⚠️ Legal / Ethical Notice

**Only scan systems and networks that you own or have explicit written
permission to test.** Port scanning systems without authorization is
illegal in many countries (e.g. under the U.S. Computer Fraud and Abuse
Act, or equivalent laws elsewhere) and may violate your ISP's or cloud
provider's terms of service.

This tool includes a mandatory `--i-have-authorization` flag as a
safety reminder — you are responsible for how you use it.

## Features

- Runs a full-port Nmap scan (`-p- --open`) and a RustScan scan
- Times both scans and compares them side-by-side
- Compares which open ports were found by each tool (common / unique)
- Outputs a clean two-panel PNG chart (scan duration + port overlap)
- Pass extra arguments straight through to either tool

## Requirements

- Python 3.9+
- [Nmap](https://nmap.org/download.html) installed and on your `PATH`
- [RustScan](https://github.com/RustScan/RustScan) installed and on your `PATH`
- Python packages in `requirements.txt`

## Installation

```bash
git clone https://github.com/shivkumaarr/nmap-rustscan-compare.git
cd nmap-rustscan-compare
pip install -r requirements.txt
```

Make sure `nmap` and `rustscan` both run from your terminal:

```bash
nmap --version
rustscan --version
```

## Usage

```bash
python3 compare_scan.py <target> --i-have-authorization
```

### Example

```bash
python3 compare_scan.py 192.168.1.10 --i-have-authorization -o report.png
```

### Optional flags

| Flag                     | Description                                      |
|--------------------------|---------------------------------------------------|
| `-o, --output`           | Output PNG path (default: `comparison_report.png`) |
| `--nmap-args`            | Extra args passed to nmap (e.g. `--nmap-args -sV`) |
| `--rustscan-args`        | Extra args passed through RustScan to nmap         |
| `--i-have-authorization` | **Required.** Confirms you're authorized to scan   |

### Sample output

```
[*] Scanning 192.168.1.10 with Nmap...
    -> 6 open port(s) found in 14.32s
[*] Scanning 192.168.1.10 with RustScan...
    -> 6 open port(s) found in 2.11s

=== Summary ===
Common ports:      [22, 80, 443, 3306, 8080, 8443]
Only in Nmap:      []
Only in RustScan:  []

[+] Graphical report saved to: comparison_report.png
```

The generated PNG contains:
1. **Scan Duration** — bar chart comparing time taken by each tool
2. **Open Port Detection** — bar chart of ports found in common vs. unique to each tool

## How it works

1. Runs `nmap -p- --open <target>` and times it
2. Runs `rustscan -a <target>` (which internally uses Nmap for service
   detection) and times it
3. Parses open ports from each tool's output using a regex
4. Computes set differences (common / nmap-only / rustscan-only)
5. Renders the comparison using `matplotlib` and saves it as a PNG

## Contributing

Pull requests are welcome — ideas for future improvements:
- JSON/HTML export in addition to PNG
- UDP scan comparison
- Support for scanning multiple targets and averaging results


