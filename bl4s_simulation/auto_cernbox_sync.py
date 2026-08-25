#!/usr/bin/env python3
"""
BL4S CERNBox Auto-Sync Daemon
Watches /home/kayra/bl4s_simulation/data for finalized .h5 run files.
On STOP (file size becomes stable), immediately uploads to CERNBox via xrdcp or cp,
then moves the file to old_data/ archive.
"""

import time
import os
import shutil
import glob
import subprocess

DATA_DIR = "/home/kayra/bl4s_simulation/data"
OLD_DATA_DIR = "/home/kayra/bl4s_simulation/old_data"
EOS_DIR = "/eos/user/k/kyavuz/bl4s_data"
EOS_XRD_PATH = "root://eosuser.cern.ch//eos/user/k/kyavuz/bl4s_data"
CERN_USER = "kyavuz"


def renew_kerberos():
    """Try to renew Kerberos ticket silently."""
    try:
        subprocess.run(["kinit", "-R", CERN_USER], timeout=5,
                       capture_output=True)
    except Exception:
        pass


def upload_to_eos(src_path: str, filename: str) -> bool:
    """Try xrdcp first (CERN EOS native), fallback to cp."""
    dest_xrd = f"{EOS_XRD_PATH}/{filename}"
    dest_cp = os.path.join(EOS_DIR, filename)

    # Method 1: xrdcp (best for EOS - no Kerberos ticket needed if token exists)
    try:
        result = subprocess.run(
            ["xrdcp", "--silent", src_path, dest_xrd],
            timeout=120, capture_output=True
        )
        if result.returncode == 0:
            print(f"[CERNBox-Sync] xrdcp OK: {filename} -> CERNBox")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Method 2: EOS fuse mount with plain cp (requires kinit)
    try:
        os.makedirs(EOS_DIR, exist_ok=True)
        shutil.copy2(src_path, dest_cp)
        print(f"[CERNBox-Sync] cp OK: {filename} -> {EOS_DIR}/")
        return True
    except Exception as e:
        print(f"[CERNBox-Sync] Upload failed for {filename}: {e}")
        return False


def sync_loop():
    os.makedirs(OLD_DATA_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[CERNBox-Sync] Watching {DATA_DIR} | Uploading to CERNBox on STOP ...")

    # Attempt Kerberos renewal at startup
    renew_kerberos()
    last_kinit_renew = time.time()

    while True:
        # Renew Kerberos ticket every 30 minutes
        if time.time() - last_kinit_renew > 1800:
            renew_kerberos()
            last_kinit_renew = time.time()

        h5_files = glob.glob(os.path.join(DATA_DIR, "*.h5"))
        for src_path in h5_files:
            filename = os.path.basename(src_path)
            archive_path = os.path.join(OLD_DATA_DIR, filename)

            try:
                size1 = os.path.getsize(src_path)
                if size1 == 0:
                    continue

                # Wait and check if file is still being written (STOP not yet called)
                time.sleep(2.0)
                size2 = os.path.getsize(src_path)

                # Size stable = H5DataWriter flushed and closed the file (STOP received)
                if size1 == size2:
                    print(f"[CERNBox-Sync] Detected finalized run: {filename} ({size1 / (1024*1024):.2f} MB)")

                    # 1. Upload to CERNBox
                    uploaded = upload_to_eos(src_path, filename)

                    # 2. Always archive locally regardless of upload success
                    shutil.move(src_path, archive_path)
                    print(f"[CERNBox-Sync] Archived {filename} -> old_data/")

                    if not uploaded:
                        print(f"[CERNBox-Sync] WARNING: Upload failed. File safe in old_data/.")

            except Exception:
                pass

        time.sleep(3.0)


if __name__ == "__main__":
    sync_loop()
