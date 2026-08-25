"""
BL4S QDC / Scintillator / Cherenkov Physics Analysis
Publication-quality Particle ID dashboard for the CERN BL4S experiment.
Generates: individual spectra, Cherenkov vs Calorimeter 2D PID, S2 vs S3 correlation.
Usage: python3 analyze_h5_qdc.py path/to/run.h5
"""

import sys
import os
import struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
import h5py

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.edgecolor": "#cccccc",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

CERN_BLUE = "#003087"
CH_COLORS = {
    "S2":   "#003087",  # CERN blue
    "S3":   "#0067b1",
    "CALO": "#e6383a",  # Red
    "C0":   "#8B00D6",  # Purple
    "C1":   "#CC6600",  # Orange
}

# ── Input ─────────────────────────────────────────────────────────────────────
print("=== BL4S Constellation — QDC / Particle Identification Analysis ===")
if len(sys.argv) > 1:
    h5_path = sys.argv[1].strip().strip('"').strip("'")
else:
    h5_path = input("HDF5 file path: ").strip().strip('"').strip("'")

if not os.path.exists(h5_path):
    print(f"[ERROR] File not found: {h5_path}"); sys.exit(1)

out_dir = os.path.dirname(os.path.abspath(h5_path))
run_name = os.path.splitext(os.path.basename(h5_path))[0]

# ── Parse HDF5 ────────────────────────────────────────────────────────────────
N_CH = 32
qdc_data = {ch: [] for ch in range(N_CH)}
total_events = 0

print(f"\nReading: {h5_path}")
with h5py.File(h5_path, "r") as f:
    def visit(name, node):
        global total_events
        if not isinstance(node, h5py.Dataset): return
        if ("qdc" not in name.lower() and "mockqdc" not in name.lower()): return
        if "block" not in name.lower(): return
        raw = node[:].tobytes()
        if len(raw) != N_CH * 2: return
        total_events += 1
        vals = struct.unpack(f"<{N_CH}H", raw)
        for ch in range(N_CH):
            qdc_data[ch].append(vals[ch])
    f.visititems(visit)

print(f"Events parsed: {total_events:,}")
if total_events == 0:
    print("[ERROR] No QDC data found in the file."); sys.exit(1)

# Convert to arrays for speed
qdc = {ch: np.array(qdc_data[ch]) for ch in range(N_CH)}

# ── Named channels (BL4S setup) ───────────────────────────────────────────────
S2 = qdc[0]    # Scintillator 2 (MIP tag for all particles)
S3 = qdc[1]    # Scintillator 3 (MIP tag)
CALO = qdc[2]  # Calorimeter front face (shower = electron/positron)
C0 = qdc[3]    # Cherenkov C0 (threshold ≈ pion/kaon, all e+/e-)
C1 = qdc[4]    # Cherenkov C1 (threshold ≈ pion only)


def stat_box(ax, data, color, extra=""):
    mu, sigma = np.mean(data), np.std(data)
    txt = f"μ = {mu:.0f}\nσ = {sigma:.0f}\nN = {len(data):,}"
    if extra:
        txt = extra + "\n" + txt
    ax.text(0.97, 0.95, txt, transform=ax.transAxes, fontsize=9,
            va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.85, ec=color, lw=1.2))


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Full PID Dashboard
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
fig.suptitle(
    f"BL4S Particle Identification Dashboard — QDC Analysis\n"
    f"Run: {run_name}  |  5 GeV mixed beam  |  Events: {total_events:,}",
    fontsize=15, fontweight="bold"
)
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.42, wspace=0.38)

# ── Row 1: Individual scintillator / Cherenkov spectra ──────────────────────
for col, (name, data, color, label, rng) in enumerate([
    ("S2 Scintillator",   S2,   CH_COLORS["S2"],   "MIP peak (all particles)", (0, 500)),
    ("S3 Scintillator",   S3,   CH_COLORS["S3"],   "MIP peak (all particles)", (0, 500)),
    ("Cherenkov C0",      C0,   CH_COLORS["C0"],   "e⁻, π⁺, K⁺ above threshold", (0, 600)),
    ("Cherenkov C1",      C1,   CH_COLORS["C1"],   "e⁻, π⁺ above threshold", (0, 600)),
]):
    ax = fig.add_subplot(gs[0, col])
    ax.hist(data, bins=80, range=rng, color=color, alpha=0.8, histtype="stepfilled")
    ax.hist(data, bins=80, range=rng, color=color, histtype="step", linewidth=1.2)
    ax.set_title(name, fontsize=11, fontweight="bold", color=color)
    ax.set_xlabel("QDC Counts")
    ax.set_ylabel("Events")
    stat_box(ax, data, color, extra=label)

