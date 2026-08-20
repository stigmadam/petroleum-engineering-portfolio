"""
plots.py
--------
Pareto chart and residual diagnostic plots (Normal Probability Plot,
Residuals vs. Fitted), replicating the standard Minitab DOE output style
used in the thesis, plus the log-transform diagnostic comparison.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def pareto_chart(results, t_crit, field_name, save_path):
    terms = [r["term"] for r in results]
    vals = [r["standardized_effect"] for r in results]
    colors = ["#c2542c" if r["significant"] else "#a8adb5" for r in results]

    fig, ax = plt.subplots(figsize=(8, 6.5))
    y_pos = np.arange(len(terms))[::-1]
    ax.barh(y_pos, vals, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(terms, fontsize=9)
    ax.axvline(t_crit, color="red", ls="--", lw=1.2)
    ax.text(t_crit + 0.5, len(terms) - 1, f"{t_crit}", color="red", fontsize=9)
    ax.set_xlabel("Standardized Effect")
    ax.set_title(f"Pareto Chart of Standardized Effects — Field {field_name}\n(response is Np, α = 0.05)")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def residual_diagnostics(resid_std, fitted, field_name, save_path, response_label="Np"):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    stats.probplot(resid_std, dist="norm", plot=axes[0])
    axes[0].set_title(f"Normal Probability Plot — Field {field_name}")
    axes[0].get_lines()[0].set_markerfacecolor("#2f6fa8")
    axes[0].get_lines()[0].set_markeredgecolor("#2f6fa8")
    axes[0].get_lines()[1].set_color("#c2542c")

    axes[1].scatter(fitted, resid_std, color="#2f6fa8", s=22)
    axes[1].axhline(0, color="gray", ls="--", lw=1)
    axes[1].set_xlabel(f"Fitted Value ({response_label})")
    axes[1].set_ylabel("Standardized Residual")
    axes[1].set_title(f"Residuals vs. Fitted — Field {field_name}")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def comparison_bar(field_results, save_path):
    """Compare top-5 standardized effects across all 3 fields."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
    for ax, (field, res) in zip(axes, field_results.items()):
        top5 = res["effects_table"][:5]
        terms = [r["term"] for r in top5][::-1]
        vals = [r["standardized_effect"] for r in top5][::-1]
        ax.barh(terms, vals, color="#1f6f4a")
        ax.set_title(f"Field {field}")
        ax.set_xlabel("Standardized Effect")
    plt.suptitle("Top 5 Influential Terms — Cross-Field Comparison", y=1.03)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
