"""
core/straighten.py  (v2 – High-Accuracy Ensemble Engine)
---------------------------------------------------------
Multi-strategy detection with RANSAC, FFT, and weighted-median voting.

Strategies (all run, results fused):
  1. RANSAC Hough Lines     – robust against outlier lines
  2. Probabilistic Hough    – fast dense-line detection
  3. FFT Dominant Frequency – global rotation in frequency domain
  4. Multi-scale Gradient   – robust gradient-histogram at 3 scales
  5. Min-Bounding Rect      – document / product silhouette
  6. Horizon Row Analysis   – sky/ground brightness transition

Fusion:
  • Per-strategy angles are clustered (DBSCAN-like gap-split)
  • The largest cluster's weighted-median is chosen
  • A calibrated confidence score gates the final output
"""

from __future__ import annotations

import logging
import math
from typing import Tuple, List

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_angle(deg: float) -> float:
    """Map any angle to (-45, 45] — the smallest tilt correction."""
    while deg > 45:
        deg -= 90
    while deg <= -45:
        deg += 90
    return deg


def _weighted_median(values: List[float], weights: List[float]) -> float:
    """Weighted median: the value where cumulative weight crosses 0.5."""
    if not values:
        return 0.0
    paired = sorted(zip(values, weights), key=lambda x: x[0])
    total = sum(w for _, w in paired)
    cum = 0.0
    for v, w in paired:
        cum += w
        if cum >= total / 2:
            return v
    return paired[-1][0]


def _cluster_angles(angles: List[float], weights: List[float], gap: float = 5.0):
    """
    Split angle list into clusters where adjacent (sorted) values differ > gap°.
    Returns list of (angle_list, weight_list) per cluster, largest first.
    """
    if not angles:
        return []
    paired = sorted(zip(angles, weights), key=lambda x: x[0])
    clusters: List[List[Tuple[float, float]]] = [[paired[0]]]
    for i in range(1, len(paired)):
        if paired[i][0] - clusters[-1][-1][0] > gap:
            clusters.append([])
        clusters[-1].append(paired[i])
    clusters.sort(key=lambda c: sum(w for _, w in c), reverse=True)
    result = []
    for c in clusters:
        avs, aws = zip(*c)
        result.append((list(avs), list(aws)))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 1 – RANSAC Hough Lines
# ─────────────────────────────────────────────────────────────────────────────

