"""De Loecker, Eeckhout and Unger (2020) on SEC filings, 2011-2025: the aggregate markup.

Rebuilds the paper's main object, the sales-weighted average markup of US public companies,
from the free SEC XBRL panel built by src/fetch_sec.py. For each firm i and year t

    markup_it = theta_st * sales_it / COGS_it

where theta_st is the output elasticity of the variable input (cost of goods sold) in sector s.
The paper's robustness version (its Section VI.A) is used as the main specification: theta_st is
the median across firms in the sector-year of COGS / (COGS + r_t * K_it). A fixed theta of 0.85,
the paper's other robustness check, is also reported.

Outputs (results/):
    aggregate_markup.csv     sales-weighted markup by year, two theta choices, plus weighted percentiles
    decomposition.csv        the paper's equation (9): within, market share, cross term, net entry
    sector_decomposition.csv the paper's equation (10) across sectors, 2011-2016, 2016-2025, 2011-2025
    sector_markups.csv       sector markups and sales shares by year
    firms_named.csv          the largest companies and the companies that moved the aggregate most
    sample_counts.csv        rows loaded, dropped and kept at each rule
    firm_years.csv.gz        the cleaned firm-year panel, used again by src/overhead.py
    markup_trend.png, markup_percentiles.png

Usage (from the repository root):
    python src/markups.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

YEARS = list(range(2011, 2026))   # every filer tags its statements in XBRL from fiscal 2011 on
TRIM = 0.01                       # paper: drop top and bottom 1% of COGS/sales and SG&A/sales, by year
DEPRECIATION_AND_RISK = 0.12      # paper: user cost r = fed funds - inflation + 12%
THETA_FIXED = 0.85                # paper, Figure II(A): fixed output elasticity
DEU_2016 = 1.61                   # paper, Section III.A: benchmark aggregate markup in 2016
DEU_1980 = 1.21                   # paper, Section III.A: benchmark aggregate markup in 1980
META_CIK = 1326801                # SEC registrant number of Meta Platforms (Facebook), for one robustness row
US_STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE "
                "NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split())

# SIC major groups mapped to the paper's two-digit NAICS sectors (nearest equivalent).
SECTORS = [((1, 9), "Agriculture"), ((10, 14), "Mining, oil and gas"), ((15, 17), "Construction"),
           ((20, 39), "Manufacturing"), ((40, 47), "Transportation"), ((48, 48), "Information"),
           ((49, 49), "Utilities"), ((50, 51), "Wholesale trade"), ((52, 57), "Retail trade"),
           ((58, 58), "Accommodation and food"), ((59, 59), "Retail trade"), ((60, 64), "Finance and insurance"),
           ((65, 65), "Real estate"), ((67, 67), "Finance and insurance"), ((70, 70), "Accommodation and food"),
           ((72, 72), "Other services"), ((73, 73), "Business services and software"),
           ((75, 76), "Other services"), ((78, 79), "Arts and entertainment"), ((80, 80), "Health care"),
           ((81, 89), "Professional services")]


def sector_of(sic):
    major = int(sic) // 100
    for (lo, hi), name in SECTORS:
        if lo <= major <= hi:
            return name
    return None


def wmean(x, w):
    return float(np.sum(x * w) / np.sum(w))


def wquantile(x, w, q):
    order = np.argsort(x)
    x, w = np.asarray(x)[order], np.asarray(w)[order]
    cum = np.cumsum(w) / np.sum(w)
    return float(x[np.searchsorted(cum, q)])


def user_cost():
    """r_t = annual fed funds rate - CPI inflation + 12%, all as fractions (paper, Section II.C)."""
    ff = pd.read_csv(RAW / "fred" / "FEDFUNDS.csv", parse_dates=["observation_date"]).dropna()
    cpi = pd.read_csv(RAW / "fred" / "CPIAUCSL.csv", parse_dates=["observation_date"]).dropna()
    df = ff.merge(cpi, on="observation_date")
    df["year"] = df["observation_date"].dt.year
    df["inflation"] = df["CPIAUCSL"].pct_change()
    df["r"] = df["FEDFUNDS"] / 100 - df["inflation"] + DEPRECIATION_AND_RISK
    return df.set_index("year")["r"]


def build_sample():
    fy = pd.read_csv(RAW / "sec_firm_years.csv.gz")
    co = pd.read_csv(RAW / "sec_companies.csv")
    counts = [("filer-years with revenue in the SEC panel", len(fy))]
    df = fy[fy["year"].isin(YEARS)].copy()
    counts.append(("in 2011-2025", len(df)))

    # SG&A: the tagged total, else its two components. Overhead adds R&D, which the paper's
    # Compustat SG&A item contains (the paper reports R&D at 20% of SG&A by 2016).
    parts = df[["g_and_a", "s_and_m"]].sum(axis=1, min_count=1)
    df["sga"] = df["sga_tagged"].fillna(parts)
    df["overhead"] = df["sga"] + df["rd"].fillna(0)
    # COGS rebuilt the way Compustat defines it, from the identity
    #   operating income before depreciation = sales - COGS - SG&A (R&D included in SG&A).
    # XBRL cost-of-revenue tags are often partial (AT&T's equipment cost, UnitedHealth's pharmacy
    # cost), so the identity is used whenever its pieces are filed; otherwise the tagged figure.
    # Operating income from the filing, else gross revenue minus total costs. Where excise taxes were
    # taken out of revenue, the same taxes leave COGS because operating income is unchanged.
    op_income = df["operating_income"].fillna(df["revenue_gross"] - df["costs_and_expenses"])
    df["cogs_identity"] = df["revenue"] - op_income - df["dep_amort"] - df["overhead"]
    df["cogs_reported"] = df["cogs_tagged"].fillna(df["revenue"] - df["gross_profit"])
    # Filers with no SG&A tag (Philip Morris files "marketing, administration and research costs")
    # but with gross profit and operating income: overhead is everything between the two lines.
    below_gross = (df["gross_profit"] - op_income).where(df["sga"].isna() & (df["gross_profit"] > op_income))
    df["overhead"] = df["overhead"].fillna(below_gross)
    # Filers with operating income and depreciation but no SG&A or gross-profit line at all (FedEx,
    # C.H. Robinson) put every operating cost in one list; as in Compustat, it all counts as COGS.
    no_overhead_line = df["overhead"].isna()
    identity_all = df["revenue"] - op_income - df["dep_amort"] - df["rd"].fillna(0)
    df["cogs_identity"] = df["cogs_identity"].fillna(identity_all.where(no_overhead_line))
    use_identity = df["cogs_identity"] > 0
    # Without the identity, a tagged cost line is used only when it is the filer's whole cost of
    # revenue, checked by cost plus gross profit adding up to revenue (within 2% of revenue). Unchecked tags are
    # often one component (DuPont's 2017 tag is $9.6 billion against $62.5 billion of sales).
    # A second check: cost of revenue plus overhead equals total operating costs (Alphabet, 2015-2020).
    checked = (((df["cogs_reported"] + df["gross_profit"] - df["revenue"]).abs() <= 0.02 * df["revenue"])
               | ((df["cogs_reported"] + df["overhead"] - (df["revenue"] - op_income)).abs() <= 0.02 * df["revenue"]))
    df["cogs_reported"] = df["cogs_reported"].where(checked)
    df["cogs"] = df["cogs_identity"].where(use_identity, df["cogs_reported"])
    df["cogs_source"] = np.where(use_identity, np.where(no_overhead_line, "identity, no SG&A line", "identity"),
                                 np.where(df["cogs_reported"].notna(), "tagged", "none"))

    keep = (df["revenue"] > 0) & (df["cogs"] > 0)
    counts.append(("dropped: no positive revenue and COGS", int((~keep).sum())))
    df = df[keep]
    counts.append(("of those kept, COGS from the Compustat identity", int((df["cogs_source"] == "identity").sum())))
    counts.append(("of those kept, COGS from the identity with no SG&A line",
                   int((df["cogs_source"] == "identity, no SG&A line").sum())))
    counts.append(("of those kept, COGS from the cost-of-revenue tag", int((df["cogs_source"] == "tagged").sum())))

    df = df.merge(co[["cik", "name", "sic", "country_of_incorporation", "state_of_incorporation"]],
                  on="cik", how="left")
    us = (df["country_of_incorporation"] == "US") | (
        df["country_of_incorporation"].isna() & df["state_of_incorporation"].isin(US_STATES))
    counts.append(("dropped: incorporated outside the US or state unknown (paper: US-incorporated)", int((~us).sum())))
    df = df[us]
    df["sector"] = df["sic"].map(lambda s: sector_of(s) if pd.notna(s) and s > 0 else None)
    has_sector = df["sector"].notna()
    counts.append(("dropped: no SIC industry code (paper: firms without an industry code excluded)",
                   int((~has_sector).sum())))
    df = df[has_sector].copy()
    fin = df["sic"].between(6000, 6799)
    counts.append(("dropped: banks, insurers and real estate (SIC 6000-6799), whose XBRL cost lines are not COGS",
                   int(fin.sum())))
    df = df[~fin].copy()

    # Paper's trimming: top and bottom 1% of COGS/sales and SG&A/sales, computed year by year.
    df["cogs_share"] = df["cogs"] / df["revenue"]
    df["sga_share"] = df["overhead"] / df["revenue"]
    out = pd.Series(False, index=df.index)
    for col in ["cogs_share", "sga_share"]:
        lo = df.groupby("year")[col].transform(lambda s: s.quantile(TRIM))
        hi = df.groupby("year")[col].transform(lambda s: s.quantile(1 - TRIM))
        out |= df[col].notna() & ((df[col] < lo) | (df[col] > hi))
    counts.append(("dropped: top or bottom 1% of COGS/sales or overhead/sales in its year", int(out.sum())))
    df = df[~out].copy()
    counts.append(("kept: firm-years in the markup sample", len(df)))
    counts.append(("kept: distinct firms", df["cik"].nunique()))
    for label, n in counts:
        print(f"  {label}: {n:,}")
    return df, pd.DataFrame(counts, columns=["step", "rows"])


def sector_theta(df, capital, name):
    """Paper's Section VI.A: theta_st = median over firms in sector s, year t of COGS / (COGS + r K)."""
    share = df["cogs"] / (df["cogs"] + df["r"] * capital)
    return share.groupby([df["sector"], df["year"]]).transform("median").rename(name)


