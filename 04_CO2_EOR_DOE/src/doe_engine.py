"""
doe_engine.py
-------------
Reproduces the Two-Level Full Factorial (2^6) DOE analysis from the thesis
using only the raw 64-run simulation matrix (Tables 7-9) - no access to the
original Minitab project or EORgui software is required or used.

Key methodological note: the factor levels actually run in the experiment
were determined EMPIRICALLY from the raw data (min/max observed per column)
rather than assumed from the thesis's narrative "Low/Medium/High" tables.
This matters because, on inspection, the as-run levels for a few
factors/fields differ slightly from the nominal ranges stated in the
methodology text (e.g. Field Y's tested Thickness/D-P Coefficient levels
sit closer to the reported "Medium" values than the reported "High" values).
This is a common, normal occurrence in real experimental work, and
verifying against the raw run matrix - rather than trusting the narrative
table - is the correct engineering practice, so it is kept and reported
here rather than silently "corrected."

Design/analysis approach (matches Minitab's default 2-level factorial
treatment for an unreplicated design):
  1. Code every factor to -1 (low) / +1 (high).
  2. Fit the SATURATED model (intercept + all effects up to the 6-way
     interaction = 64 terms for 64 runs) via ordinary least squares. Because
     the coded design is exactly orthogonal, this has a closed-form solution
     and is numerically exact (not an approximation).
  3. Pool the higher-order interactions (3-way and above, 42 terms) as an
     estimate of "pure error" - the standard remedy for an unreplicated
     factorial where individual replicate error is unavailable. This gives
     42 error degrees of freedom.
  4. Standardized effect (equivalent to Minitab's Pareto chart value) for
     each main effect / 2-way interaction = t-statistic = effect / SE(effect),
     using the pooled error variance from step 3.
"""

import itertools
import numpy as np
import pandas as pd
from scipy import stats

FACTOR_COLS = ["initial_oil_cut", "pattern_area", "porosity",
                "permeability", "thickness", "dp_coefficient"]
FACTOR_LABELS = {"initial_oil_cut": "A (Initial Oil Cut)", "pattern_area": "B (Pattern Area)",
                  "porosity": "C (Porosity)", "permeability": "D (Permeability)",
                  "thickness": "E (Thickness)", "dp_coefficient": "F (D-P Coefficient)"}
FACTOR_CODES = {"initial_oil_cut": "A", "pattern_area": "B", "porosity": "C",
                 "permeability": "D", "thickness": "E", "dp_coefficient": "F"}


def load_field(csv_path):
    df = pd.read_csv(csv_path)
    return df


def code_factors(df):
    """Code each factor column to -1/+1 based on the empirical min/max actually run."""
    coded = pd.DataFrame(index=df.index)
    levels = {}
    for col in FACTOR_COLS:
        lo, hi = df[col].min(), df[col].max()
        levels[col] = (lo, hi)
        mid = (lo + hi) / 2
        coded[col] = np.where(df[col] >= mid, 1.0, -1.0)
        # sanity check: should be a true 2-level design
        n_unique = df[col].nunique()
        if n_unique != 2:
            raise ValueError(f"Column {col} has {n_unique} unique values - not a 2-level factor as expected.")
    return coded, levels


def build_design_matrix(coded, max_order=6):
    """Build the full saturated design matrix: intercept + all interactions up to max_order."""
    cols = list(coded.columns)
    terms = {"Intercept": np.ones(len(coded))}
    term_order = {"Intercept": 0}
    for order in range(1, max_order + 1):
        for combo in itertools.combinations(cols, order):
            name = "".join(FACTOR_CODES[c] for c in combo)
            val = np.ones(len(coded))
            for c in combo:
                val = val * coded[c].values
            terms[name] = val
            term_order[name] = order
    X = pd.DataFrame(terms)
    return X, term_order


def fit_and_rank_effects(df):
    """
    Full pipeline: code factors, fit saturated model, pool 3-way+ interactions
    as error, compute standardized effects for main effects + 2-way interactions.
    Returns a results dict.
    """
    y = df["Np"].values
    n = len(y)
    coded, levels = code_factors(df)
    X, term_order = build_design_matrix(coded)

    # exact OLS solve (orthogonal design => closed form, but use lstsq for robustness)
    beta, _, _, _ = np.linalg.lstsq(X.values, y, rcond=None)
    beta = pd.Series(beta, index=X.columns)

    # effect = 2 * beta (difference between high-level mean and low-level mean)
    effect = 2 * beta

    # pool higher-order (order >= 3) terms as error
    error_terms = [t for t, o in term_order.items() if o >= 3]
    df_error = len(error_terms)
    ss_error = sum(n * beta[t] ** 2 for t in error_terms)
    ms_error = ss_error / df_error
    se_beta = np.sqrt(ms_error / n)
    se_effect = 2 * se_beta

    keep_terms = [t for t, o in term_order.items() if 1 <= o <= 2]
    t_crit = stats.t.ppf(0.975, df_error)

    results = []
    for t in keep_terms:
        std_effect = abs(effect[t] / se_effect)
        results.append(dict(term=t, order=term_order[t], effect=round(effect[t], 3),
                             standardized_effect=round(std_effect, 2),
                             significant=std_effect > t_crit))
    results = sorted(results, key=lambda r: r["standardized_effect"], reverse=True)

    # fitted values / residuals using ONLY main effects + significant/all 2-way terms
    # (matches thesis: full main+2-way model used for the residual diagnostics)
    model_terms = ["Intercept"] + keep_terms
    X_model = X[model_terms].values
    beta_model, _, _, _ = np.linalg.lstsq(X_model, y, rcond=None)
    fitted = X_model @ beta_model
    residuals = y - fitted
    resid_std = residuals / residuals.std(ddof=len(model_terms))

    return dict(
        levels=levels, effects_table=results, t_crit=round(t_crit, 3), df_error=df_error,
        fitted=fitted, residuals=residuals, resid_std=resid_std, y=y,
        model_terms=model_terms, n=n,
    )
