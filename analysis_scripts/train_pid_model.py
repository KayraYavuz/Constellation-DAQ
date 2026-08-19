#!/usr/bin/env python3
"""
BL4S Machine Learning Particle Identification (PID) Model Training Suite
Trains a Multi-Class Classifier (Electron, Muon, Pion, Proton, Pi0, Noise)
using simulated high-energy physics detector signatures.
Exports optimized model weights and feature scalers to JSON for real-time sub-millisecond inference.
"""

import os
import json
import math
import random
import numpy as np

PARTICLE_CLASSES = ["electron", "muon", "pion", "proton", "pi0", "noise"]
FEATURE_NAMES = [
    "calo_e_total",         # Total energy deposited in Pb-Glass calorimeter (MeV)
    "calo_shower_radius",   # Lateral shower dispersion radius (mm)
    "cherenkov_qdc",        # Cherenkov counter PMT integrated charge (QDC channels)
    "timepix_tot",          # Mean Timepix cluster Time-over-Threshold (dE/dx proxy)
    "timepix_cluster_size", # Number of pixels firing per cluster
    "tof_ns",               # Time of Flight between S1 and S2 (ns)
    "beta_velocity"         # Computed particle velocity v/c
]

def generate_synthetic_dataset(n_samples_per_class: int = 2000):
    """
    Generates synthetic physics events with realistic Gaussian and Landau distributions
    calibrated against CERN PS / DESY test beam parameters (~1-3 GeV/c momentum).
    """
    data = []
    labels = []
    
    # Distance S1 -> S2 is ~4.5 meters => light time ~ 15.0 ns
    c_light = 0.299792458 # m/ns
    dist_m = 4.5
    t_light = dist_m / c_light # ~15.01 ns
    
    for cls_idx, cls_name in enumerate(PARTICLE_CLASSES):
        for _ in range(n_samples_per_class):
            if cls_name == "electron":
                # EM Shower (Full energy), High Cherenkov light (beta~1.0), MIP in TPX
                calo_e = float(np.random.normal(2000, 150))
                shower_r = float(np.random.normal(18.0, 3.0))
                cherenkov = float(np.random.normal(850, 90))
                tot = float(np.random.normal(28, 5))
                c_size = float(np.random.normal(3.2, 0.8))
                tof = float(np.random.normal(t_light, 0.3))
                beta = dist_m / (tof * c_light)

            elif cls_name == "muon":
                # MIP in calo (~150-200 MeV), moderate Cherenkov, MIP in TPX, beta~1.0
                calo_e = float(np.random.normal(180, 25))
                shower_r = float(np.random.normal(6.0, 1.5))
                cherenkov = float(np.random.normal(620, 80))
                tot = float(np.random.normal(30, 4))
                c_size = float(np.random.normal(2.8, 0.6))
                tof = float(np.random.normal(t_light + 0.15, 0.35))
                beta = dist_m / (tof * c_light)

            elif cls_name == "pion":
                # Charged pion: Hadronic interaction/MIP, low/moderate Cherenkov, MIP in TPX
                calo_e = float(np.random.normal(350, 120))
                shower_r = float(np.random.normal(12.0, 4.0))
                cherenkov = float(np.random.normal(450, 90))
                tot = float(np.random.normal(35, 6))
                c_size = float(np.random.normal(3.5, 0.9))
                tof = float(np.random.normal(t_light + 0.3, 0.4))
                beta = dist_m / (tof * c_light)

            elif cls_name == "proton":
                # Heavy proton: High ionization (Bragg dE/dx, high ToT & large cluster), no Cherenkov, slower ToF
                calo_e = float(np.random.normal(500, 180))
                shower_r = float(np.random.normal(14.0, 3.5))
                cherenkov = float(np.random.normal(40, 15)) # Below Cherenkov threshold
                tot = float(np.random.normal(85, 16))        # High dE/dx
                c_size = float(np.random.normal(9.5, 2.5))
                tof = float(np.random.normal(t_light + 1.8, 0.6)) # Slower
                beta = dist_m / (tof * c_light)

            elif cls_name == "pi0":
                # Neutral pion decay (pi0 -> gamma gamma): Dual EM shower in calo (>2200 MeV), wide shower, no Cherenkov
                calo_e = float(np.random.normal(2400, 220))
                shower_r = float(np.random.normal(32.0, 6.0)) # Wide dual cluster
                cherenkov = float(np.random.normal(50, 20))
                tot = float(np.random.normal(32, 7))
                c_size = float(np.random.normal(3.8, 1.0))
                tof = float(np.random.normal(t_light + 0.1, 0.35))
                beta = dist_m / (tof * c_light)

            elif cls_name == "noise":
                # Pedestal noise / accidental background
                calo_e = float(np.random.exponential(50))
                shower_r = float(np.random.uniform(0, 40))
                cherenkov = float(np.random.exponential(30))
                tot = float(np.random.exponential(15))
                c_size = float(np.random.uniform(1.0, 3.0))
                tof = float(np.random.uniform(5.0, 35.0))
                beta = dist_m / (tof * c_light)

            # Ensure physically valid bounds
            calo_e = max(0.0, calo_e)
            shower_r = max(1.0, shower_r)
            cherenkov = max(0.0, cherenkov)
            tot = max(0.0, tot)
            c_size = max(1.0, c_size)
            tof = max(1.0, tof)
            beta = max(0.1, min(1.2, beta))

            feature_vec = [calo_e, shower_r, cherenkov, tot, c_size, tof, beta]
            data.append(feature_vec)
            labels.append(cls_idx)

    return np.array(data), np.array(labels)

