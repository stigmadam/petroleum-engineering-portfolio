"""
pvt.py
------
Standard black-oil PVT correlations (Standing, Vasquez-Beggs, Beggs-Robinson,
Lee et al., Papay) used to support the IPR-VLP nodal analysis model.

All correlations use field units:
    P    : psia
    T    : degF
    Rs   : scf/STB
    Bo   : rb/STB
    Bg   : rb/scf
    API  : degrees API
    gg   : gas specific gravity (air = 1)
    visc : cp
    rho  : lbm/ft3
"""

import numpy as np


def oil_sg(api):
    """Oil specific gravity from API gravity."""
    return 141.5 / (131.5 + api)


# ---------------------------------------------------------------- GAS ----
def gas_pseudocriticals(gg):
    """Standing correlation for pseudo-critical properties of dry/associated gas."""
    ppc = 677.0 + 15.0 * gg - 37.5 * gg ** 2       # psia
    tpc = 168.0 + 325.0 * gg - 12.5 * gg ** 2       # degR
    return ppc, tpc


def gas_z_factor(p, t_f, gg):
    """
    Gas compressibility factor via the Papay (1968) explicit approximation
    to the Standing-Katz chart. Adequate for screening / nodal analysis work.
    """
    ppc, tpc = gas_pseudocriticals(gg)
    ppr = p / ppc
    tpr = (t_f + 460.0) / tpc
    z = 1.0 - (3.52 * ppr) / (10 ** (0.9813 * tpr)) + (0.274 * ppr ** 2) / (10 ** (0.8157 * tpr))
    return max(z, 0.2)


def gas_fvf(p, t_f, z):
    """Gas formation volume factor, rb/scf."""
    return 0.00504 * z * (t_f + 460.0) / p


def gas_density(p, t_f, gg, z):
    """Gas density, lbm/ft3."""
    mg = 28.97 * gg
    return (p * mg) / (z * 10.732 * (t_f + 460.0))


def gas_viscosity(p, t_f, gg, z):
    """Lee, Gonzalez & Eakin (1966) gas viscosity correlation, cp."""
    mg = 28.97 * gg
    t_r = t_f + 460.0
    rho_g = gas_density(p, t_f, gg, z) / 62.4  # g/cc equivalent scaling used in Lee correlation
    k = ((9.4 + 0.02 * mg) * t_r ** 1.5) / (209.0 + 19.0 * mg + t_r)
    x = 3.5 + 986.0 / t_r + 0.01 * mg
    y = 2.4 - 0.2 * x
    mu_g = 1e-4 * k * np.exp(x * rho_g ** y)
    return mu_g


# ---------------------------------------------------------------- OIL ----
def rs_standing(p, t_f, api, gg, pb, rsb):
    """
    Standing (1947) solution GOR correlation.
    For P >= Pb the oil is undersaturated -> Rs is held at Rsb.
    For P <  Pb, Rs decreases from Rsb per the Standing correlation.
    """
    p_eval = min(p, pb)
    rs = gg * ((p_eval / 18.2 + 1.4) * 10 ** (0.0125 * api - 0.00091 * t_f)) ** 1.2048
    if p >= pb:
        return rsb
    return rs


def bo_standing(p, t_f, api, gg, pb, rsb, rs):
    """
    Standing correlation for oil FVF below/at bubble point, with a simple
    Vasquez-Beggs undersaturated compressibility correction above Pb.
    """
    go = oil_sg(api)
    bob = 0.9759 + 0.00012 * (rsb * (gg / go) ** 0.5 + 1.25 * t_f) ** 1.2
    if p <= pb:
        bo_sat = 0.9759 + 0.00012 * (rs * (gg / go) ** 0.5 + 1.25 * t_f) ** 1.2
        return bo_sat
    # undersaturated region: shrink Bo slightly above Pb using Vasquez-Beggs co
    co = (-1433.0 + 5.0 * rsb + 17.2 * t_f - 1180.0 * gg + 12.61 * api) / (1e5 * p)
    co = max(co, 3e-6)
    return bob * np.exp(-co * (p - pb))


def oil_density(p, t_f, api, gg, bo, rs):
    """Live oil density, lbm/ft3."""
    go = oil_sg(api)
    return (350.17 * go + 0.0764 * rs * gg) / (5.615 * bo)


def dead_oil_viscosity(t_f, api):
    """Beggs-Robinson dead oil viscosity, cp."""
    x = (10 ** (3.0324 - 0.02023 * api)) * t_f ** (-1.163)
    return 10 ** x - 1.0


def oil_viscosity(p, t_f, api, rs, pb):
    """Beggs-Robinson live/undersaturated oil viscosity, cp."""
    mu_od = dead_oil_viscosity(t_f, api)
    a = 10.715 * (rs + 100.0) ** (-0.515)
    b = 5.44 * (rs + 150.0) ** (-0.338)
    mu_ob = a * mu_od ** b
    if p <= pb:
        return mu_ob
    m = 2.6 * p ** 1.187 * np.exp(-11.513 - 8.98e-5 * p)
    return mu_ob * (p / pb) ** m


# -------------------------------------------------------------- WATER ----
def water_viscosity(t_f):
    """Van Wingen / McCain approximation, cp."""
    return np.exp(1.003 - 1.479e-2 * t_f + 1.982e-5 * t_f ** 2)


def water_density(sg_w, bw=1.01):
    """Water density, lbm/ft3 (Bw assumed ~constant, weak function of P,T)."""
    return 62.4 * sg_w / bw
