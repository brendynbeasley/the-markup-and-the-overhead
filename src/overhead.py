"""The extension: Traina's counter-test, counting overhead (SG&A) as a variable cost.

Traina (2018) argued that the De Loecker-Eeckhout-Unger markup rises partly because cost of goods
sold leaves out selling, general and administrative spending, a growing share of what firms spend
to make and sell their products. His measure, written in the paper's own notation (its eq. 17), is

    tau_it = theta_(V+X),st * sales_it / (COGS_it + SGA_it)

This script computes tau on the same firms and years as the COGS-based markup, tests whether the
two trends differ, and tracks the operating margin after COGS and overhead (the paper's eq. 18),
to which tau is tied by tau = theta / (1 - margin).

Run src/markups.py first; this script reads results/firm_years.csv.gz.

Outputs (results/):
    overhead_aggregate.csv   by year: COGS markup and tau on the matched sample, overhead and margin
    trend_tests.csv          firm fixed-effect trend regressions, sales-weighted, clustered by firm
    bootstrap_changes.csv    2011-2025 change in each aggregate, firm-resampling bootstrap
    firms_overhead.csv       the named firms with both measures
    overhead_vs_markup.png

Usage (from the repository root):
    python src/overhead.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results"

FIRST, LAST = 2011, 2025
THETA_TRAINA_FIXED = 0.95   # paper, Section IV.B: Traina's elasticity "approximately 0.95"
DEU_TAU_1980, DEU_TAU_2016 = 1.08, 1.18   # paper, Section IV.B: tau rose from 1.08 to 1.18
BOOT_REPS = 500             # firm-level bootstrap draws
SEED = 1980


def wmean(x, w):
    return float(np.sum(x * w) / np.sum(w))


def load():
    df = pd.read_csv(OUT / "firm_years.csv.gz")
    n0 = len(df)
    df = df[df["overhead"] > 0].copy()
    print(f"  loaded {n0:,} firm-years; kept {len(df):,} with an overhead (SG&A) figure (dropped {n0 - len(df):,})")
    df["share"] = df["revenue"] / df.groupby("year")["revenue"].transform("sum")
    # Traina's elasticity from cost shares, the same way as the COGS elasticity in markups.py.
    rk = df["r"] * df["capital"]
    df["cost_share_vx"] = (df["cogs"] + df["overhead"]) / (df["cogs"] + df["overhead"] + rk)
    theta_vx = df.groupby(["sector", "year"])["cost_share_vx"].median().rename("theta_vx")
    df = df.merge(theta_vx, left_on=["sector", "year"], right_index=True, how="left")
    df["tau"] = df["theta_vx"] * df["revenue"] / (df["cogs"] + df["overhead"])
    df["tau_fixed"] = THETA_TRAINA_FIXED * df["revenue"] / (df["cogs"] + df["overhead"])
    df["tau_sga_only"] = df["theta_vx"] * df["revenue"] / (df["cogs"] + df["sga"])
    df["operating_margin"] = 1 - (df["cogs"] + df["overhead"]) / df["revenue"]   # paper's eq. 18
    print(f"  Traina elasticity theta_(V+X): median across sector-years {theta_vx.median():.3f}")
    return df


def aggregate(df):
    rows = []
    for year, g in df.groupby("year"):
        w = g["revenue"]
        total_cost = g["cogs"] + g["overhead"] + (g["r"] * g["capital"]).fillna(0)  # paper's eq. 13 costs
        rows.append({"year": year, "firms": len(g),
                     "markup_cogs": wmean(g["markup"], w), "tau": wmean(g["tau"], w),
                     "tau_theta_095": wmean(g["tau_fixed"], w), "tau_sga_without_rd": wmean(g["tau_sga_only"], w),
                     "overhead_share_of_cost": g["overhead"].sum() / total_cost.sum(),
                     "cogs_share_of_sales": g["cogs"].sum() / w.sum(),
                     "overhead_share_of_sales": g["overhead"].sum() / w.sum(),
                     "operating_margin": wmean(g["operating_margin"], w),
                     "user_cost_r": g["r"].iloc[0],
                     "theta_cogs": wmean(g["theta"], w), "theta_vx": wmean(g["theta_vx"], w)})
    return pd.DataFrame(rows)


def trend_test(df, col, log=True):
    """y_it = a_i + b * (year - 2011) + e_it, weights = sales share in the year, SEs clustered by firm.

    y is ln(col) for the markups (b is then the proportional change per year) and the level for the
    operating margin, which can be negative.
    """
    d = df[["cik", "year", "share", col]].dropna()
    if log:
        d = d[d[col] > 0]
    d = d[d.groupby("cik")["year"].transform("count") >= 2]
    d["y"] = np.log(d[col]) if log else d[col]
    d["t"] = d["year"] - FIRST
    w = d["share"]
    for v in ["y", "t"]:  # weighted within-firm demeaning (absorbs the firm fixed effect)
        d[v + "_dm"] = d[v] - (d[v] * w).groupby(d["cik"]).transform("sum") / w.groupby(d["cik"]).transform("sum")
    fit = sm.WLS(d["y_dm"], d[["t_dm"]], weights=w).fit(cov_type="cluster", cov_kwds={"groups": d["cik"]})
    b, se = fit.params["t_dm"], fit.bse["t_dm"]
    return {"outcome": f"ln({col})" if log else col, "slope_per_year": b, "se": se, "ci_low": b - 1.96 * se,
            "ci_high": b + 1.96 * se, "p_value": fit.pvalues["t_dm"], "n_firm_years": len(d),
            "n_firms": d["cik"].nunique()}


def bootstrap(df, cols):
    """Resample firms with replacement; recompute each sales-weighted aggregate's 2011-2025 change."""
    rng = np.random.default_rng(SEED)
    d = df[df["year"].isin([FIRST, LAST])][["cik", "year", "revenue"] + cols]
    firms = d["cik"].unique()
    by_firm = {k: g for k, g in d.groupby("cik")}

    def change(frame):
        a, b = frame[frame["year"] == FIRST], frame[frame["year"] == LAST]
        return {c: wmean(b[c], b["revenue"]) - wmean(a[c], a["revenue"]) for c in cols}

    point = change(d)
    draws = []
    for _ in range(BOOT_REPS):
        pick = rng.choice(firms, size=len(firms), replace=True)
        draws.append(change(pd.concat([by_firm[k] for k in pick], ignore_index=True)))
    draws = pd.DataFrame(draws)
    draws["gap"] = draws["markup"] - draws["tau"]
    point["gap"] = point["markup"] - point["tau"]
    draws["tau_rise_over_markup_rise"] = draws["tau"] / draws["markup"]
    point["tau_rise_over_markup_rise"] = point["tau"] / point["markup"]
    rows = [{"measure": c, "change_2011_2025": point[c], "boot_se": draws[c].std(),
             "ci_low": draws[c].quantile(0.025), "ci_high": draws[c].quantile(0.975),
             "share_of_draws_above_zero": float((draws[c] > 0).mean())} for c in cols + ["gap", "tau_rise_over_markup_rise"]]
    return pd.DataFrame(rows)