def add_markups(df):
    df["r"] = df["year"].map(user_cost())
    # Capital: the paper uses gross PP&E (PPEGT), but only about one filer-year in eight reports it
    # in XBRL. Where it is missing, gross is imputed as net PP&E times the median gross/net ratio of
    # the filers in the same sector that report both (all years pooled). The imputation only enters
    # through the sector median cost share, so one firm's error moves little.
    ratio = (df["ppe_gross"] / df["ppe_net"]).where((df["ppe_net"] > 0) & (df["ppe_gross"] >= df["ppe_net"]))
    med = ratio.groupby(df["sector"]).transform("median").fillna(ratio.median())
    df["capital"] = df["ppe_gross"].fillna(df["ppe_net"] * med)
    print(f"  capital: gross PP&E reported for {df['ppe_gross'].notna().mean():.0%} of firm-years; "
          f"imputed from net for {(df['ppe_gross'].isna() & df['ppe_net'].notna()).mean():.0%} "
          f"(median gross/net ratio {ratio.median():.2f}); missing for {df['capital'].isna().mean():.0%}")
    df["theta"] = sector_theta(df, df["capital"], "theta")
    df["theta_net_k"] = sector_theta(df, df["ppe_net"], "theta_net_k")
    df["markup"] = df["theta"] * df["revenue"] / df["cogs"]
    df["markup_fixed"] = THETA_FIXED * df["revenue"] / df["cogs"]
    df["markup_net_k"] = df["theta_net_k"] * df["revenue"] / df["cogs"]
    cogs_da = df["cogs"] + df["dep_amort"].where(df["cogs_source"] != "tagged")
    df["markup_incl_da"] = df["theta"] * df["revenue"] / cogs_da
    df["share"] = df["revenue"] / df.groupby("year")["revenue"].transform("sum")
    th = df.groupby(["sector", "year"])["theta"].first()
    print(f"  output elasticity theta: median across sector-years {th.median():.3f}, "
          f"range {th.min():.3f} to {th.max():.3f}")
    return df


