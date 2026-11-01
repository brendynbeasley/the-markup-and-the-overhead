"""Build the firm-year panel of US public companies from the SEC Financial Statement Data Sets.

De Loecker, Eeckhout and Unger (2020) use Compustat, which is licensed. Compustat itself is
transcribed from the annual reports companies file with the SEC, and since 2009-2011 those reports
are also filed in machine-readable XBRL form. The SEC publishes every XBRL figure from every filing
each quarter as the Financial Statement Data Sets (FSDS): sub.txt (one row per filing, with the
filer's SIC industry code and country of incorporation) and num.txt (one row per reported number).

Every 10-K reports three years of income statement and two years of balance sheet. The 60 quarterly
releases from 2011 Q3 to 2026 Q2 hold every annual report filed in that span (2011 Q3 is the first
quarter in which every filer, small companies included, had to tag its statements), so they cover
fiscal years 2011 to 2025; where a figure appears in more than one report, the latest filing (which carries
any restatement) is kept.

It writes two compact files that are committed, so the analysis runs offline:
    data/raw/sec_firm_years.csv.gz   one row per filer and fiscal year, values in US dollars
    data/raw/sec_companies.csv       one row per filer: name, SIC code, country and state of incorporation

The quarterly zip files (60 to 130 MB each, about 5.6 GB in all) are saved in data/raw/sec/ (ignored by git).

Usage (from the repository root):
    python src/fetch_sec.py                     # download what is missing, then build
    python src/fetch_sec.py --zips <folder>     # build from zip files already on disk
"""

import io
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# SEC asks automated clients to identify themselves and to stay under ten requests a second.
HEADERS = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com"}
FSDS_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{}.zip"
# If sec.gov refuses the request (it rate-limits shared network addresses), the Internet Archive's
# copy of the same URL is used. The files used here were fetched that way on 1 November 2026.
ARCHIVE_URL = "https://web.archive.org/web/2026id_/{}"
QUARTERS = ["2011q3", "2011q4"] + [f"{y}q{q}" for y in range(2012, 2026) for q in (1, 2, 3, 4)] + ["2026q1", "2026q2"]
FISCAL_YEARS = range(2011, 2026)
FORMS = {"10-K", "10-K/A", "10-KT"}

# Each item is filed under one of several us-gaap tags depending on the year and the filer.
# For revenue the largest value across tags is kept (some filers report a sub-total under one tag).
# Compustat records sales net of excise taxes, so where a filer reports excise taxes inside revenue
# (Philip Morris, for example) they are taken out; see net_of_excise() below.
REVENUE_TAGS = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "SalesRevenueGoodsNet", "SalesRevenueServicesNet",
                "SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes"]  # oil companies before 2018
NET_REVENUE_TAGS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]
# Cost of goods sold, the paper's variable input (Compustat COGS): totals first, then narrower tags.
COGS_TAGS = ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
             "CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization", "CostOfServices"]
ITEMS = {  # output column -> tags in priority order (first tag present wins)
    "excise": ["ExciseAndSalesTaxes"],
    "cogs_tagged": COGS_TAGS,
    "gross_profit": ["GrossProfit"],
    "sga_tagged": ["SellingGeneralAndAdministrativeExpense"],
    "g_and_a": ["GeneralAndAdministrativeExpense"],
    "s_and_m": ["SellingAndMarketingExpense", "SellingExpense", "MarketingExpense"],
    "rd": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
    # Operating income and depreciation, used to rebuild Compustat's COGS from its accounting identity
    # (operating income before depreciation = sales - COGS - SG&A, with R&D inside SG&A).
    "operating_income": ["OperatingIncomeLoss"],
    "costs_and_expenses": ["CostsAndExpenses"],
    "dep_amort": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                  "DepreciationAmortizationAndAccretionNet", "Depreciation"],
    # Capital: the paper uses gross property, plant and equipment (PPEGT); net is the fallback.
    "ppe_gross": ["PropertyPlantAndEquipmentGross"],
    "ppe_net": ["PropertyPlantAndEquipmentNet",
                "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization"],
}
INSTANT = {"ppe_gross", "ppe_net"}
ALL_TAGS = set(REVENUE_TAGS) | {t for tags in ITEMS.values() for t in tags}


def net_of_excise(out, flows):
    """Take excise taxes out of revenue where a filer reports them inside it.

    Revenue becomes gross revenue minus excise taxes when that figure matches the filer's own cost of
    goods plus gross profit (within 2%), or when it is at least as large as the filer's largest
    explicitly net revenue tag; otherwise the revenue figure already excludes the taxes.
    """
    net = flows[flows["tag"].isin(NET_REVENUE_TAGS)].groupby(["cik", "year"])["value"].max().reindex(out.index)
    candidate = out["revenue"] - out["excise"]
    parts = out["cogs_tagged"] + out["gross_profit"]
    matches_parts = (candidate - parts).abs() <= 0.02 * parts
    not_below_net = candidate >= net.fillna(0) * 0.98
    use = (out["excise"] > 0) & (candidate > 0) & (matches_parts | (parts.isna() & not_below_net))
    out["revenue_gross"] = out["revenue"]
    out.loc[use, "revenue"] = candidate[use]
    return out


def zip_path(q, folder):
    path = folder / f"{q}.zip"
    if not path.exists():
        url = FSDS_URL.format(q)
        print(f"  downloading {url}")
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=900)
        if r.status_code != 200 or not r.content.startswith(b"PK"):
            print(f"  sec.gov answered {r.status_code}; using the Internet Archive copy")
            r = requests.get(ARCHIVE_URL.format(url), headers=HEADERS, timeout=900)
            r.raise_for_status()
        folder.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".part")
        tmp.write_bytes(r.content)
        tmp.rename(path)
    return path