def plot(agg):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.8))
    ax1.plot(agg["year"], agg["markup_cogs"], color="#1f4e79", lw=2.2, marker="o", ms=4,
             label="COGS as the variable cost (De Loecker et al.)")
    ax1.plot(agg["year"], agg["tau"], color="#c0504d", lw=2.2, marker="s", ms=4,
             label="COGS + SG&A as the variable cost (Traina)")
    ax1.set_ylabel("Price over marginal cost")
    ax1.set_title("Two markups, same firms")
    ax1.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    ax2.plot(agg["year"], 100 * agg["overhead_share_of_sales"], color="#7f7f7f", lw=2, label="SG&A and R&D, % of sales")
    ax2.plot(agg["year"], 100 * agg["operating_margin"], color="#c0504d", lw=2,
             label="Sales less COGS, SG&A and R&D, % of sales")
    ax2.set_title("Overhead and margin")
    ax2.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "overhead_vs_markup.png", dpi=150)
    plt.close(fig)


def main():
    print("Loading the cleaned panel from results/firm_years.csv.gz")
    df = load()
    agg = aggregate(df)
    tests = pd.DataFrame([trend_test(df, c) for c in ["markup", "tau", "tau_fixed"]]
                         + [trend_test(df, "operating_margin", log=False)])
    df["markup_over_tau"] = df["markup"] / df["tau"]
    tests = pd.concat([tests, pd.DataFrame([trend_test(df, "markup_over_tau")])], ignore_index=True)
    boot = bootstrap(df, ["markup", "tau", "operating_margin"])

    named = pd.read_csv(OUT / "firms_named.csv")
    t = df[df["year"].isin([FIRST, LAST])].pivot_table(index="cik", columns="year",
                                                        values=["tau", "overhead", "revenue", "theta_vx"])
    t.columns = [f"{a}_{b}" for a, b in t.columns]
    t[f"overhead_share_{LAST}"] = t[f"overhead_{LAST}"] / t[f"revenue_{LAST}"]
    t[f"overhead_{LAST}_billion"] = t[f"overhead_{LAST}"] / 1e9
    keep = [f"tau_{FIRST}", f"tau_{LAST}", f"theta_vx_{LAST}", f"overhead_{LAST}_billion", f"overhead_share_{LAST}"]
    named = named.merge(t[keep], left_on="cik",
                        right_index=True, how="left")

    agg.round(6).to_csv(OUT / "overhead_aggregate.csv", index=False)
    tests.to_csv(OUT / "trend_tests.csv", index=False, float_format="%.8f")
    boot.round(6).to_csv(OUT / "bootstrap_changes.csv", index=False)
    named.round(6).to_csv(OUT / "firms_overhead.csv", index=False)
    plot(agg)

    a0, a1 = agg.iloc[0], agg.iloc[-1]
    print(f"Matched sample: COGS markup {a0['markup_cogs']:.3f} -> {a1['markup_cogs']:.3f}; "
          f"tau {a0['tau']:.3f} -> {a1['tau']:.3f} (paper's 2016 tau: {DEU_TAU_2016})")
    print(f"Operating margin {a0['operating_margin']:.3f} -> {a1['operating_margin']:.3f}")
    print(tests[["outcome", "slope_per_year", "se", "p_value", "n_firm_years"]].to_string(index=False))
    print(boot.to_string(index=False))


if __name__ == "__main__":
    main()