def _ransac_hough(gray: np.ndarray) -> Tuple[float, float]:
    """
    Run Hough line detection multiple times with slightly varied parameters,
    collect all line angles, then use RANSAC-like iteration:
    pick the angle with the most inlier lines within a 2° window.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 130, apertureSize=3)
    h, w = gray.shape
    min_len = max(30, int(min(h, w) * 0.10))

    all_angles: List[float] = []
    all_lengths: List[float] = []

    # Multiple Hough passes with varied thresholds
    for threshold in [60, 80, 100]:
        for gap in [15, 25]:
            lines = cv2.HoughLinesP(
                edges, 1, np.pi / 360,  # 0.5° precision
                threshold=threshold,
                minLineLength=min_len,
                maxLineGap=gap,
            )
            if lines is None:
                continue
            for line in lines:
                x1, y1, x2, y2 = line[0]
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                if length < 5:
                    continue
                angle = _normalise_angle(math.degrees(math.atan2(dy, dx)))
                all_angles.append(angle)
                all_lengths.append(length)

    if len(all_angles) < 3:
        return 0.0, 0.0

    # RANSAC: find angle with max inlier weight within ±2°
    best_angle, best_support = 0.0, 0.0
    inlier_thresh = 2.0
    for candidate, _ in zip(all_angles, all_lengths):
        support = sum(
            l for a, l in zip(all_angles, all_lengths)
            if abs(a - candidate) <= inlier_thresh
        )
        if support > best_support:
            best_support = support
            inlier_mask = [abs(a - candidate) <= inlier_thresh for a in all_angles]
            inlier_angles = [a for a, m in zip(all_angles, inlier_mask) if m]
            inlier_lengths = [l for l, m in zip(all_lengths, inlier_mask) if m]
            best_angle = _weighted_median(inlier_angles, inlier_lengths)

    total_len = sum(all_lengths)
    inlier_len = sum(l for a, l in zip(all_angles, all_lengths)
                     if abs(a - best_angle) <= inlier_thresh)
    confidence = (inlier_len / total_len) * min(1.0, len(all_angles) / 15.0) if total_len > 0 else 0.0
    return float(best_angle), float(min(confidence, 1.0))


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 2 – FFT Dominant Rotation
# ─────────────────────────────────────────────────────────────────────────────

def _fft_angle(gray: np.ndarray) -> Tuple[float, float]:
    """
    The 2-D FFT of a rotated image has its dominant energy ridge
    perpendicular to the main lines. Find the ridge angle via
    radial projection of the FFT power spectrum.
    """
    # Resize for speed
    target = 512
    h, w = gray.shape
    scale = target / max(h, w)
    if scale < 1.0:
        small = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        small = gray.copy()

    sh, sw = small.shape

    # Apodise (Hann window) to suppress edge effects
    hann_y = np.hanning(sh).reshape(-1, 1)
    hann_x = np.hanning(sw).reshape(1, -1)
    windowed = small.astype(np.float32) * hann_y * hann_x

    # FFT + shift + log magnitude
    fft = np.fft.fft2(windowed)
    fft_shift = np.fft.fftshift(fft)
    magnitude = np.log1p(np.abs(fft_shift))

    # Mask DC component (centre square)
    cy, cx = sh // 2, sw // 2
    dc_r = min(sh, sw) // 10
    magnitude[cy - dc_r:cy + dc_r, cx - dc_r:cx + dc_r] = 0

    # Radial projection: for each angle θ, sum magnitude along that direction
    best_power, best_angle = 0.0, 0.0
    ys, xs = np.mgrid[-cy:sh - cy, -cx:sw - cx].astype(np.float32)
    radii = np.sqrt(xs ** 2 + ys ** 2)

    # Only consider mid-frequency annulus
    r_min = min(sh, sw) * 0.05
    r_max = min(sh, sw) * 0.45
    annulus = (radii >= r_min) & (radii <= r_max)

    for theta_deg in range(-45, 46):
        theta_rad = math.radians(theta_deg)
        # Project: pixels along this angle direction
        proj_x = np.cos(theta_rad)
        proj_y = np.sin(theta_rad)
        proj = xs * proj_x + ys * proj_y
        # Narrow strip perpendicular to this direction
        strip_width = max(2, int(min(sh, sw) * 0.02))
        strip_mask = (np.abs(proj) <= strip_width) & annulus
        power = float(np.sum(magnitude[strip_mask]))
        if power > best_power:
            best_power = power
            best_angle = float(theta_deg)

    # FFT gives perpendicular direction → rotate 90°
    fft_angle = _normalise_angle(best_angle - 90)
    # Low confidence for FFT — it's a weaker prior
    total_power = float(np.sum(magnitude[annulus]))
    confidence = 0.4 * (best_power / total_power) if total_power > 0 else 0.0
    return fft_angle, float(min(confidence, 0.6))


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 3 – Multi-Scale Gradient Histogram
# ─────────────────────────────────────────────────────────────────────────────

def _multiscale_gradient(gray: np.ndarray) -> Tuple[float, float]:
    """
    Compute gradient orientation histograms at multiple downscale levels,
    then fuse the results for a robust dominant-angle estimate.
    """
    angles_all: List[float] = []
    weights_all: List[float] = []

    for scale in [1.0, 0.5, 0.25]:
        h, w = gray.shape
        sh, sw = int(h * scale), int(w * scale)
        if sh < 20 or sw < 20:
            continue
        if scale < 1.0:
            g = cv2.resize(gray, (sw, sh), interpolation=cv2.INTER_AREA)
        else:
            g = gray

        gx = cv2.Sobel(g, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        ori = np.degrees(np.arctan2(gy, gx))  # -180..180

        # Only strong gradients
        thresh = np.percentile(mag, 85)
        mask = mag > thresh
        if not np.any(mask):
            continue

        sel_ori = ori[mask]
        sel_mag = mag[mask]

        # Build histogram in 1° bins [-90, 90]
        bins = np.arange(-90, 91, 1)
        hist, _ = np.histogram(sel_ori % 180 - 90, bins=bins, weights=sel_mag)

        # Peak angle
        peak_idx = int(np.argmax(hist))
        peak_angle = float(bins[peak_idx])
        peak_angle = _normalise_angle(peak_angle)

        total = float(np.sum(hist))
        if total <= 0:
            continue
        w_angle = float(hist[peak_idx]) / total

        # Scale contributes with its resolution weight
        angles_all.append(peak_angle)
        weights_all.append(w_angle * scale)  # full-scale counts more

    if not angles_all:
        return 0.0, 0.0

    angle = _weighted_median(angles_all, weights_all)
    # std-based confidence
    std = float(np.std(angles_all)) if len(angles_all) > 1 else 10.0
    confidence = max(0.0, 0.6 - std / 20.0)
    return float(angle), confidence


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 4 – Min-Bounding Rectangle (document/product)
# ─────────────────────────────────────────────────────────────────────────────

def _contour_angle(gray: np.ndarray) -> Tuple[float, float]:
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    # Try Otsu first, fall back to adaptive
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.0, 0.0
    largest = max(contours, key=cv2.contourArea)
    h, w = gray.shape
    min_area = 0.03 * h * w
    if cv2.contourArea(largest) < min_area:
        return 0.0, 0.0
    rect = cv2.minAreaRect(largest)
    angle = rect[2]
    if angle < -45:
        angle += 90
    angle = _normalise_angle(angle)
    box = cv2.boxPoints(rect)
    box_area = cv2.contourArea(box.astype(np.float32))
    contour_area = cv2.contourArea(largest)
    rectangularity = contour_area / box_area if box_area > 0 else 0.0
    confidence = rectangularity * 0.75
    return float(angle), float(confidence)


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 5 – Horizon Line Detection
# ─────────────────────────────────────────────────────────────────────────────

def _horizon_angle(gray: np.ndarray) -> Tuple[float, float]:
    h, w = gray.shape
    # Find row with maximum variance (sharpest transition)
    row_stds = np.std(gray, axis=1).astype(np.float64)
    horizon_row = int(np.argmax(row_stds))

    # Sample multiple candidate rows near the horizon
    band = max(5, h // 15)
    y_start = max(0, horizon_row - band)
    y_end = min(h, horizon_row + band)
    region = gray[y_start:y_end, :]

    edges = cv2.Canny(region, 30, 100)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30,
                             minLineLength=int(w * 0.15), maxLineGap=20)
    if lines is None:
        return 0.0, 0.15

    angles: List[float] = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx, dy = x2 - x1, y2 - y1
        a = _normalise_angle(math.degrees(math.atan2(dy, dx)))
        angles.append(a)

    if not angles:
        return 0.0, 0.15

    angle = float(np.mean(angles))
    std = float(np.std(angles))
    confidence = max(0.1, 0.4 - std / 20.0)
    return angle, confidence


# ─────────────────────────────────────────────────────────────────────────────
# Ensemble Fusion
# ─────────────────────────────────────────────────────────────────────────────

def detect_rotation_angle(image: np.ndarray) -> Tuple[float, dict]:
    """
    High-accuracy ensemble angle detection.
    All 5 strategies run, angles are clustered, and the best cluster's
    weighted-median is returned.

    Returns:
        angle  – CCW rotation degrees to apply
        diag   – diagnostic dict
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Downsample large images for analysis
    max_dim = 1400
    h, w = gray.shape
    scale = min(1.0, max_dim / max(h, w))
    if scale < 1.0:
        gray_s = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        gray_s = gray

    # --- Run all strategies ---
    strategies = {
        "ransac_hough":  _ransac_hough(gray_s),
        "fft":           _fft_angle(gray_s),
        "gradient":      _multiscale_gradient(gray_s),
        "contour":       _contour_angle(gray_s),
        "horizon":       _horizon_angle(gray_s),
    }

    diag = {name: {"angle": a, "confidence": c} for name, (a, c) in strategies.items()}

    # Collect angles with weight = confidence
    all_angles: List[float] = []
    all_weights: List[float] = []
    for name, (angle, conf) in strategies.items():
        if conf > 0.05:
            all_angles.append(angle)
            all_weights.append(conf)

    if not all_angles:
        diag["chosen"] = "none"
        diag["final_angle"] = 0.0
        diag["final_confidence"] = 0.0
        return 0.0, diag

    # --- Cluster and pick dominant group ---
    clusters = _cluster_angles(all_angles, all_weights, gap=4.0)
    best_angles, best_weights = clusters[0]

    final_angle = _weighted_median(best_angles, best_weights)
    final_conf = sum(best_weights) / (sum(all_weights) or 1.0)

    # Threshold: don't rotate if confidence too low or angle too tiny
    if final_conf < 0.08:
        final_angle = 0.0
    if abs(final_angle) < 0.25:
        final_angle = 0.0

    # Identify which strategy dominates
    best_strategy = max(strategies, key=lambda k: strategies[k][1])

    diag["chosen"] = best_strategy
    diag["final_angle"] = final_angle
    diag["final_confidence"] = final_conf
    diag["cluster_size"] = len(best_angles)

    logger.info(
        "Ensemble detection: angle=%.3f° conf=%.3f [%d strategies agreed, best=%s]",
        final_angle, final_conf, len(best_angles), best_strategy,
    )
    return final_angle, diag


# ─────────────────────────────────────────────────────────────────────────────
# Rotation (high quality)
# ─────────────────────────────────────────────────────────────────────────────

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate by `angle` degrees (CCW positive) with LANCZOS4 quality.
    Canvas is expanded to contain all pixels — no clipping.
    """
    if angle == 0.0:
        return image
    h, w = image.shape[:2]
    cx, cy = w / 2.0, h / 2.0
    M = cv2.getRotationMatrix2D((cx, cy), -angle, 1.0)
    cos_a = abs(M[0, 0])
    sin_a = abs(M[0, 1])
    new_w = int(round(h * sin_a + w * cos_a))
    new_h = int(round(h * cos_a + w * sin_a))
    M[0, 2] += new_w / 2.0 - cx
    M[1, 2] += new_h / 2.0 - cy
    return cv2.warpAffine(
        image, M, (new_w, new_h),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )
