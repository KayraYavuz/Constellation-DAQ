import h5py
import numpy as np
import struct
import matplotlib.pyplot as plt
import os

def analyze_qdc_data():
    print("=== Constellation BL4S - HDF5 QDC Physics Analysis ===")
    filename = input("Lütfen HDF5 dosyasının yolunu girin (ör. /Users/kayrayavuz/Desktop/DATA/run_10.h5): ").strip()
    
    if not os.path.exists(filename):
        print(f"Error: {filename} bulunamadı.")
        return

    channels = 32
    qdc_data = {ch: [] for ch in range(channels)}
    total_events = 0

    print(f"--- Reading HDF5 File: {filename} ---")
    
    def process_node(name, node):
        nonlocal total_events
        if isinstance(node, h5py.Dataset):
            if ("mockqdc" in name.lower() or "qdc" in name.lower()) and "block" in name.lower():
                data = node[:]
                raw_bytes = data.tobytes()
                # Her kanal 2 byte: <H
                if len(raw_bytes) == channels * 2:
                    total_events += 1
                    unpacked_values = struct.unpack(f"<{channels}H", raw_bytes)
                    for ch in range(channels):
                        qdc_data[ch].append(unpacked_values[ch])

    try:
        with h5py.File(filename, 'r') as f:
            f.visititems(process_node)
    except Exception as e:
        print(f"Failed to read HDF5 file: {e}")
        return

    print(f"Processed {total_events} QDC events.")

    if total_events == 0:
        print("No QDC data found in the file or format mismatch.")
        return

    print("--- Generating Physics Plots ---")
    fig, axs = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Simulated 5 GeV Beam - Particle Identification (QDC)', fontsize=16)

    # Ch 0: S2 Scintillator
    axs[0, 0].hist(qdc_data[0], bins=50, range=(0, 500), color='blue', alpha=0.7)
    axs[0, 0].set_title('S2 Scintillator (MIP for all particles)')
    axs[0, 0].set_xlabel('QDC Counts')
    
    # Ch 1: S3 Scintillator
    axs[0, 1].hist(qdc_data[1], bins=50, range=(0, 500), color='green', alpha=0.7)
    axs[0, 1].set_title('S3 Scintillator (MIP for all particles)')
    axs[0, 1].set_xlabel('QDC Counts')

    # Ch 2: Calorimeter
    # Shows MIP peak + Shower Peak
    axs[0, 2].hist(qdc_data[2], bins=100, range=(0, 1000), color='red', alpha=0.7)
    axs[0, 2].set_title('Calorimeter (e- Shower vs Hadron MIP)')
    axs[0, 2].set_xlabel('QDC Counts')
    
    # Ch 3: Cherenkov C0
    axs[1, 0].hist(qdc_data[3], bins=100, range=(0, 500), color='purple', alpha=0.7)
    axs[1, 0].set_title('Cherenkov C0 (e-, Pion, Kaon)')
    axs[1, 0].set_xlabel('QDC Counts')

    # Ch 4: Cherenkov C1
    axs[1, 1].hist(qdc_data[4], bins=100, range=(0, 500), color='orange', alpha=0.7)
    axs[1, 1].set_title('Cherenkov C1 (e-, Pion)')
    axs[1, 1].set_xlabel('QDC Counts')
    
    # 2D Plot of C0 vs Calorimeter to identify electrons
    axs[1, 2].hist2d(qdc_data[2], qdc_data[3], bins=50, range=[[0, 1000], [0, 500]], cmap='viridis')
    axs[1, 2].set_title('Calorimeter vs Cherenkov C0')
    axs[1, 2].set_xlabel('Calorimeter QDC')
    axs[1, 2].set_ylabel('C0 QDC')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_png = os.path.join(os.path.dirname(filename), "qdc_physics_dashboard.png")
    plt.savefig(output_png)
    print(f"Saved Physics Dashboard to: {output_png}")
    print("=== Data Analysis Completed Successfully! ===")

if __name__ == "__main__":
    analyze_qdc_data()
