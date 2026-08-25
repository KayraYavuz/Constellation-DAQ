"""
BL4S Calorimeter Data Analysis
Publication-quality plots for the CERN BL4S experiment.
Generates: energy spectrum (all channels), 4x4 heatmap, timing distribution.
Usage: python3 analyze_h5_calorimeter.py path/to/run.h5
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
    "axes.titlesize": 13,
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
ACCENT_COLORS = [
    "#003087", "#0067b1", "#e6383a", "#f7941d",
    "#4daf4a", "#984ea3", "#a65628", "#f781bf",
    "#377eb8", "#ff7f00", "#e41a1c", "#4daf4a",
    "#999999", "#a6cee3", "#fdbf6f", "#b2df8a",
]

# ── Input ─────────────────────────────────────────────────────────────────────
print("=== BL4S Constellation — Calorimeter Data Analysis ===")
if len(sys.argv) > 1:
    h5_path = sys.argv[1].strip().strip('"').strip("'")
else:
    h5_path = input("HDF5 file path: ").strip().strip('"').strip("'")

if not os.path.exists(h5_path):
    print(f"[ERROR] File not found: {h5_path}"); sys.exit(1)

out_dir = os.path.dirname(os.path.abspath(h5_path))
run_name = os.path.splitext(os.path.basename(h5_path))[0]

# ── Parse HDF5 ────────────────────────────────────────────────────────────────
N_CH = 16
amplitudes = {ch: [] for ch in range(N_CH)}
num_hits   = {ch: [] for ch in range(N_CH)}
times      = {ch: [] for ch in range(N_CH)}
total_events = 0

print(f"\nReading: {h5_path}")
with h5py.File(h5_path, "r") as f:
    def visit(name, node):
        global total_events
        if not isinstance(node, h5py.Dataset): return
        if ("calorimeter" not in name.lower() and "mockcalorimeter" not in name.lower()): return
        if "block" not in name.lower(): return
        raw = node[:].tobytes()
        if len(raw) != N_CH * 8: return
        total_events += 1
        for ch in range(N_CH):
            o = ch * 8
            amp, n, t = struct.unpack("<H B x f", raw[o:o+8])
            amplitudes[ch].append(amp)
            num_hits[ch].append(n)
            times[ch].append(t)
    f.visititems(visit)

print(f"Events parsed: {total_events:,}")
if total_events == 0:
    print("[ERROR] No calorimeter data found. Check file format."); sys.exit(1)

# ── Total energy per channel (mean) for heatmap ───────────────────────────────
mean_amp = np.array([np.mean(amplitudes[ch]) if amplitudes[ch] else 0 for ch in range(N_CH)])
total_amp = np.array([np.sum(amplitudes[ch]) if amplitudes[ch] else 0 for ch in range(N_CH)])
heatmap = total_amp.reshape(4, 4)


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Energy Spectra — All 16 Channels (4×4 grid)
# ══════════════════════════════════════════════════════════════════════════════
fig1, axes = plt.subplots(4, 4, figsize=(20, 14))
fig1.suptitle(
    f"BL4S Lead-Glass Calorimeter — Energy Spectra per Crystal\n"
    f"Run: {run_name}  |  Total events: {total_events:,}",
    fontsize=14, fontweight="bold", y=1.01
)
axes = axes.flatten()

for ch in range(N_CH):
    ax = axes[ch]
    data = np.array(amplitudes[ch])
    color = ACCENT_COLORS[ch]

    counts, edges = np.histogram(data, bins=80, range=(0, 6500))
    centers = (edges[:-1] + edges[1:]) / 2
    ax.bar(centers, counts, width=edges[1]-edges[0], color=color, alpha=0.75, linewidth=0)
    ax.step(centers, counts, color=color, linewidth=0.8, alpha=0.9)

    # Statistics box
    stats = (f"μ = {np.mean(data):.0f}\n"
             f"σ = {np.std(data):.0f}\n"
             f"N = {len(data):,}")
    ax.text(0.97, 0.95, stats, transform=ax.transAxes,
            fontsize=7.5, va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec=color, lw=0.8))

    ax.set_title(f"Crystal {ch:02d}", fontsize=10, fontweight="bold", color=color)
    ax.set_xlabel("ADC Counts", fontsize=8)
    ax.set_ylabel("Events", fontsize=8)
    ax.set_xlim(0, 6500)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x/1000)}k" if x >= 1000 else str(int(x))))

plt.tight_layout()
path1 = os.path.join(out_dir, f"{run_name}_calorimeter_spectra.png")
fig1.savefig(path1, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig1)
print(f"Saved: {path1}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: 4×4 Energy Heatmap + Timing + Hits/Event Summary Dashboard
# ══════════════════════════════════════════════════════════════════════════════
fig2 = plt.figure(figsize=(18, 10))
fig2.suptitle(
    f"BL4S Calorimeter — Detector Summary Dashboard\n"
    f"Run: {run_name}  |  Events: {total_events:,}",
    fontsize=14, fontweight="bold"
)
gs = gridspec.GridSpec(2, 3, figure=fig2, hspace=0.38, wspace=0.35)

# Left: 4×4 Heatmap
ax_heat = fig2.add_subplot(gs[:, 0])
im = ax_heat.imshow(heatmap, cmap="YlOrRd", interpolation="nearest", aspect="auto")
cbar = plt.colorbar(im, ax=ax_heat, shrink=0.85, label="Total ADC Counts")
cbar.ax.tick_params(labelsize=9)
for row in range(4):
    for col in range(4):
        ch = row * 4 + col
        val = heatmap[row, col]
        ax_heat.text(col, row, f"C{ch:02d}\n{val/1e6:.1f}M",
                     ha="center", va="center", fontsize=8,
                     color="white" if val > heatmap.max() * 0.6 else "black",
                     fontweight="bold")
ax_heat.set_title("4×4 Crystal Energy Map\n(Total ADC Counts)", fontsize=12, fontweight="bold")
ax_heat.set_xticks(range(4)); ax_heat.set_xticklabels(["Col 0", "Col 1", "Col 2", "Col 3"], fontsize=9)
ax_heat.set_yticks(range(4)); ax_heat.set_yticklabels(["Row 0", "Row 1", "Row 2", "Row 3"], fontsize=9)
ax_heat.grid(False)

# Top-middle: Summed energy spectrum (all crystals)
ax_sum = fig2.add_subplot(gs[0, 1])
all_amps = np.array([a for ch in range(N_CH) for a in amplitudes[ch]])
ax_sum.hist(all_amps, bins=100, range=(0, 6500),
            color=CERN_BLUE, alpha=0.8, histtype="stepfilled")
ax_sum.set_title("Total Calorimeter Energy Spectrum", fontsize=11, fontweight="bold")
ax_sum.set_xlabel("ADC Counts (summed all 16 crystals)")
ax_sum.set_ylabel("Events")
ax_sum.text(0.97, 0.95,
            f"μ = {np.mean(all_amps):.0f} ADC\nσ = {np.std(all_amps):.0f} ADC",
            transform=ax_sum.transAxes, fontsize=9, va="top", ha="right",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec=CERN_BLUE))

# Bottom-middle: Mean energy per crystal bar chart
ax_bar = fig2.add_subplot(gs[1, 1])
bars = ax_bar.bar(range(N_CH), mean_amp, color=ACCENT_COLORS, alpha=0.85, linewidth=0)
ax_bar.set_title("Mean Energy per Crystal", fontsize=11, fontweight="bold")
ax_bar.set_xlabel("Crystal ID")
ax_bar.set_ylabel("Mean ADC Counts")
ax_bar.set_xticks(range(N_CH))
ax_bar.set_xticklabels([f"C{i:02d}" for i in range(N_CH)], rotation=45, fontsize=8)
ax_bar.axhline(np.mean(mean_amp), color="red", linestyle="--", linewidth=1.2, label=f"Mean = {np.mean(mean_amp):.0f}")
ax_bar.legend(fontsize=9)

# Top-right: Hits per event distribution
ax_hits = fig2.add_subplot(gs[0, 2])
all_hits = np.array([n for ch in range(N_CH) for n in num_hits[ch]])
ax_hits.hist(all_hits, bins=range(0, 8), color="#e6383a", alpha=0.8,
             histtype="stepfilled", align="left", rwidth=0.7)
ax_hits.set_title("Hits per Crystal per Event", fontsize=11, fontweight="bold")
ax_hits.set_xlabel("# Hits")
ax_hits.set_ylabel("Count")
ax_hits.set_xticks(range(7))
mode_hits = int(np.bincount(all_hits.astype(int)).argmax())
ax_hits.text(0.97, 0.95, f"Mode = {mode_hits} hits",
             transform=ax_hits.transAxes, fontsize=9, va="top", ha="right",
             bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#e6383a"))

# Bottom-right: Timing distribution (Ch 0 representative)
ax_time = fig2.add_subplot(gs[1, 2])
all_times = np.array([t for ch in range(N_CH) for t in times[ch]])
ax_time.hist(all_times, bins=80, color="#4daf4a", alpha=0.8, histtype="stepfilled")
ax_time.set_title("Crystal Timing Distribution", fontsize=11, fontweight="bold")
ax_time.set_xlabel("Time [ns]")
ax_time.set_ylabel("Events")
ax_time.text(0.97, 0.95,
             f"μ = {np.mean(all_times):.1f} ns\nσ = {np.std(all_times):.1f} ns",
             transform=ax_time.transAxes, fontsize=9, va="top", ha="right",
             bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#4daf4a"))

# Watermark
fig2.text(0.99, 0.01, "BL4S @ CERN PS T9 | Constellation DAQ | PionIST-3",
          ha="right", va="bottom", fontsize=8, color="gray", style="italic")

path2 = os.path.join(out_dir, f"{run_name}_calorimeter_dashboard.png")
fig2.savefig(path2, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig2)
print(f"Saved: {path2}")

print(f"\n=== Calorimeter Analysis Complete | {total_events:,} events processed ===")
