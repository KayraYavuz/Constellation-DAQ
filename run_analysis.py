#!/usr/bin/env python3
"""
BL4S Batch Data Analysis Runner
Runs all analysis scripts on every .h5 file in a directory (or a single file).
Usage:
  python3 run_analysis.py                        # asks for directory
  python3 run_analysis.py path/to/run.h5         # single file
  python3 run_analysis.py path/to/data_dir/      # all .h5 in directory
"""

import sys
import os
import glob
import subprocess

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_scripts")

ANALYSIS_SCRIPTS = [
    ("analyze_h5_calorimeter.py", "Calorimeter"),
    ("analyze_h5_timepix.py",     "TimePix"),
    ("analyze_h5_qdc.py",         "QDC / PID"),
]

YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner():
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  BL4S Data Analysis — Batch Runner")
    print(f"  CERN PS T9 | Constellation DAQ")
    print(f"{'='*60}{RESET}\n")

NO_DATA_MARKERS = [
    "No QDC data found", "No calorimeter data found", "No TimePix data found",
    "Events parsed: 0", "total_hits == 0", "total_events == 0",
]

def run_script(script_name, h5_file):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"  {YELLOW}[SKIP]{RESET} Script not found: {script_path}")
        return "skip"
    result = subprocess.run(
        [sys.executable, script_path, h5_file],
        capture_output=True, text=True
    )
    combined = result.stdout + result.stderr
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if "Saved:" in line or "Complete" in line:
                print(f"  {GREEN}✔{RESET}  {line.strip()}")
        return "ok"
    else:
        # Check if it's just "no data" — treat as skip, not error
        if any(marker in combined for marker in NO_DATA_MARKERS):
            print(f"  {YELLOW}—  No data in this run (detector may have been inactive){RESET}")
            return "skip"
        print(f"  {RED}✘  Failed:{RESET}")
        for line in combined.splitlines()[-5:]:
            print(f"     {line}")
        return "fail"

def analyze_file(h5_file):
    fname = os.path.basename(h5_file)
    print(f"\n{BOLD}{YELLOW}▶ {fname}{RESET}")
    print(f"  Path: {h5_file}")
    results = {}
    for script, label in ANALYSIS_SCRIPTS:
        print(f"  [{label}]", end=" ", flush=True)
        ok = run_script(script, h5_file)
        results[label] = ok
    return results

def main():
    banner()

    if len(sys.argv) > 1:
        target = sys.argv[1].strip().strip('"').strip("'")
    else:
        target = input(
            "Enter path to .h5 file or directory containing .h5 files:\n> "
        ).strip().strip('"').strip("'")

    # Determine list of h5 files
    if os.path.isfile(target) and target.endswith(".h5"):
        h5_files = [target]
    elif os.path.isdir(target):
        h5_files = sorted(glob.glob(os.path.join(target, "*.h5")))
        if not h5_files:
            print(f"{RED}No .h5 files found in: {target}{RESET}")
            sys.exit(1)
    else:
        print(f"{RED}Path not found or not a .h5 file: {target}{RESET}")
        sys.exit(1)

    print(f"Found {BOLD}{len(h5_files)}{RESET} .h5 file(s) to analyze.\n")

    all_results = {}
    for h5_file in h5_files:
        all_results[h5_file] = analyze_file(h5_file)

    # Summary table
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}{RESET}")
    total_ok = 0
    total_skip = 0
    total_fail = 0
    for h5_file, results in all_results.items():
        fname = os.path.basename(h5_file)
        ok_labels   = [l for l, r in results.items() if r == "ok"]
        skip_labels = [l for l, r in results.items() if r == "skip"]
        fail_labels = [l for l, r in results.items() if r == "fail"]
        total_ok   += len(ok_labels)
        total_skip += len(skip_labels)
        total_fail += len(fail_labels)
        if fail_labels:
            status = f"{RED}✘{RESET}"
        elif ok_labels:
            status = f"{GREEN}✔{RESET}"
        else:
            status = f"{YELLOW}—{RESET}"
        print(f"  {status} {BOLD}{fname}{RESET}")
        if ok_labels:
            print(f"     Generated: {', '.join(ok_labels)}")
        if skip_labels:
            print(f"     {YELLOW}Skipped (no data):{RESET} {', '.join(skip_labels)}")
        if fail_labels:
            print(f"     {RED}Failed:{RESET} {', '.join(fail_labels)}")
        out_dir = os.path.dirname(h5_file)
        run_name = os.path.splitext(fname)[0]
        pngs = glob.glob(os.path.join(out_dir, f"{run_name}_*.png"))
        for png in pngs:
            print(f"     → {png}")

    parts = []
    if total_ok:   parts.append(f"{GREEN}✔ {total_ok} plots generated{RESET}")
    if total_skip: parts.append(f"{YELLOW}— {total_skip} skipped (no data){RESET}")
    if total_fail: parts.append(f"{RED}✘ {total_fail} failed{RESET}")
    print(f"\n  {'  '.join(parts)}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")


if __name__ == "__main__":
    main()
