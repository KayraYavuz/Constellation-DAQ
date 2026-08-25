#!/usr/bin/env python3
"""
BL4S CERNBox Auto-Sync Daemon
- Watches data/ for new .h5 run files finalized on STOP
- Uploads to CERNBox: /eos/user/k/kyavuz/bl4s_data/old_data/
- Archives locally to old_data/
- At startup: syncs any existing old_data/ files not yet on CERNBox
"""

import time
import os
import shutil
import glob
import subprocess

DATA_DIR     = "/home/kayra/bl4s_simulation/data"
OLD_DATA_DIR = "/home/kayra/bl4s_simulation/old_data"

# CERNBox EOS paths — old_data/ mirrors the local archive folder
EOS_OLD_DIR  = "/eos/user/k/kyavuz/bl4s_data/old_data"
EOS_OLD_XRD  = "root://eosuser.cern.ch//eos/user/k/kyavuz/bl4s_data/old_data"
CERN_USER    = "kyavuz"


def renew_kerberos():
    """Silently renew Kerberos ticket."""
    try:
        subprocess.run(["kinit", "-R", CERN_USER], timeout=5, capture_output=True)
    except Exception:
        pass


def eos_mkdir():
    """Ensure the old_data/ folder exists on CERNBox."""
    try:
        subprocess.run(
            ["xrdfs", "eosuser.cern.ch", "mkdir", "-p",
             "/eos/user/k/kyavuz/bl4s_data/old_data"],
            timeout=10, capture_output=True
        )
    except Exception:
        pass
    try:
        os.makedirs(EOS_OLD_DIR, exist_ok=True)
    except Exception:
        pass


def upload_to_eos(src_path: str, filename: str) -> bool:
    """Upload a file to CERNBox old_data/. Try xrdcp first, then fuse cp."""
    dest_xrd = f"{EOS_OLD_XRD}/{filename}"
    dest_cp  = os.path.join(EOS_OLD_DIR, filename)

    # Method 1: xrdcp (native EOS, no Kerberos dependency)
    try:
        r = subprocess.run(
            ["xrdcp", "--silent", src_path, dest_xrd],
            timeout=120, capture_output=True
        )
        if r.returncode == 0:
            print(f"[CERNBox-Sync] xrdcp OK → old_data/{filename}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Method 2: FUSE-mounted EOS (requires kinit)
    try:
        eos_mkdir()
        shutil.copy2(src_path, dest_cp)
        print(f"[CERNBox-Sync] cp OK → old_data/{filename}")
        return True
    except Exception as e:
        print(f"[CERNBox-Sync] Upload FAILED for {filename}: {e}")
        return False


def already_on_eos(filename: str) -> bool:
    """Check if file already exists on EOS (xrdfs stat)."""
    try:
        r = subprocess.run(
            ["xrdfs", "eosuser.cern.ch", "stat",
             f"/eos/user/k/kyavuz/bl4s_data/old_data/{filename}"],
            timeout=5, capture_output=True
        )
        return r.returncode == 0
    except Exception:
        pass
    # Fallback: check FUSE mount
    return os.path.exists(os.path.join(EOS_OLD_DIR, filename))


def backfill_old_data():
    """Upload any old_data/ files not yet on CERNBox."""
    existing = glob.glob(os.path.join(OLD_DATA_DIR, "*.h5"))
    if not existing:
        return
    print(f"[CERNBox-Sync] Backfill: checking {len(existing)} file(s) in old_data/ ...")
    eos_mkdir()
    for src_path in existing:
        filename = os.path.basename(src_path)
        if already_on_eos(filename):
            print(f"[CERNBox-Sync] Already on CERNBox: {filename} (skip)")
        else:
            print(f"[CERNBox-Sync] Uploading missing file: {filename}")
            upload_to_eos(src_path, filename)


def sync_loop():
    os.makedirs(OLD_DATA_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[CERNBox-Sync] Started. Watching {DATA_DIR}")
    print(f"[CERNBox-Sync] Uploading to: {EOS_OLD_XRD}")

    renew_kerberos()
    eos_mkdir()
    backfill_old_data()  # Upload any leftover files at startup

    last_kinit = time.time()

    while True:
        # Renew Kerberos every 30 minutes
        if time.time() - last_kinit > 1800:
            renew_kerberos()
            last_kinit = time.time()

        h5_files = glob.glob(os.path.join(DATA_DIR, "*.h5"))
        for src_path in h5_files:
            filename = os.path.basename(src_path)
            archive_path = os.path.join(OLD_DATA_DIR, filename)
            try:
                size1 = os.path.getsize(src_path)
                if size1 == 0:
                    continue
                time.sleep(2.0)
                size2 = os.path.getsize(src_path)

                # File stable → STOP received, H5DataWriter flushed
                if size1 == size2:
                    mb = size1 / (1024 * 1024)
                    print(f"[CERNBox-Sync] Run finalized: {filename} ({mb:.2f} MB)")

                    # 1. Upload to CERNBox old_data/
                    uploaded = upload_to_eos(src_path, filename)

                    # 2. Always archive locally
                    shutil.move(src_path, archive_path)
                    print(f"[CERNBox-Sync] Archived → old_data/{filename}")

                    if not uploaded:
                        print(f"[CERNBox-Sync] WARNING: Upload failed. File safe in local old_data/")
            except Exception:
                pass

        time.sleep(3.0)


if __name__ == "__main__":
    sync_loop()
