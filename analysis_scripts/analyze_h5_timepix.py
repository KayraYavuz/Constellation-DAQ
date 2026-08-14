import h5py
import numpy as np
import matplotlib.pyplot as plt
import os
import struct

print("=== Constellation BL4S - HDF5 TimePix Data Analysis ===")

h5_file_path = input("Lütfen HDF5 dosyasının yolunu girin (ör. /Users/kayrayavuz/Desktop/DATA/run_11.h5): ").strip()
if not os.path.exists(h5_file_path):
    print(f"Hata: {h5_file_path} bulunamadı!")
    exit(1)

output_dir = os.path.dirname(h5_file_path)

# Verileri tutacağımız listeler
hits_per_event = []
x_vals, y_vals = [], []
pix_vals = []
ftoa_vals = []
tot_vals = []
ts_low_vals, ts_high_vals = [], []
toa14_vals = []
time_ns_vals = []

print(f"\n--- Reading HDF5 File: {h5_file_path} ---")

with h5py.File(h5_file_path, "r") as f:
    total_events = 0
    total_hits = 0
    
    def process_node(name, node):
        global total_events, total_hits
        if isinstance(node, h5py.Dataset):
            if ("mocktimepix" in name.lower() or "timepix" in name.lower()) and "block" in name.lower():
                data = node[:]
                raw_bytes = data.tobytes()
                # Her hit 16 byte: <B B B x H x x I I
                event_hits = len(raw_bytes) // 16
                hits_per_event.append(event_hits)
                total_events += 1
                total_hits += event_hits
                
                for i in range(event_hits):
                    offset = i * 16
                    hit_data = raw_bytes[offset:offset+16]
                    x, y, ftoa, tot, toa_low, toa_high = struct.unpack('<B B B x H x x I I', hit_data)
                    
                    x_vals.append(x)
                    y_vals.append(y)
                    pix_vals.append(x + 256 * y)
                    ftoa_vals.append(ftoa)
                    tot_vals.append(tot)
                    ts_low_vals.append(toa_low)
                    ts_high_vals.append(toa_high)
                    
                    # TOA14 ve Time ns hesaplamaları
                    ts_full = (toa_high << 32) | toa_low
                    toa14 = ts_full % 16384
                    toa14_vals.append(toa14)
                    time_ns_vals.append(toa14 * 25.0 - ftoa * 1.5625)

    f.visititems(process_node)

print(f"Processed {total_events} events with a total of {total_hits} TimePix hits.")

if total_hits == 0:
    print("No TimePix data found in the file or format mismatch.")
    exit(1)

print("\n--- Generating Plots ---")

fig = plt.figure(figsize=(18, 12))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. 2D Hitmap (X vs Y)
ax1 = plt.subplot(2, 3, 1)
h2d, xedges, yedges = np.histogram2d(x_vals, y_vals, bins=256, range=[[0, 256], [0, 256]])
im = ax1.imshow(h2d.T, origin='lower', extent=[0, 256, 0, 256], cmap='viridis', interpolation='nearest')
ax1.set_title("TimePix Hitmap", fontweight='bold')
ax1.set_xlabel("X Pixel")
ax1.set_ylabel("Y Pixel")
plt.colorbar(im, ax=ax1, label="Hits")

# 2. X Profile
ax2 = plt.subplot(2, 3, 2)
ax2.hist(x_vals, bins=256, range=(0, 256), color="#1f77b4", histtype="step")
ax2.set_title("X Profile", fontweight='bold')
ax2.set_xlabel("X Pixel")

# 3. Y Profile
ax3 = plt.subplot(2, 3, 3)
ax3.hist(y_vals, bins=256, range=(0, 256), color="#ff7f0e", histtype="step")
ax3.set_title("Y Profile", fontweight='bold')
ax3.set_xlabel("Y Pixel")

# 4. Number of Hits per Event
ax4 = plt.subplot(2, 3, 4)
ax4.hist(hits_per_event, bins=50, range=(0, 100), color="#2ca02c")
ax4.set_title("Hits per Event", fontweight='bold')
ax4.set_xlabel("# Hits")

# 5. Time over Threshold (ToT)
ax5 = plt.subplot(2, 3, 5)
ax5.hist(tot_vals, bins=100, range=(0, 4096), color="#d62728")
ax5.set_title("Time over Threshold (ToT)", fontweight='bold')
ax5.set_xlabel("ToT (counts)")

# 6. Time within 14-bit wrap (ns)
ax6 = plt.subplot(2, 3, 6)
ax6.hist(time_ns_vals, bins=100, color="#9467bd")
ax6.set_title("Time within 14-bit wrap (ns)", fontweight='bold')
ax6.set_xlabel("Time (ns)")

plt.tight_layout()
timepix_plot_path = os.path.join(output_dir, "timepix_dashboard.png")
plt.savefig(timepix_plot_path, dpi=200)
plt.close()

print(f"Saved TimePix Dashboard to: {timepix_plot_path}")
print("=== Data Analysis Completed Successfully! ===")
