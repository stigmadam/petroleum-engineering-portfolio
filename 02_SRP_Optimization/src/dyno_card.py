"""
dyno_card.py
------------
Generates stylized surface dynamometer cards (polished-rod load vs. position)
for the classic sucker-rod-pump (SRP) failure modes discussed in standard
artificial-lift references (Gibbs, API RP 11L discussions of card shapes).

These are SYNTHETIC, parametrically-generated cards built to reproduce the
*characteristic shape signatures* engineers are trained to recognize on a
dynamometer card - they are not measured field data or a full rod-string
wave-equation simulation (see report.md, Limitations).

Position is normalized 0 -> S (in) over the stroke. Each card is returned as
a closed loop: upstroke leg (position 0 -> S) followed by downstroke leg
(position S -> 0).
"""

import numpy as np


def _smoothstep(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _gaussian(x, center, width):
    return np.exp(-0.5 * ((x - center) / width) ** 2)


def _smooth_noise(n_pts, scale, rng, n_ctrl=10):
    """Low-frequency correlated noise (real dyno traces are not white noise)."""
    ctrl = rng.normal(0, scale, size=n_ctrl)
    xp = np.linspace(0, n_pts - 1, n_ctrl)
    x = np.arange(n_pts)
    return np.interp(x, xp, ctrl)


CONDITIONS = [
    "normal",
    "gas_interference",
    "fluid_pound",
    "worn_traveling_valve",
    "parted_rod",
]


def generate_card(condition, pprl, mprl, stroke_in=64.0, n_pts=160, noise=0.01, seed=None):
    """
    Returns (position, load) arrays tracing one closed dynamometer card loop
    for the requested condition.

    pprl, mprl : target peak / minimum polished rod load (lbf) for a HEALTHY
                 equivalent card - individual conditions modify these targets
                 internally to reflect the physical effect of that failure
                 mode (e.g. gas interference compresses the range).
    """
    rng = np.random.default_rng(seed)
    s = stroke_in
    x = np.linspace(0, s, n_pts)

    if condition == "normal":
        load_up = mprl + (pprl - mprl) * _smoothstep(x, 0, 0.12 * s)
        d = s - x
        load_down = pprl - (pprl - mprl) * _smoothstep(d, 0, 0.12 * s)

    elif condition == "gas_interference":
        pprl_g, mprl_g = pprl * 0.82, mprl * 1.22   # compressed load range
        load_up = mprl_g + (pprl_g - mprl_g) * _smoothstep(x, 0, 0.55 * s)
        d = s - x
        load_down = pprl_g - (pprl_g - mprl_g) * _smoothstep(d, 0, 0.55 * s)

    elif condition == "fluid_pound":
        load_up = mprl + (pprl - mprl) * _smoothstep(x, 0, 0.12 * s)
        d = s - x
        load_down = pprl - (pprl - mprl) * _smoothstep(d, 0, 0.12 * s)
        # shock load spike near the bottom of the downstroke (plunger hits fluid)
        pound = 0.35 * (pprl - mprl) * _gaussian(d, center=0.86 * s, width=0.035 * s)
        load_down = load_down - pound

    elif condition == "worn_traveling_valve":
        pprl_w = pprl * 0.72
        tilt = 0.22 * (pprl - mprl) / s
        load_up = mprl + (pprl_w - mprl) * _smoothstep(x, 0, 0.30 * s) + tilt * x
        d = s - x
        load_down = (pprl_w + tilt * s) - (pprl_w + tilt * s - mprl) * _smoothstep(d, 0, 0.30 * s)

    elif condition == "parted_rod":
        flat = (pprl + mprl) / 2 * 0.35
        load_up = np.full_like(x, flat) + 0.01 * (pprl - mprl) * (x / s)
        load_down = np.full_like(x, flat) + 0.01 * (pprl - mprl) * (x / s)

    else:
        raise ValueError(f"Unknown condition: {condition}")

    load_up = load_up + _smooth_noise(n_pts, noise * (pprl - mprl), rng)
    load_down = load_down + _smooth_noise(n_pts, noise * (pprl - mprl), rng)

    position = np.concatenate([x, x[::-1]])
    load = np.concatenate([load_up, load_down[::-1]])
    return position, load