# ── Row 2: Calorimeter full spectrum + S2 vs S3 + C0 vs C1 + PID summary ──
# Calorimeter spectrum
ax_calo = fig.add_subplot(gs[1, 0])
ax_calo.hist(CALO, bins=100, range=(0, 1200), color=CH_COLORS["CALO"],
             alpha=0.8, histtype="stepfilled")
ax_calo.hist(CALO, bins=100, range=(0, 1200), color=CH_COLORS["CALO"],
             histtype="step", linewidth=1.2)
ax_calo.set_title("Calorimeter (shower signal)", fontsize=11, fontweight="bold",
                  color=CH_COLORS["CALO"])
ax_calo.set_xlabel("QDC Counts")
ax_calo.set_ylabel("Events")
# Annotation: MIP region
ax_calo.axvspan(0, 200, alpha=0.12, color="blue", label="MIP region (π, K, p)")
ax_calo.axvspan(400, 1200, alpha=0.12, color="red", label="Shower region (e⁻)")
ax_calo.legend(fontsize=8)
stat_box(ax_calo, CALO, CH_COLORS["CALO"], "e⁻ shower vs hadron MIP")

# S2 vs S3 correlation
ax_s2s3 = fig.add_subplot(gs[1, 1])
h_s2s3, xb, yb = np.histogram2d(S2, S3, bins=60, range=[[0, 500], [0, 500]])
im = ax_s2s3.imshow(h_s2s3.T, origin="lower", extent=[0, 500, 0, 500],
                    cmap="Blues", norm=LogNorm(vmin=1), interpolation="nearest", aspect="equal")
plt.colorbar(im, ax=ax_s2s3, label="Events (log)", shrink=0.85)
ax_s2s3.set_title("S2 vs S3 Correlation\n(Beam uniformity check)", fontsize=11, fontweight="bold")
ax_s2s3.set_xlabel("S2 QDC Counts")
ax_s2s3.set_ylabel("S3 QDC Counts")
ax_s2s3.grid(False)
# Diagonal (S2 ≈ S3 for MIP)
lim = 500
ax_s2s3.plot([0, lim], [0, lim], "r--", linewidth=1, alpha=0.6, label="S2 = S3")
ax_s2s3.legend(fontsize=8)

# C0 vs C1 Cherenkov PID
ax_c01 = fig.add_subplot(gs[1, 2])
h_c01, xb, yb = np.histogram2d(C0, C1, bins=60, range=[[0, 600], [0, 600]])
im = ax_c01.imshow(h_c01.T, origin="lower", extent=[0, 600, 0, 600],
                   cmap="Purples", norm=LogNorm(vmin=1), interpolation="nearest", aspect="equal")
plt.colorbar(im, ax=ax_c01, label="Events (log)", shrink=0.85)
ax_c01.set_title("Cherenkov C0 vs C1\n(π/K/e⁻ separation)", fontsize=11, fontweight="bold")
ax_c01.set_xlabel("C0 QDC Counts")
ax_c01.set_ylabel("C1 QDC Counts")
ax_c01.grid(False)
# Label regions
ax_c01.text(480, 30, "K⁺", color="white", fontsize=9, fontweight="bold", ha="right")
ax_c01.text(480, 250, "π⁺", color="white", fontsize=9, fontweight="bold", ha="right")
ax_c01.text(30, 480, "e⁻/e⁺", color="white", fontsize=9, fontweight="bold")