def read_quarter(path):
    """Return (filings, numbers) for one quarterly zip, keeping annual reports and the tags we use."""
    with zipfile.ZipFile(path) as z:
        sub = pd.read_csv(io.BytesIO(z.read("sub.txt")), sep="\t", dtype=str,
                          usecols=["adsh", "cik", "name", "sic", "countryinc", "stprinc", "form", "period", "filed"])
        sub = sub[sub["form"].isin(FORMS)]
        num = pd.read_csv(io.BytesIO(z.read("num.txt")), sep="\t", dtype=str, quoting=3,
                          usecols=lambda c: c in {"adsh", "tag", "coreg", "ddate", "qtrs", "uom",
                                                  "value", "segments"})
    # Tags are matched by name. Filers sometimes declare a standard us-gaap name in their own
    # extension (Exxon's revenue tag in its 2016 report), so the taxonomy version is not checked.
    num = num[num["adsh"].isin(sub["adsh"]) & num["tag"].isin(ALL_TAGS) & (num["uom"] == "USD")
              & num["coreg"].isna()]
    if "segments" in num.columns:  # keep consolidated totals, not segment or geographic breakdowns
        num = num[num["segments"].isna()]
    num = num[num["qtrs"].isin(["0", "4"])]
    num = num.merge(sub[["adsh", "cik", "filed"]], on="adsh")
    num["value"] = pd.to_numeric(num["value"], errors="coerce")
    return sub, num[["cik", "tag", "ddate", "qtrs", "value", "filed"]]


def fiscal_year(ddate):
    """Compustat's convention: a fiscal year ending January-May belongs to the previous year."""
    d = pd.to_datetime(ddate, format="%Y%m%d", errors="coerce")
    return d.dt.year.where(d.dt.month >= 6, d.dt.year - 1)


def build(folder):
    subs, nums = [], []
    for q in QUARTERS:
        sub, num = read_quarter(zip_path(q, folder))
        subs.append(sub.assign(quarter=q))
        nums.append(num)
        print(f"  {q}: {len(sub):,} annual reports, {len(num):,} usable figures")
    num = pd.concat(nums, ignore_index=True)
    # The same figure appears in up to three filings; keep the most recently filed (restated) value.
    # If one filing reports two values for the same item and date, the larger (the total) is kept.
    num = num.sort_values(["filed", "value"]).drop_duplicates(["cik", "tag", "ddate", "qtrs"], keep="last")
    num["year"] = fiscal_year(num["ddate"])
    num = num[num["year"].isin(FISCAL_YEARS)]
    # Keep a filer's figures only for fiscal years it filed its own annual report for. This drops
    # comparatives a successor company restates for years before it existed (the new Walt Disney
    # holding company formed in 2019 reports 2017 and 2018, which the old Disney already filed).
    own = pd.concat(subs)[["cik", "period"]].assign(year=lambda d: fiscal_year(d["period"]))
    own = own[["cik", "year"]].drop_duplicates()
    n0 = len(num)
    num = num.merge(own, on=["cik", "year"])
    print(f"  dropped {n0 - len(num):,} figures for years before the filer's first own annual report")
    # If a filer changed its fiscal year end, keep the latest period end within the fiscal year.
    num = num.sort_values("ddate").drop_duplicates(["cik", "tag", "year", "qtrs"], keep="last")

    flows, stocks = num[num["qtrs"] == "4"], num[num["qtrs"] == "0"]
    rev = flows[flows["tag"].isin(REVENUE_TAGS)].groupby(["cik", "year"])["value"].max().rename("revenue")
    out = rev.to_frame()
    for col, tags in ITEMS.items():
        src = stocks if col in INSTANT else flows
        d = src[src["tag"].isin(tags)].copy()
        d["rank"] = d["tag"].map({t: i for i, t in enumerate(tags)})
        d = d.sort_values("rank").drop_duplicates(["cik", "year"])
        out = out.join(d.set_index(["cik", "year"])["value"].rename(col), how="left")
        if col == "cogs_tagged":
            out = out.join(d.set_index(["cik", "year"])["tag"].rename("cogs_tag"), how="left")
    out = net_of_excise(out, flows).reset_index()

    sub = pd.concat(subs, ignore_index=True).sort_values("filed")
    co = sub.drop_duplicates("cik", keep="last")[["cik", "name", "sic", "countryinc", "stprinc"]]
    co = co.rename(columns={"countryinc": "country_of_incorporation", "stprinc": "state_of_incorporation"})
    return out, co


def main():
    folder = Path(sys.argv[sys.argv.index("--zips") + 1]) if "--zips" in sys.argv else RAW / "sec"
    print(f"Building firm-year panel from {len(QUARTERS)} quarterly SEC Financial Statement Data Sets")
    fy, co = build(folder)
    fy = fy[fy["cik"].isin(co["cik"])]
    fy.to_csv(RAW / "sec_firm_years.csv.gz", index=False, float_format="%.0f",
              compression={"method": "gzip", "mtime": 0})
    co.to_csv(RAW / "sec_companies.csv", index=False)
    print(f"Wrote data/raw/sec_firm_years.csv.gz: {len(fy):,} filer-years, {fy['cik'].nunique():,} filers")
    print(f"Wrote data/raw/sec_companies.csv: {len(co):,} filers")


if __name__ == "__main__":
    main()
