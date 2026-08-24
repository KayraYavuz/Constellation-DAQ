#!/usr/bin/env python3
"""
BL4S CERNBox Auto-Sync Daemon
Watches /home/kayra/bl4s_simulation/data for finalized .h5 run files
and automatically copies them to /eos/user/k/kyavuz/bl4s_data in real-time.
"""

import time
import os
import shutil
import glob

DATA_DIR = "/home/kayra/bl4s_simulation/data"
EOS_DIR = "/eos/user/k/kyavuz/bl4s_data"

def sync_loop():
    print(f"[CERNBox-Sync] Monitoring {DATA_DIR} -> {EOS_DIR} ...")
    synced_files = set()
    
    # Initialize with existing files so we don't spam
    if os.path.exists(EOS_DIR):
        for f in glob.glob(os.path.join(EOS_DIR, "*.h5")):
            synced_files.add(os.path.basename(f))

    while True:
        try:
            if not os.path.exists(EOS_DIR):
                os.makedirs(EOS_DIR, exist_ok=True)
                
            h5_files = glob.glob(os.path.join(DATA_DIR, "*.h5"))
            for src_path in h5_files:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(EOS_DIR, filename)
                
                # Check file size stability (ensure H5 is sealed/written)
                try:
                    size1 = os.path.getsize(src_path)
                    time.sleep(1.0)
                    size2 = os.path.getsize(src_path)
                    
                    # If size is stable and not in sync set or size changed
                    if size1 == size2 and size1 > 0:
                        if filename not in synced_files or not os.path.exists(dest_path) or os.path.getsize(dest_path) != size1:
                            shutil.copy2(src_path, dest_path)
                            synced_files.add(filename)
                            print(f"[CERNBox-Sync] Successfully uploaded {filename} ({size1 / (1024*1024):.2f} MB) to CERNBox!")
                except Exception as e:
                    # File might still be locked by H5Writer
                    pass
        except Exception as e:
            pass
        
        time.sleep(3.0)

if __name__ == "__main__":
    sync_loop()