def aggregate(df):
    rows = []
    for year, g in df.groupby("year"):
        rows.append({"year": year, "firms": len(g), "sales_trillion": g["revenue"].sum() / 1e12,
                     "markup": wmean(g["markup"], g["revenue"]),
                     "markup_theta_085": wmean(g["markup_fixed"], g["revenue"]),
                     "markup_unweighted_mean": g["markup"].mean(),
                     "p50": wquantile(g["markup"], g["revenue"], 0.50),
                     "p75": wquantile(g["markup"], g["revenue"], 0.75),
                     "p90": wquantile(g["markup"], g["revenue"], 0.90),
                     "theta_sales_weighted": wmean(g["theta"], g["revenue"])})
    return pd.DataFrame(rows)


def robustness(df):
    """The aggregate markup in 2011, 2016 and 2025 under alternative choices."""
    variants = {
        "main: cost-share elasticity, all COGS sources": (df, "markup"),
        "elasticity fixed at 0.85": (df, "markup_fixed"),
        "cost-share elasticity using net PP&E as capital": (df, "markup_net_k"),
        "only firm-years with COGS from the Compustat identity": (df[df["cogs_source"] == "identity"], "markup"),
        "COGS including depreciation (operating costs less overhead)": (df, "markup_incl_da"),
        "firms present in all of 2011, 2016 and 2025": (df[df.groupby("cik")["year"].transform(
            lambda y: {2011, 2016, 2025} <= set(y))], "markup"),
        "manufacturing only": (df[df["sector"] == "Manufacturing"], "markup"),
        "without Meta Platforms, the largest single contributor": (df[df["cik"] != META_CIK], "markup"),
    }
    rows = []
    for label, (d, col) in variants.items():
        vals = {y: wmean(g[col], g["revenue"]) for y, g in d[d[col].notna()].groupby("year") if y in (2011, 2016, 2025)}
        rows.append({"variant": label, "m2011": vals.get(2011), "m2016": vals.get(2016), "m2025": vals.get(2025),
                     "change_2011_2025": vals.get(2025, np.nan) - vals.get(2011, np.nan),
                     "firm_years": int(d[col].notna().sum())})
    return pd.DataFrame(rows)


