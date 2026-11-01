# Technical notes

This is the technical companion to the [README](README.md). It covers the data, the method, the full set of test
statistics and how to reproduce everything. Every table is in [results/FINDINGS.md](results/FINDINGS.md), and a
review of the original paper's methods is in [METHODS_REVIEW.md](METHODS_REVIEW.md).

## The original study

Jan De Loecker, Jan Eeckhout and Gabriel Unger, "The Rise of Market Power and the Macroeconomic Implications,"
*Quarterly Journal of Economics* 135(2), 2020, pp. 561–644. Using Compustat for US-incorporated public firms,
1955–2016 (247,644 firm-years with sales, COGS and SG&A, Appendix Table B.1), they compute firm markups by the
production approach and report a sales-weighted average of 1.21 in 1980 and 1.61 in 2016 (Section III.A), a flat
median with a rising upper tail (Figure III), reallocation toward high-markup firms accounting for about two-thirds of
the rise (Figure IV), an average profit rate rising from 1% to 8% of sales (abstract), and Traina's COGS-plus-SG&A
measure rising from 1.08 to 1.18 (Section IV.B).

## Headline results

| | 2011 | 2016 | 2025 | Change 2011–2025 |
|---|---|---|---|---|
| Aggregate markup, cost-share elasticity (paper's Section VI.A) | 1.529 | 1.613 | 1.793 | +0.264 |
| Aggregate markup, elasticity fixed at 0.85 (paper's Figure II.A) | 1.393 | 1.500 | 1.661 | +0.268 |
| Paper's benchmark | | 1.61 | | |
| Sales-weighted median markup | 1.293 | 1.312 | 1.323 | +0.030 |
| Sales-weighted 90th percentile | 2.182 | 2.259 | 2.803 | +0.621 |
| COGS markup, firms reporting overhead | 1.584 | 1.674 | 1.878 | +0.294 |
| Traina's measure, same firms | 1.154 | 1.144 | 1.214 | +0.060 |

## Data

- **SEC Financial Statement Data Sets**, quarterly releases 2011 Q3 through 2026 Q2 (60 zip files, about 5.6 GB),
  from `https://www.sec.gov/files/dera/data/financial-statement-data-sets/<quarter>.zip`. On 1 November 2026 sec.gov
  was refusing requests from the shared network address used for this work, so the files were retrieved from the
  Internet Archive's copies of those exact URLs (snapshots dated January to October 2026). `src/fetch_sec.py` tries
  sec.gov first and falls back to the archive. The zips are not committed; the compact panel built from them is:
  `data/raw/sec_firm_years.csv.gz` (70,983 filer-years) and `data/raw/sec_companies.csv` (SIC code, country and state
  of incorporation for 14,020 filers).
- **FRED**, annual averages of `FEDFUNDS` and `CPIAUCSL`, downloaded 1 November 2026 to `data/raw/fred/`.

## Method

Rules fixed before looking at the aggregate series:

- **Firm-year:** fiscal year by Compustat's convention (a year ending January to May belongs to the prior year).
  Figures come from the filer's own 10-K, 10-K/A or 10-KT, consolidated only; when a figure is restated, the latest
  filing wins. A filer's figures count only for fiscal years in which it filed its own annual report, which drops
  comparatives a successor company restates for its predecessor.
- **Sales:** largest of the revenue tags, net of excise taxes where the filer reports them inside revenue.
- **COGS:** Compustat's identity, sales less operating income less depreciation and amortization less SG&A less R&D.
  Without it, the filer's cost-of-revenue tag, accepted only if it plus gross profit equals sales, or it plus overhead
  equals operating costs, within 2% of sales. Filers with no SG&A or gross-profit line count all operating costs
  other than depreciation and R&D as COGS.
- **Overhead $`X`$:** SG&A (or its selling and administrative components) plus R&D, matching the paper's Compustat
  SG&A, which contains R&D.
- **Sample:** positive sales and COGS; US-incorporated; an SIC code; SIC 6000–6799 (banks, insurers, real estate)
  excluded, a departure from the paper; top and bottom 1% of COGS/sales and overhead/sales dropped within each year,
  as in the paper.
- **Elasticity:** $`\theta_{st}`$ is the median over firms in sector $`s`$ and year $`t`$ of
  $`\mathit{COGS}/(\mathit{COGS} + r_t K)`$, with 15 sectors built from SIC major groups to match two-digit NAICS sectors,
  $`r_t`$ the fed funds rate less CPI inflation plus 12%, and $`K`$ gross PP&E, imputed where missing (83% of
  firm-years) as net PP&E times the sector's median gross/net ratio. Unlike the paper, $`K`$ is not deflated by an
  industry input price index.
- **Known weakness of the identity:** every operating expense that is not SG&A, R&D or depreciation falls into
  COGS, including litigation provisions and impairments. Mastercard, which files no cost-of-sales line, is the
  clearest case among the named firms.

The markup and its aggregate:

```math
\mu_{it} = \theta_{st}\,\frac{S_{it}}{\mathit{COGS}_{it}},
\qquad M_t = \sum_i m_{it}\,\mu_{it},
\qquad m_{it} = \frac{S_{it}}{\sum_j S_{jt}}
```

The paper's firm-level decomposition (its equation 9), with $`\tilde\mu_{i,t-1} = \mu_{i,t-1} - M_{t-1}`$ and entrants
and exiters demeaned by $`M_{t-1}`$:

```math
\begin{aligned}
\Delta M_t &= \textstyle\sum_{i \in C} m_{i,t-1}\Delta\mu_{it}
 + \sum_{i \in C}\tilde\mu_{i,t-1}\Delta m_{it}
 + \sum_{i \in C}\Delta\mu_{it}\Delta m_{it} \\
&\quad + \textstyle\sum_{i \in N}(\mu_{it} - M_{t-1})\,m_{it}
 - \sum_{i \in E}(\mu_{i,t-1} - M_{t-1})\,m_{i,t-1}
\end{aligned}
```

$`C`$ is continuing firms, $`N`$ entrants and $`E`$ exiters. The script checks that the terms add to $`\Delta M_t`$.

Traina's measure (the paper's equation 17), with $`\theta^{V+X}_{st}`$ the sector-year median of
$`(\mathit{COGS} + X)/(\mathit{COGS} + X + r_t K)`$:

```math
\tau_{it} = \theta^{V+X}_{st}\,\frac{S_{it}}{\mathit{COGS}_{it} + X_{it}}
```

The within-firm trend, on firm-years that also report overhead (the sample of Traina's measure), firms with at least
two years, weighted by $`m_{it}`$, firm fixed effects absorbed by weighted demeaning, standard errors clustered by
firm:

```math
y_{it} = \alpha_i + \beta\,(t - 2011) + \varepsilon_{it},
\qquad H_0:\ \beta = 0
```

Here $`y_{it}`$ is the log COGS markup, the log of Traina's measure, the operating margin or the log ratio of the two
markups. Changes in aggregates from 2011 to 2025 use a firm bootstrap on the same overhead sample (500 draws, seed
1980, elasticities held at their sample values).

## Test statistics

Within-firm trends (`results/trend_tests.csv`), 38,938 firm-years, 5,412 firms:

| Outcome | $`\hat\beta`$ per year | SE | 95% CI | p |
|---|---|---|---|---|
| ln COGS markup | −0.00079 | 0.00086 | [−0.00247, 0.00089] | 0.354 |
| ln Traina's measure | 0.00117 | 0.00072 | [−0.00024, 0.00257] | 0.104 |
| ln Traina's measure, θ = 0.95 | 0.00115 | 0.00070 | [−0.00022, 0.00252] | 0.101 |
| Operating margin (level) | 0.00063 | 0.00054 | [−0.00043, 0.00170] | 0.241 |
| ln(COGS markup / Traina's measure) | −0.00196 | 0.00075 | [−0.00344, −0.00049] | 0.009 |

Bootstrap changes, 2011 to 2025, on firms reporting overhead (`results/bootstrap_changes.csv`):

| Measure | Change | Bootstrap SE | 95% CI |
|---|---|---|---|
| COGS markup | +0.294 | 0.153 | [0.047, 0.618] |
| Traina's measure | +0.060 | 0.032 | [0.005, 0.127] |
| Operating margin | +0.025 | 0.015 | [−0.002, 0.055] |
| Gap between the two changes | +0.234 | 0.134 | [0.028, 0.525] |
| Ratio of the two changes | 0.206 | 0.388 | [0.017, 0.564] |

Cumulative decomposition, 2011 to 2025 (`results/decomposition.csv`): within −0.111, market share +0.252, cross
+0.038, net entry +0.084, total +0.264. Across sectors (`results/sector_decomposition.csv`): within-sector +0.120,
between-sector +0.073, cross +0.071.

Robustness (`results/robustness.csv`), change 2011 to 2025: net PP&E as capital +0.289; COGS from the identity only
+0.306; COGS including depreciation +0.156; firms present in 2011, 2016 and 2025 +0.074; manufacturing only +0.160;
without Meta Platforms +0.140.

## Why no production-function elasticities

The paper's benchmark estimates $`\theta_{st}`$ by a control-function production-function estimator for each sector
and year. Bond, Hashemi, Kaplan and Zoch (2021) show that with revenue rather than quantity data this elasticity does
not identify the markup, and the paper itself reports that cost-share elasticities give a similar series (its Figure
XII). I used the cost-share and fixed-elasticity versions only.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/fetch_sec.py        # optional: rebuilds data/raw/sec_*.csv from the 60 SEC zips (about 5.6 GB)
python src/markups.py          # replication, decomposition, named firms, robustness
python src/overhead.py         # Traina's measure, trend tests, bootstrap
```

## References

- Bond, S., Hashemi, A., Kaplan, G. & Zoch, P. (2021). Some unpleasant markup arithmetic: production function
  elasticities and their estimation from production data. *Journal of Monetary Economics* 121.
- De Loecker, J., Eeckhout, J. & Unger, G. (2020). The rise of market power and the macroeconomic implications.
  *Quarterly Journal of Economics* 135(2), 561–644.
- De Loecker, J. & Warzynski, F. (2012). Markups and firm-level export status. *American Economic Review* 102(6).
- Traina, J. (2018). Is aggregate market power increasing? Production trends using financial statements. Stigler
  Center Working Paper 272.
