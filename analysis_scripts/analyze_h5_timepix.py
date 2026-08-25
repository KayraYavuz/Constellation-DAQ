"""
BL4S TimePix Pixel Detector Data Analysis
Publication-quality plots for the CERN BL4S experiment.
Generates: 2D hitmap, X/Y profiles, ToT spectrum, timing, cluster size.
Usage: python3 analyze_h5_timepix.py path/to/run.h5
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

# ── Input ─────────────────────────────────────────────────────────────────────
print("=== BL4S Constellation — TimePix Pixel Detector Analysis ===")
if len(sys.argv) > 1:
    h5_path = sys.argv[1].strip().strip('"').strip("'")
else:
    h5_path = input("HDF5 file path: ").strip().strip('"').strip("'")

if not os.path.exists(h5_path):
    print(f"[ERROR] File not found: {h5_path}"); sys.exit(1)

out_dir = os.path.dirname(os.path.abspath(h5_path))
run_name = os.path.splitext(os.path.basename(h5_path))[0]

# ── Parse HDF5 ────────────────────────────────────────────────────────────────
hits_per_event = []
x_vals, y_vals = [], []
tot_vals = []
time_ns_vals = []
total_events = 0
total_hits = 0

print(f"\nReading: {h5_path}")
with h5py.File(h5_path, "r") as f:
    def visit(name, node):
        global total_events, total_hits
        if not isinstance(node, h5py.Dataset): return
        if ("timepix" not in name.lower() and "mocktimepix" not in name.lower()): return
        if "block" not in name.lower(): return
        raw = node[:].tobytes()
        event_hits = len(raw) // 16
        if event_hits == 0: return
        hits_per_event.append(event_hits)
        total_events += 1
        total_hits += event_hits
        for i in range(event_hits):
            o = i * 16
            x, y, ftoa, tot, toa_low, toa_high = struct.unpack("<B B B x H x x I I", raw[o:o+16])
            x_vals.append(x)
            y_vals.append(y)
            tot_vals.append(tot)
            ts_full = (toa_high << 32) | toa_low
            toa14 = ts_full % 16384
            time_ns_vals.append(toa14 * 25.0 - ftoa * 1.5625)
    f.visititems(visit)

print(f"Events: {total_events:,} | Total hits: {total_hits:,} | Avg hits/event: {total_hits/max(total_events,1):.2f}")
if total_hits == 0:
    print("[ERROR] No TimePix data found."); sys.exit(1)

x_arr = np.array(x_vals)
y_arr = np.array(y_vals)
tot_arr = np.array(tot_vals)
time_arr = np.array(time_ns_vals)
hpe_arr = np.array(hits_per_event)

# 2D hitmap
h2d, xedges, yedges = np.histogram2d(x_arr, y_arr, bins=256, range=[[0,256],[0,256]])

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Spatial Dashboard — 2D Hitmap + Projections
# ══════════════════════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(16, 14))
fig1.suptitle(
    f"BL4S TimePix Pixel Detector — Spatial Hit Map\n"
    f"Run: {run_name}  |  Total Hits: {total_hits:,}  |  Events: {total_events:,}",
    fontsize=14, fontweight="bold"
)

# Use GridSpec with space for marginal plots
gs = gridspec.GridSpec(3, 3, figure=fig1, hspace=0.35, wspace=0.35,
                       width_ratios=[3, 1, 1], height_ratios=[3, 1, 1])

# Main 2D hitmap (log scale)
ax_main = fig1.add_subplot(gs[0, 0])
im = ax_main.imshow(
    h2d.T, origin="lower", extent=[0, 256, 0, 256],
    cmap="inferno", norm=LogNorm(vmin=1),
    interpolation="nearest", aspect="equal"
)
cbar = plt.colorbar(im, ax=ax_main, label="Hits (log scale)", shrink=0.9)
cbar.ax.tick_params(labelsize=9)
ax_main.set_title("2D Hit Map (log scale)", fontsize=12, fontweight="bold")
ax_main.set_xlabel("X Pixel")
ax_main.set_ylabel("Y Pixel")
ax_main.grid(False)
# Mark pixel with most hits
max_idx = np.unravel_index(h2d.argmax(), h2d.shape)
ax_main.plot(max_idx[0], max_idx[1], "w+", markersize=12, markeredgewidth=2,
             label=f"Peak ({max_idx[0]}, {max_idx[1]})")
ax_main.legend(fontsize=9, loc="upper right")

# X projection
ax_x = fig1.add_subplot(gs[1, 0])
x_proj = h2d.sum(axis=1)
ax_x.bar(range(256), x_proj, color=CERN_BLUE, alpha=0.8, linewidth=0)
ax_x.set_xlabel("X Pixel")
ax_x.set_ylabel("Total Hits")
ax_x.set_title("X Projection", fontsize=11, fontweight="bold")
ax_x.set_xlim(0, 256)
ax_x.text(0.97, 0.95, f"Peak X = {x_proj.argmax()}",
          transform=ax_x.transAxes, fontsize=9, va="top", ha="right",
          bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec=CERN_BLUE))

# Y projection
ax_y = fig1.add_subplot(gs[2, 0])
y_proj = h2d.sum(axis=0)
ax_y.bar(range(256), y_proj, color="#e6383a", alpha=0.8, linewidth=0)
ax_y.set_xlabel("Y Pixel")
ax_y.set_ylabel("Total Hits")
ax_y.set_title("Y Projection", fontsize=11, fontweight="bold")
ax_y.set_xlim(0, 256)
ax_y.text(0.97, 0.95, f"Peak Y = {y_proj.argmax()}",
          transform=ax_y.transAxes, fontsize=9, va="top", ha="right",
          bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#e6383a"))

# ToT spectrum
ax_tot = fig1.add_subplot(gs[0, 1])
ax_tot.hist(tot_arr, bins=100, range=(0, 4096), color="#f7941d", alpha=0.85, histtype="stepfilled")
ax_tot.set_title("Time over\nThreshold (ToT)", fontsize=11, fontweight="bold")
ax_tot.set_xlabel("ToT [counts]")
ax_tot.set_ylabel("Hits")
ax_tot.text(0.97, 0.95, f"μ = {np.mean(tot_arr):.0f}\nσ = {np.std(tot_arr):.0f}",
            transform=ax_tot.transAxes, fontsize=9, va="top", ha="right",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#f7941d"))

# Timing
ax_time = fig1.add_subplot(gs[1, 1])
valid_t = time_arr[np.isfinite(time_arr)]
ax_time.hist(valid_t, bins=80, color="#4daf4a", alpha=0.85, histtype="stepfilled")
ax_time.set_title("ToA Timing\nDistribution", fontsize=11, fontweight="bold")
ax_time.set_xlabel("Time [ns]")
ax_time.set_ylabel("Hits")
ax_time.text(0.97, 0.95, f"μ = {np.mean(valid_t):.1f} ns\nσ = {np.std(valid_t):.1f} ns",
             transform=ax_time.transAxes, fontsize=9, va="top", ha="right",
             bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#4daf4a"))

# Cluster size (hits per event)
ax_cls = fig1.add_subplot(gs[2, 1])
max_cluster = min(int(hpe_arr.max()) + 2, 50)
ax_cls.hist(hpe_arr, bins=range(1, max_cluster), color="#984ea3", alpha=0.85,
            histtype="stepfilled", align="left", rwidth=0.75)
ax_cls.set_title("Cluster Size\n(Hits / Event)", fontsize=11, fontweight="bold")
ax_cls.set_xlabel("Hits per Event")
ax_cls.set_ylabel("Events")
ax_cls.text(0.97, 0.95,
            f"Median = {np.median(hpe_arr):.0f}\nMax = {hpe_arr.max()}",
            transform=ax_cls.transAxes, fontsize=9, va="top", ha="right",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="#984ea3"))

# Occupancy (fraction of pixels hit ≥1)
ax_occ = fig1.add_subplot(gs[0, 2])
occupancy = (h2d > 0).sum() / (256 * 256) * 100
hot_pixels = (h2d > np.percentile(h2d[h2d > 0], 99)).sum() if h2d.sum() > 0 else 0
info_text = (
    f"Total hits: {total_hits:,}\n"
    f"Pixels hit: {int((h2d>0).sum()):,}\n"
    f"Occupancy: {occupancy:.2f}%\n"
    f"Hot pixels (>99%ile): {hot_pixels}\n"
    f"Mean hits/event: {np.mean(hpe_arr):.2f}\n"
    f"Median hits/event: {np.median(hpe_arr):.1f}\n"
    f"Events: {total_events:,}"
)
ax_occ.axis("off")
ax_occ.text(0.05, 0.95, "Run Statistics", transform=ax_occ.transAxes,
            fontsize=12, fontweight="bold", va="top", color=CERN_BLUE)
ax_occ.text(0.05, 0.78, info_text, transform=ax_occ.transAxes,
            fontsize=10, va="top", family="monospace",
            bbox=dict(boxstyle="round", fc="#eef2ff", ec=CERN_BLUE, alpha=0.9, lw=1.5))

# ToT vs Hits scatter (correlation)
ax_corr = fig1.add_subplot(gs[1:, 2])
if len(tot_arr) > 5000:
    idx = np.random.choice(len(tot_arr), 5000, replace=False)
    tot_s, hpe_s = tot_arr[idx], np.repeat(hpe_arr, hpe_arr)[idx]
else:
    tot_s = tot_arr
    hpe_s = np.repeat(hpe_arr, hpe_arr)[:len(tot_s)]

h_corr, xb, yb = np.histogram2d(tot_s, hpe_s, bins=[50, min(30, max_cluster-1)],
                                  range=[[0, 4096], [1, max_cluster]])
ax_corr.imshow(h_corr.T, origin="lower", aspect="auto",
               extent=[0, 4096, 1, max_cluster],
               cmap="Blues", interpolation="nearest")
ax_corr.set_title("ToT vs\nCluster Size", fontsize=11, fontweight="bold")
ax_corr.set_xlabel("ToT [counts]")
ax_corr.set_ylabel("Hits per Event")
ax_corr.grid(False)

fig1.text(0.99, 0.01, "BL4S @ CERN PS T9 | Constellation DAQ | PionIST-3",
          ha="right", va="bottom", fontsize=8, color="gray", style="italic")

path1 = os.path.join(out_dir, f"{run_name}_timepix_dashboard.png")
fig1.savefig(path1, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig1)
print(f"Saved: {path1}")

print(f"\n=== TimePix Analysis Complete | {total_hits:,} hits in {total_events:,} events ===")