def decompose(df, col="markup"):
    """Paper's equation (9), year over year, with markups demeaned by last year's aggregate."""
    rows = []
    for t in YEARS[1:]:
        a = df[df["year"] == t - 1].set_index("cik")
        b = df[df["year"] == t].set_index("cik")
        agg0, agg1 = wmean(a[col], a["share"]), wmean(b[col], b["share"])
        both = a.index.intersection(b.index)
        m0, m1 = a.loc[both, "share"], b.loc[both, "share"]
        u0, u1 = a.loc[both, col], b.loc[both, col]
        within = float(np.sum(m0 * (u1 - u0)))
        mshare = float(np.sum((u0 - agg0) * (m1 - m0)))
        cross = float(np.sum((u1 - u0) * (m1 - m0)))
        entry = b.loc[b.index.difference(a.index)]
        exits = a.loc[a.index.difference(b.index)]
        net_entry = float(np.sum((entry[col] - agg0) * entry["share"]) - np.sum((exits[col] - agg0) * exits["share"]))
        total = agg1 - agg0
        assert abs(total - (within + mshare + cross + net_entry)) < 1e-9, "decomposition does not add up"
        rows.append({"year": t, "change": total, "within": within, "market_share": mshare, "cross": cross,
                     "reallocation": mshare + cross, "net_entry": net_entry,
                     "entrants": len(entry), "exits": len(exits), "continuers": len(both)})
    return pd.DataFrame(rows)


def sector_decompose(df, periods):
    """Paper's equation (10): within-sector, between-sector and cross terms."""
    sec = (df.groupby(["year", "sector"])
             .apply(lambda g: pd.Series({"markup": wmean(g["markup"], g["revenue"]), "sales": g["revenue"].sum()}),
                    include_groups=False)
             .reset_index())
    sec["share"] = sec["sales"] / sec.groupby("year")["sales"].transform("sum")
    rows = []
    for t0, t1 in periods:
        a = sec[sec["year"] == t0].set_index("sector")
        b = sec[sec["year"] == t1].set_index("sector")
        s = a.index.intersection(b.index)
        dmu, dm = b.loc[s, "markup"] - a.loc[s, "markup"], b.loc[s, "share"] - a.loc[s, "share"]
        rows.append({"from": t0, "to": t1, "markup_from": wmean(a["markup"], a["share"]),
                     "markup_to": wmean(b["markup"], b["share"]),
                     "change": wmean(b["markup"], b["share"]) - wmean(a["markup"], a["share"]),
                     "within": float(np.sum(a.loc[s, "share"] * dmu)),
                     "between": float(np.sum(a.loc[s, "markup"] * dm)), "cross": float(np.sum(dmu * dm))})
    return pd.DataFrame(rows), sec


