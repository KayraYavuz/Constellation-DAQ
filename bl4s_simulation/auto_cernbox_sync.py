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
OLD_DATA_DIR = "/home/kayra/bl4s_simulation/old_data"
EOS_DIR = "/eos/user/k/kyavuz/bl4s_data"

def sync_loop():
    print(f"[CERNBox-Sync] Monitoring {DATA_DIR} -> {EOS_DIR} & archiving to {OLD_DATA_DIR} ...")
    os.makedirs(OLD_DATA_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    while True:
        try:
            if not os.path.exists(EOS_DIR):
                os.makedirs(EOS_DIR, exist_ok=True)
                
            h5_files = glob.glob(os.path.join(DATA_DIR, "*.h5"))
            for src_path in h5_files:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(EOS_DIR, filename)
                archive_path = os.path.join(OLD_DATA_DIR, filename)
                
                # Check file size stability (ensure H5 is sealed/closed by STOP)
                try:
                    size1 = os.path.getsize(src_path)
                    time.sleep(1.5)
                    size2 = os.path.getsize(src_path)
                    
                    # If size is completely stable and file is ready
                    if size1 == size2 and size1 > 0:
                        # 1. Upload to CERNBox
                        shutil.copy2(src_path, dest_path)
                        print(f"[CERNBox-Sync] Successfully uploaded {filename} ({size1 / (1024*1024):.2f} MB) to CERNBox!")
                        
                        # 2. Move to old_data so data/ directory stays clean for new runs
                        shutil.move(src_path, archive_path)
                        print(f"[CERNBox-Sync] Moved {filename} -> {OLD_DATA_DIR}/")
                except Exception as e:
                    # File is still actively written by H5DataWriter
                    pass
        except Exception as e:
            pass
        
        time.sleep(3.0)


if __name__ == "__main__":
    sync_loop()