# Cherenkov occupancy bar chart (fraction of events with signal > threshold)
ax_pid_sum = fig.add_subplot(gs[1, 3])
THRESH = 50
frac_c0 = (C0 > THRESH).sum() / len(C0) * 100
frac_c1 = (C1 > THRESH).sum() / len(C1) * 100
frac_both = ((C0 > THRESH) & (C1 > THRESH)).sum() / len(C0) * 100
frac_none = ((C0 <= THRESH) & (C1 <= THRESH)).sum() / len(C0) * 100
labels = ["C0 only\n(K⁺-like)", "C1 only\n(p-like)", "C0 + C1\n(π⁺, e⁻)", "No Cher.\n(p, K below)"]
vals = [frac_c0 - frac_both, max(frac_c1 - frac_both, 0), frac_both, frac_none]
colors_bar = [CH_COLORS["C0"], "#009966", "#CC00CC", "#888888"]
bars = ax_pid_sum.bar(labels, vals, color=colors_bar, alpha=0.85, linewidth=0)
for bar, v in zip(bars, vals):
    ax_pid_sum.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f"{v:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax_pid_sum.set_title(f"Cherenkov Tag Occupancy\n(threshold > {THRESH} counts)", fontsize=11, fontweight="bold")
ax_pid_sum.set_ylabel("Fraction of Events [%]")
ax_pid_sum.set_ylim(0, max(vals) * 1.25)

# ── Row 3: Primary PID: Calorimeter vs Cherenkov C0 (best electron ID) ──────
ax_big = fig.add_subplot(gs[2, :2])
h_pid, xb, yb = np.histogram2d(CALO, C0, bins=[80, 60], range=[[0, 1200], [0, 600]])
im_big = ax_big.imshow(h_pid.T, origin="lower", extent=[0, 1200, 0, 600],
                       cmap="viridis", norm=LogNorm(vmin=1), interpolation="nearest", aspect="auto")
plt.colorbar(im_big, ax=ax_big, label="Events (log scale)", shrink=0.85)
ax_big.set_title("PRIMARY PID PLANE: Calorimeter vs Cherenkov C0\n"
                 "(Electrons: high CALO + high C0 | Pions: low CALO + mid C0 | Kaons: low CALO + low C0)",
                 fontsize=12, fontweight="bold")
ax_big.set_xlabel("Calorimeter QDC Counts  →  [Hadron MIP | Electron Shower]")
ax_big.set_ylabel("Cherenkov C0 QDC Counts")
ax_big.grid(False)
# Region labels
ax_big.text(1100, 550, "e⁻/e⁺", color="white", fontsize=12, fontweight="bold", ha="right")
ax_big.text(1100, 50,  "e⁻ (no Cher.)", color="yellow", fontsize=9, ha="right")
ax_big.text(80,   400, "π⁺", color="white", fontsize=12, fontweight="bold")
ax_big.text(80,   100, "K⁺/p", color="cyan", fontsize=12, fontweight="bold")
ax_big.axvline(300, color="white", linestyle="--", linewidth=1, alpha=0.6, label="MIP/Shower boundary")
ax_big.axhline(100, color="yellow", linestyle="--", linewidth=1, alpha=0.6, label="Cherenkov threshold")
ax_big.legend(fontsize=9, loc="upper left")

# S2 vs Calorimeter
ax_s2calo = fig.add_subplot(gs[2, 2:])
h_s2c, xb, yb = np.histogram2d(S2, CALO, bins=[60, 80], range=[[0, 500], [0, 1200]])
im_sc = ax_s2calo.imshow(h_s2c.T, origin="lower", extent=[0, 500, 0, 1200],
                          cmap="magma", norm=LogNorm(vmin=1), interpolation="nearest", aspect="auto")
plt.colorbar(im_sc, ax=ax_s2calo, label="Events (log scale)", shrink=0.85)
ax_s2calo.set_title("S2 Scintillator vs Calorimeter\n(Beam flux normalization cross-check)",
                    fontsize=12, fontweight="bold")
ax_s2calo.set_xlabel("S2 QDC Counts  →  Beam rate")
ax_s2calo.set_ylabel("Calorimeter QDC  →  Shower energy")
ax_s2calo.grid(False)

fig.text(0.99, 0.01, "BL4S @ CERN PS T9 | Constellation DAQ | PionIST-3",
         ha="right", va="bottom", fontsize=8, color="gray", style="italic")

path = os.path.join(out_dir, f"{run_name}_qdc_pid_dashboard.png")
fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {path}")

print(f"\n=== QDC/PID Analysis Complete | {total_events:,} events ===")