def named_firms(df):
    t0, t1 = YEARS[0], YEARS[-1]
    keep = ["cik", "name", "sector", "revenue", "markup", "share"]
    a = df[df["year"] == t0][keep].set_index("cik")
    m = df[df["year"] == 2016][["cik", "markup"]].set_index("cik")["markup"].rename("markup_2016")
    b = df[df["year"] == t1][keep].set_index("cik")
    f = b.join(a[["markup", "share"]].add_suffix(f"_{t0}")).join(m)
    f = f.rename(columns={"markup": f"markup_{t1}", "share": f"share_{t1}", "revenue": f"revenue_{t1}"})
    # Each firm's contribution to the change in the sales-weighted average, measured against the
    # 2011 average so that contributions sum to the aggregate change (firms that left the sample
    # after 2011 make up the rest).
    base = wmean(a["markup"], a["share"])
    f["contribution"] = (f[f"share_{t1}"] * (f[f"markup_{t1}"] - base)
                         - (f[f"share_{t0}"] * (f[f"markup_{t0}"] - base)).fillna(0))
    largest = f.sort_values(f"revenue_{t1}", ascending=False).head(20).assign(list="largest by 2025 sales")
    movers = f.sort_values("contribution", ascending=False).head(15).assign(list="largest contribution to the rise")
    out = pd.concat([largest, movers]).reset_index()
    out[f"revenue_{t1}"] = out[f"revenue_{t1}"] / 1e9
    return out.rename(columns={f"revenue_{t1}": f"revenue_{t1}_billion"})


def plot_trend(agg):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(agg["year"], agg["markup"], color="#1f4e79", lw=2.2, marker="o", ms=4,
            label="Sales-weighted markup, cost-share elasticity")
    ax.plot(agg["year"], agg["markup_theta_085"], color="#7aa6c2", lw=1.6, ls="--",
            label="Same, elasticity fixed at 0.85")
    ax.scatter([2016], [DEU_2016], color="#c0504d", zorder=5, s=55, label="De Loecker et al., 2016 (1.61)")
    ax.axhline(DEU_1980, color="#999999", lw=0.8, ls=":")
    ax.text(2011.1, DEU_1980 + 0.01, "Their 1980 level (1.21)", fontsize=8, color="#666666")
    ax.set_ylabel("Price over marginal cost")
    ax.set_title("Aggregate markup of US public companies, SEC filings 2011-2025")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "markup_trend.png", dpi=150)
    plt.close(fig)


def plot_percentiles(agg):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for col, label, color in [("p90", "90th percentile", "#1f4e79"), ("p75", "75th percentile", "#4f81bd"),
                              ("markup", "Average", "#c0504d"), ("p50", "Median", "#7f7f7f")]:
        ax.plot(agg["year"], agg[col], label=label, color=color, lw=2 if col == "markup" else 1.6)
    ax.set_ylabel("Price over marginal cost (sales-weighted)")
    ax.set_title("The markup distribution, 2011-2025")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "markup_percentiles.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    print("Loading SEC firm-year panel")
    df, counts = build_sample()
    df = add_markups(df)
    agg = aggregate(df)
    dec = decompose(df)
    sdec, sec = sector_decompose(df, [(2011, 2016), (2016, 2025), (2011, 2025)])
    named = named_firms(df)
    robust = robustness(df)

    counts.to_csv(OUT / "sample_counts.csv", index=False)
    agg.round(6).to_csv(OUT / "aggregate_markup.csv", index=False)
    dec.round(6).to_csv(OUT / "decomposition.csv", index=False)
    sdec.round(6).to_csv(OUT / "sector_decomposition.csv", index=False)
    sec.round(6).to_csv(OUT / "sector_markups.csv", index=False)
    named.round(6).to_csv(OUT / "firms_named.csv", index=False)
    robust.round(6).to_csv(OUT / "robustness.csv", index=False)
    cols = ["cik", "name", "year", "sector", "sic", "revenue", "cogs", "cogs_source", "cogs_reported", "sga", "rd",
            "overhead",
            "capital", "r", "theta", "markup", "markup_fixed", "share"]
    df[cols].to_csv(OUT / "firm_years.csv.gz", index=False, float_format="%.6g",
                   compression={"method": "gzip", "mtime": 0})  # fixed header, so reruns are byte-identical
    plot_trend(agg)
    plot_percentiles(agg)

    a0, a1 = agg.iloc[0], agg.iloc[-1]
    a16 = agg[agg["year"] == 2016].iloc[0]
    print(f"Aggregate markup: {a0['markup']:.3f} in {int(a0['year'])}, {a16['markup']:.3f} in 2016 "
          f"(paper: {DEU_2016}), {a1['markup']:.3f} in {int(a1['year'])}")
    print(f"Median markup: {a0['p50']:.3f} -> {a1['p50']:.3f}; 90th percentile: {a0['p90']:.3f} -> {a1['p90']:.3f}")
    tot = dec[["change", "within", "market_share", "cross", "reallocation", "net_entry"]].sum()
    print("Cumulative decomposition 2011-2025: " + ", ".join(f"{k} {v:+.3f}" for k, v in tot.items()))
    print(f"Wrote results to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
