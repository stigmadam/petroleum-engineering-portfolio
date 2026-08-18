"""
diagnostics.py
--------------
Feature extraction and rule-based diagnosis for surface dynamometer cards.

Approach: this mirrors how a production/surveillance engineer visually reads
a card before more advanced ML-based pattern recognition is applied in a
SCADA/RTU system - a small set of interpretable features (peak/min load,
card area ratio, notch depth, top-edge tilt) are extracted, and a decision
tree of hand-written rules (calibrated against the synthetic generator in
dyno_card.py) assigns the most likely failure mode plus a recommended action.

A rule-based approach is deliberately used instead of a black-box ML model:
it is fully explainable, requires no training data, and mirrors the manual
diagnostic logic taught in artificial-lift training (e.g. IWCF/well
surveillance courses) - important when a recommendation may drive a
workover decision.
"""

import numpy as np


def card_area(position, load):
    """Shoelace formula - area enclosed by the closed card loop (lbf-in)."""
    x, y = position, load
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def extract_features(position, load, stroke_in):
    pprl = float(np.max(load))
    mprl = float(np.min(load))
    rng = pprl - mprl
    area = card_area(position, load)
    rect_area = stroke_in * rng
    area_ratio = area / rect_area if rect_area > 0 else 0.0

    n = len(position) // 2
    up_pos, up_load = position[:n], load[:n]
    down_pos, down_load = position[n:], load[n:]

    # top-edge tilt: slope of the upstroke load in the top 60% of stroke (worn valve signature)
    top_mask = up_pos > 0.35 * stroke_in
    if top_mask.sum() > 3:
        tilt = np.polyfit(up_pos[top_mask], up_load[top_mask], 1)[0]
    else:
        tilt = 0.0

    # notch depth: how far load dips below the local baseline on the downstroke (fluid pound signature)
    if len(down_load) > 5:
        baseline = np.median(down_load[len(down_load) // 3:])
        notch_depth = max(baseline - np.min(down_load), 0.0)
    else:
        notch_depth = 0.0
    notch_ratio = notch_depth / rng if rng > 0 else 0.0

    return dict(pprl=pprl, mprl=mprl, load_range=rng, area_ratio=round(area_ratio, 3),
                top_tilt_lbf_per_in=round(float(tilt), 1), notch_ratio=round(notch_ratio, 3))


def diagnose(features, healthy_load_range=None):
    """
    Rule-based decision tree. Returns (diagnosis, confidence_note, recommendation).

    `healthy_load_range` (optional, lbf) is the well's expected/design
    (PPRL - MPRL) when operating normally - known from the pump design card
    or well file, NOT derived from the card being diagnosed. It lets the
    "mechanical failure" rule scale to the well's own load magnitude rather
    than using a fixed absolute threshold.
    """
    f = features
    ref_range = healthy_load_range if healthy_load_range else max(f["load_range"] * 3, 1000.0)

    # 1. Mechanical failure: almost no card area, load barely varies -> parted rod / stuck pump
    if f["area_ratio"] < 0.20 and f["load_range"] < 0.30 * ref_range:
        return ("Parted rod / stuck pump (mechanical failure)",
                "Card collapsed to a thin sliver - almost no work being done at surface.",
                "Shut down immediately, pull rods on next available rig, inspect rod string/pump for parting or plunger sticking.")

    # 2. Fluid pound: sharp localized notch on the downstroke
    if f["notch_ratio"] > 0.20:
        return ("Fluid pound (pump-off / low fluid level)",
                f"Sharp load notch on downstroke, notch_ratio={f['notch_ratio']}.",
                "Reduce SPM or stroke length, consider pump-off controller / timer to match runtime to inflow, verify fluid level.")

    # 3. Worn traveling valve: tilted top edge (load keeps rising instead of a flat plateau)
    if f["top_tilt_lbf_per_in"] > 8.0 and f["area_ratio"] < 0.65:
        return ("Worn / leaking traveling valve",
                f"Diagonal top edge instead of flat plateau, tilt={f['top_tilt_lbf_per_in']} lbf/in.",
                "Schedule workover to pull and inspect/replace traveling valve ball & seat; monitor volumetric efficiency in the meantime.")

    # 4. Gas interference: rounded corners, compressed load range, moderate area ratio
    if f["area_ratio"] < 0.65 and f["top_tilt_lbf_per_in"] <= 8.0 and f["notch_ratio"] <= 0.20:
        return ("Gas interference",
                f"Rounded, compressed card (area_ratio={f['area_ratio']}) without a sharp notch or tilt.",
                "Check/install gas anchor, consider lowering pump intake below perforations, evaluate SPM reduction to allow better gas separation.")

    # 5. Otherwise: normal, well-filled card
    return ("Normal operation",
            f"Near-rectangular card, area_ratio={f['area_ratio']}.",
            "No intervention required - continue routine surveillance.")