def train_and_export_model(output_path: str = "pid_model_weights.json"):
    print("=" * 65)
    print("  BL4S Multi-Class Particle Identification (PID) Training")
    print("=" * 65)
    
    print("\n[1/4] Generating high-statistics physics calibration dataset...")
    X, y = generate_synthetic_dataset(n_samples_per_class=3000)
    print(f"      Total Events: {len(X)} across {len(PARTICLE_CLASSES)} particle categories.")

    # Compute Feature Mean & Std for scaling
    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0)
    stds[stds == 0] = 1.0
    X_scaled = (X - means) / stds

    # Compute Class Centroids & Covariance for Mahalanobis / Prototype Classifier
    centroids = {}
    inv_covariances = {}
    priors = {}
    
    for cls_idx, cls_name in enumerate(PARTICLE_CLASSES):
        cls_mask = (y == cls_idx)
        X_cls = X_scaled[cls_mask]
        centroid = np.mean(X_cls, axis=0)
        cov = np.cov(X_cls, rowvar=False) + np.eye(len(FEATURE_NAMES)) * 1e-4
        inv_cov = np.linalg.inv(cov)
        
        centroids[cls_name] = centroid.tolist()
        inv_covariances[cls_name] = inv_cov.tolist()
        priors[cls_name] = float(np.sum(cls_mask) / len(y))

    print("\n[2/4] Evaluating multi-class discriminant accuracy...")
    correct = 0
    confusion = np.zeros((len(PARTICLE_CLASSES), len(PARTICLE_CLASSES)), dtype=int)
    
    for i in range(len(X)):
        x_vec = X_scaled[i]
        best_score = -float('inf')
        pred_cls = 0
        
        for c_idx, c_name in enumerate(PARTICLE_CLASSES):
            c_vec = np.array(centroids[c_name])
            inv_c = np.array(inv_covariances[c_name])
            diff = x_vec - c_vec
            # Quadratic Discriminant / Mahalanobis score
            maha_dist = float(np.dot(np.dot(diff, inv_c), diff))
            score = -0.5 * maha_dist + math.log(priors[c_name] + 1e-6)
            if score > best_score:
                best_score = score
                pred_cls = c_idx
                
        confusion[y[i]][pred_cls] += 1
        if pred_cls == y[i]:
            correct += 1

    accuracy = (correct / len(X)) * 100.0
    print(f"      Overall Classification Accuracy: {accuracy:.2f}%")

    print("\n[3/4] Confusion Matrix:")
    header = f"{'True \\ Pred':>12} | " + " | ".join([f"{c[:6]:>6}" for c in PARTICLE_CLASSES])
    print("      " + header)
    print("      " + "-" * len(header))
    for i, c_name in enumerate(PARTICLE_CLASSES):
        row_str = f"{c_name:>12} | " + " | ".join([f"{confusion[i][j]:>6}" for j in range(len(PARTICLE_CLASSES))])
        print("      " + row_str)

    # Feature Importance via variance ratios
    feature_weights = {}
    for f_idx, f_name in enumerate(FEATURE_NAMES):
        inter_class_variance = np.var([centroids[c][f_idx] for c in PARTICLE_CLASSES])
        feature_weights[f_name] = round(float(inter_class_variance), 4)

    total_w = sum(feature_weights.values())
    normalized_weights = {k: round(v / total_w, 4) for k, v in feature_weights.items()}

    print("\n[4/4] Feature Importance Breakdown:")
    for f_name, w in sorted(normalized_weights.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(w * 30)
        print(f"      {f_name:<22}: {w*100:>5.1f}% | {bar}")

    model_payload = {
        "model_name": "BL4S_QuadraticDiscriminant_PID_v3.0",
        "features": FEATURE_NAMES,
        "classes": PARTICLE_CLASSES,
        "scaler_means": means.tolist(),
        "scaler_stds": stds.tolist(),
        "centroids": centroids,
        "inv_covariances": inv_covariances,
        "priors": priors,
        "feature_importance": normalized_weights,
        "training_accuracy_pct": round(accuracy, 2)
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model_payload, f, indent=2)

    print(f"\n[OK] Model successfully exported to: {output_path}")
    return model_payload

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_json = os.path.join(script_dir, "pid_model_weights.json")
    train_and_export_model(target_json)
