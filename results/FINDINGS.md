# De Loecker, Eeckhout and Unger (2020) on SEC filings: findings

## In plain English

De Loecker, Eeckhout and Unger found that the average American public company's price rose from 21% to 61% above
the cost of making one more unit between 1980 and 2016. Rebuilding their measure from SEC filings for 2011 to 2025:

- **Their 2016 number comes back, and the rise continued.** The sales-weighted markup is 1.61 in 2016, the paper's
  figure, and 1.79 in 2025.
- **The typical company did not raise its markup.** The median stayed near 1.3, and companies' own markups drifted
  slightly down. The whole rise came from sales shifting toward high-markup companies such as Meta Platforms,
  Mastercard, Alphabet and Nvidia. Meta alone accounts for about half of it.
- **Counting overhead as a cost removes most of the rise.** When selling, administrative and research spending is
  counted alongside cost of goods, as James Traina proposed, the markup goes from 1.15 to 1.21 instead of 1.58 to
  1.88 on the same companies. Meta's markup falls from 10.88 to 1.99, Microsoft's from 3.05 to 1.80.
- **Margins widened a little.** Sales left after cost of goods and overhead rose from 14.9% to 17.4% of sales,
  but the bootstrap interval for that change includes zero.

The essay is in the [README](../README.md) and the method in [TECHNICAL.md](../TECHNICAL.md). The rest of this page
lists every table the scripts produce.

**Key to the labels:** *markup* = price over marginal cost, theta times sales over cost of goods sold (COGS);
*theta* = output elasticity of COGS, the sector-year median cost share COGS / (COGS + rK); *tau* = Traina's
measure, the same with COGS plus SG&A and R&D in the denominator; *overhead* = SG&A plus R&D; *share* = a
company's share of sample sales in the year. Fiscal years follow Compustat's convention.

## Sample construction

`sample_counts.csv`. Rows loaded, dropped and kept at each rule, in order. The three "of those kept" lines split the firm-years that passed the first rule by where their COGS figure comes from.

| step | rows |
|---|---|
| filer-years with revenue in the SEC panel | 70,983 |
| in 2011-2025 | 70,983 |
| dropped: no positive revenue and COGS | 16,535 |
| of those kept, COGS from the Compustat identity | 46,198 |
| of those kept, COGS from the identity with no SG&A line | 2,997 |
| of those kept, COGS from the cost-of-revenue tag | 5,253 |
| dropped: incorporated outside the US or state unknown (paper: US-incorporated) | 5,950 |
| dropped: no SIC industry code (paper: firms without an industry code excluded) | 5 |
| dropped: banks, insurers and real estate (SIC 6000-6799), whose XBRL cost lines are not COGS | 5,036 |
| dropped: top or bottom 1% of COGS/sales or overhead/sales in its year | 1,553 |
| kept: firm-years in the markup sample | 41,904 |
| kept: distinct firms | 6,529 |

## The aggregate markup by year

`aggregate_markup.csv`. *markup* is the sales-weighted average with the cost-share elasticity; *markup_theta_085* fixes the elasticity at 0.85; *p50*, *p75*, *p90* are sales-weighted percentiles; *theta_sales_weighted* is the sales-weighted average elasticity; *sales_trillion* is sample sales in trillions of dollars.

| year | firms | sales_trillion | markup | markup_theta_085 | markup_unweighted_mean | p50 | p75 | p90 | theta_sales_weighted |
|---|---|---|---|---|---|---|---|---|---|
| 2011 | 3,165 | 9.173 | 1.529 | 1.393 | 1.832 | 1.293 | 1.608 | 2.182 | 0.934 |
| 2012 | 3,345 | 9.680 | 1.529 | 1.403 | 1.948 | 1.298 | 1.605 | 2.178 | 0.928 |
| 2013 | 3,266 | 10.031 | 1.546 | 1.429 | 1.873 | 1.303 | 1.602 | 2.284 | 0.920 |
| 2014 | 3,251 | 10.283 | 1.576 | 1.455 | 1.948 | 1.293 | 1.640 | 2.238 | 0.922 |
| 2015 | 3,085 | 9.804 | 1.547 | 1.441 | 1.808 | 1.276 | 1.665 | 2.241 | 0.912 |
| 2016 | 2,905 | 9.701 | 1.613 | 1.500 | 1.841 | 1.312 | 1.659 | 2.259 | 0.914 |
| 2017 | 2,913 | 10.467 | 1.603 | 1.487 | 2.003 | 1.289 | 1.630 | 2.237 | 0.916 |
| 2018 | 2,615 | 10.620 | 1.607 | 1.493 | 2.044 | 1.273 | 1.612 | 2.423 | 0.917 |
| 2019 | 2,511 | 10.785 | 1.628 | 1.516 | 1.948 | 1.277 | 1.608 | 2.394 | 0.913 |
| 2020 | 2,502 | 10.340 | 1.650 | 1.524 | 1.991 | 1.314 | 1.645 | 2.460 | 0.920 |
| 2021 | 2,672 | 12.541 | 1.748 | 1.564 | 2.149 | 1.336 | 1.784 | 2.647 | 0.950 |
| 2022 | 2,633 | 13.908 | 1.713 | 1.513 | 2.144 | 1.324 | 1.791 | 2.576 | 0.962 |
| 2023 | 2,499 | 14.063 | 1.672 | 1.544 | 2.029 | 1.283 | 1.751 | 2.482 | 0.921 |
| 2024 | 2,372 | 14.667 | 1.709 | 1.594 | 2.147 | 1.290 | 1.792 | 2.559 | 0.911 |
| 2025 | 2,170 | 14.993 | 1.793 | 1.661 | 2.194 | 1.323 | 1.824 | 2.803 | 0.916 |

## The paper's equation (9), year by year

`decomposition.csv`. Year-over-year change in the aggregate markup split into the within-firm term, the market-share term, the cross term and net entry; *reallocation* is market share plus cross. Entrants and exits are firms entering or leaving the sample, which includes listings, delistings, mergers and years a filer fails a data rule.

| year | change | within | market_share | cross | reallocation | net_entry | entrants | exits | continuers |
|---|---|---|---|---|---|---|---|---|---|
| 2012 | -0.000 | -0.017 | 0.010 | -0.002 | 0.008 | 0.009 | 583 | 403 | 2,762 |
| 2013 | 0.017 | 0.009 | 0.006 | -0.002 | 0.004 | 0.004 | 332 | 411 | 2,934 |
| 2014 | 0.030 | -0.002 | 0.016 | 0.006 | 0.022 | 0.010 | 373 | 388 | 2,878 |
| 2015 | -0.029 | -0.041 | 0.027 | 0.008 | 0.035 | -0.023 | 320 | 486 | 2,765 |
| 2016 | 0.066 | 0.014 | 0.017 | 0.001 | 0.018 | 0.034 | 317 | 497 | 2,588 |
| 2017 | -0.010 | -0.013 | 0.010 | 0.002 | 0.012 | -0.009 | 379 | 371 | 2,534 |
| 2018 | 0.005 | -0.034 | 0.022 | -0.008 | 0.014 | 0.025 | 262 | 560 | 2,353 |
| 2019 | 0.021 | 0.003 | 0.020 | 0.001 | 0.021 | -0.003 | 249 | 353 | 2,262 |
| 2020 | 0.022 | -0.059 | 0.048 | 0.006 | 0.055 | 0.026 | 268 | 277 | 2,234 |
| 2021 | 0.098 | 0.093 | 0.000 | 0.003 | 0.004 | 0.001 | 395 | 225 | 2,277 |
| 2022 | -0.035 | -0.023 | -0.021 | 0.006 | -0.015 | 0.004 | 245 | 284 | 2,388 |
| 2023 | -0.041 | -0.057 | 0.016 | 0.010 | 0.026 | -0.010 | 215 | 349 | 2,284 |
| 2024 | 0.037 | -0.006 | 0.035 | 0.007 | 0.042 | 0.001 | 187 | 314 | 2,185 |
| 2025 | 0.084 | 0.024 | 0.044 | 0.000 | 0.045 | 0.016 | 162 | 364 | 2,008 |

## The paper's equation (10), across sectors

`sector_decomposition.csv`. Change in the aggregate split into changes within sectors, shifts between sectors and their interaction.

| from | to | markup_from | markup_to | change | within | between | cross |
|---|---|---|---|---|---|---|---|
| 2011 | 2016 | 1.529 | 1.613 | 0.084 | 0.090 | 0.002 | -0.008 |
| 2016 | 2025 | 1.613 | 1.793 | 0.180 | 0.044 | 0.094 | 0.042 |
| 2011 | 2025 | 1.529 | 1.793 | 0.264 | 0.120 | 0.073 | 0.071 |

## Sector markups and sales shares

`sector_markups.csv` (2011, 2016 and 2025 shown; the file has every year). Sectors are SIC major groups mapped to the nearest two-digit NAICS sector.

| sector | markup_2011 | markup_2016 | markup_2025 | share_2011 | share_2016 | share_2025 |
|---|---|---|---|---|---|---|
| Accommodation and food | 1.453 | 1.365 | 1.371 | 0.018 | 0.018 | 0.013 |
| Agriculture | 1.127 | 1.105 | 1.056 | 0.001 | 0.001 | 0.000 |
| Arts and entertainment | 1.270 | 1.225 | 1.536 | 0.003 | 0.005 | 0.014 |
| Business services and software | 2.937 | 3.404 | 4.197 | 0.045 | 0.063 | 0.117 |
| Construction | 1.123 | 1.172 | 1.190 | 0.005 | 0.008 | 0.010 |
| Health care | 1.357 | 1.155 | 1.281 | 0.004 | 0.010 | 0.010 |
| Information | 1.748 | 1.763 | 1.868 | 0.065 | 0.069 | 0.041 |
| Manufacturing | 1.606 | 1.799 | 1.766 | 0.472 | 0.386 | 0.368 |
| Mining, oil and gas | 1.426 | 0.920 | 1.354 | 0.023 | 0.016 | 0.015 |
| Other services | 1.524 | 1.844 | 1.407 | 0.002 | 0.002 | 0.002 |
| Professional services | 1.680 | 1.645 | 1.595 | 0.006 | 0.006 | 0.006 |
| Retail trade | 1.324 | 1.295 | 1.267 | 0.186 | 0.226 | 0.232 |
| Transportation | 1.126 | 1.172 | 1.265 | 0.048 | 0.049 | 0.033 |
| Utilities | 1.122 | 0.988 | 0.897 | 0.046 | 0.054 | 0.036 |
| Wholesale trade | 1.133 | 1.128 | 1.093 | 0.076 | 0.087 | 0.104 |

## Robustness of the aggregate

`robustness.csv`. The aggregate markup in 2011, 2016 and 2025 under alternative choices.

| variant | m2011 | m2016 | m2025 | change_2011_2025 | firm_years |
|---|---|---|---|---|---|
| main: cost-share elasticity, all COGS sources | 1.529 | 1.613 | 1.793 | 0.264 | 41,904 |
| elasticity fixed at 0.85 | 1.393 | 1.500 | 1.661 | 0.268 | 41,904 |
| cost-share elasticity using net PP&E as capital | 1.584 | 1.688 | 1.873 | 0.289 | 41,904 |
| only firm-years with COGS from the Compustat identity | 1.565 | 1.662 | 1.871 | 0.306 | 35,792 |
| COGS including depreciation (operating costs less overhead) | 1.361 | 1.394 | 1.518 | 0.156 | 37,796 |
| firms present in all of 2011, 2016 and 2025 | 1.547 | 1.587 | 1.622 | 0.074 | 13,323 |
| manufacturing only | 1.606 | 1.799 | 1.766 | 0.160 | 19,662 |
| without Meta Platforms, the largest single contributor | 1.529 | 1.567 | 1.670 | 0.140 | 41,891 |

## Traina's measure on the same firms

`overhead_aggregate.csv`. Firm-years that report overhead only. *markup_cogs* is the paper's measure, *tau* is Traina's with a cost-share elasticity, *tau_theta_095* fixes it at 0.95, *tau_sga_without_rd* counts SG&A but not R&D as variable; shares are aggregate ratios; *operating_margin* is the sales-weighted mean of 1 - (COGS + overhead)/sales; *user_cost_r* is the paper's user cost of capital.

| year | firms | markup_cogs | tau | tau_theta_095 | tau_sga_without_rd | overhead_share_of_cost | cogs_share_of_sales | overhead_share_of_sales | operating_margin | user_cost_r | theta_cogs | theta_vx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011 | 2,984 | 1.584 | 1.154 | 1.145 | 1.142 | 0.190 | 0.678 | 0.173 | 0.149 | 0.090 | 0.940 | 0.960 |
| 2012 | 3,176 | 1.581 | 1.144 | 1.139 | 1.133 | 0.189 | 0.682 | 0.175 | 0.144 | 0.101 | 0.935 | 0.957 |
| 2013 | 3,096 | 1.591 | 1.153 | 1.154 | 1.145 | 0.185 | 0.677 | 0.171 | 0.152 | 0.106 | 0.927 | 0.952 |
| 2014 | 3,085 | 1.625 | 1.151 | 1.149 | 1.147 | 0.190 | 0.675 | 0.176 | 0.149 | 0.105 | 0.931 | 0.954 |
| 2015 | 2,920 | 1.598 | 1.133 | 1.135 | 1.133 | 0.188 | 0.687 | 0.181 | 0.132 | 0.120 | 0.923 | 0.949 |
| 2016 | 2,749 | 1.674 | 1.144 | 1.145 | 1.155 | 0.195 | 0.670 | 0.184 | 0.147 | 0.111 | 0.925 | 0.950 |
| 2017 | 2,755 | 1.656 | 1.148 | 1.148 | 1.149 | 0.189 | 0.678 | 0.176 | 0.146 | 0.109 | 0.926 | 0.952 |
| 2018 | 2,478 | 1.676 | 1.161 | 1.159 | 1.189 | 0.193 | 0.668 | 0.180 | 0.151 | 0.114 | 0.925 | 0.954 |
| 2019 | 2,389 | 1.700 | 1.150 | 1.152 | 1.183 | 0.196 | 0.667 | 0.187 | 0.146 | 0.123 | 0.921 | 0.951 |
| 2020 | 2,388 | 1.723 | 1.135 | 1.126 | 1.187 | 0.208 | 0.677 | 0.202 | 0.120 | 0.111 | 0.929 | 0.958 |
| 2021 | 2,561 | 1.822 | 1.220 | 1.191 | 1.281 | 0.210 | 0.647 | 0.186 | 0.167 | 0.074 | 0.956 | 0.975 |
| 2022 | 2,524 | 1.783 | 1.215 | 1.178 | 1.271 | 0.207 | 0.662 | 0.183 | 0.155 | 0.057 | 0.966 | 0.981 |
| 2023 | 2,385 | 1.745 | 1.179 | 1.176 | 1.246 | 0.201 | 0.657 | 0.188 | 0.154 | 0.129 | 0.929 | 0.957 |
| 2024 | 2,258 | 1.790 | 1.188 | 1.189 | 1.276 | 0.197 | 0.653 | 0.186 | 0.161 | 0.142 | 0.919 | 0.952 |
| 2025 | 2,066 | 1.878 | 1.214 | 1.213 | 1.324 | 0.196 | 0.642 | 0.184 | 0.174 | 0.136 | 0.924 | 0.953 |

## Within-firm trend tests

`trend_tests.csv`. Slope on (year - 2011) with firm fixed effects, weighted by sales share, standard errors clustered by firm. For log outcomes the slope is the proportional change per year.

| outcome | slope_per_year | se | ci_low | ci_high | p_value | n_firm_years | n_firms |
|---|---|---|---|---|---|---|---|
| ln(markup) | -0.00079 | 0.00086 | -0.00247 | 0.00089 | 0.35403 | 38,938 | 5,412 |
| ln(tau) | 0.00117 | 0.00072 | -0.00024 | 0.00257 | 0.10372 | 38,938 | 5,412 |
| ln(tau_fixed) | 0.00115 | 0.00070 | -0.00022 | 0.00252 | 0.10082 | 38,938 | 5,412 |
| operating_margin | 0.00063 | 0.00054 | -0.00043 | 0.00170 | 0.24082 | 38,938 | 5,412 |
| ln(markup_over_tau) | -0.00196 | 0.00075 | -0.00344 | -0.00049 | 0.00907 | 38,938 | 5,412 |

## Bootstrap changes, 2011 to 2025

`bootstrap_changes.csv`. Firm bootstrap with 500 draws. *gap* is the change in the COGS markup minus the change in Traina's measure; the last row is the ratio of the two changes.

| measure | change_2011_2025 | boot_se | ci_low | ci_high | share_of_draws_above_zero |
|---|---|---|---|---|---|
| markup | 0.294 | 0.153 | 0.047 | 0.618 | 0.994 |
| tau | 0.060 | 0.032 | 0.005 | 0.127 | 0.988 |
| operating_margin | 0.025 | 0.015 | -0.002 | 0.055 | 0.962 |
| gap | 0.234 | 0.134 | 0.028 | 0.525 | 0.988 |
| tau_rise_over_markup_rise | 0.206 | 0.388 | 0.017 | 0.564 | 0.982 |

## Named companies

`firms_named.csv` and `firms_overhead.csv`. The 20 largest companies by 2025 sales and the 15 with the largest contribution to the 2011-2025 rise. *contribution* is the firm's term in the change of the sales-weighted average, measured against the 2011 average, so contributions of all firms (including those that left) sum to the aggregate change. Blank 2011 values mean the company did not yet file, filed under another registrant (Alphabet before 2015 was Google Inc.), or failed a data rule that year. `firm_years.csv.gz` holds the full cleaned firm-year panel behind every table. Mastercard files no cost-of-sales line, so its COGS by the identity is whatever operating expense is not G&A or depreciation ($1.6 billion in 2011, $1.4 billion in 2025), and its very high markup partly reflects that.

| list | name | sector | revenue_2025_billion | markup_2011 | markup_2016 | markup_2025 | share_2011 | share_2025 | contribution | tau_2025 | overhead_share_2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| largest by 2025 sales | Amazon Com Inc | Retail trade | 716.924 | 1.061 | 1.143 | 1.327 | 0.005 | 0.048 | -0.007 | 1.205 | 0.081 |
| largest by 2025 sales | Walmart Inc. | Retail trade | 713.163 | 1.322 | 1.326 | 1.299 | 0.049 | 0.048 | -0.001 | 1.023 | 0.207 |
| largest by 2025 sales | Apple Inc | Manufacturing | 416.161 | 1.637 | 1.659 | 1.824 | 0.012 | 0.028 | 0.007 | 1.463 | 0.149 |
| largest by 2025 sales | Mckesson Corp | Wholesale trade | 403.430 | 1.040 | 1.061 | 1.010 | 0.013 | 0.027 | -0.007 | 0.996 | 0.020 |
| largest by 2025 sales | Alphabet Inc. | Business services and software | 402.836 |  | 2.413 | 2.707 |  | 0.027 | 0.032 | 1.565 | 0.276 |
| largest by 2025 sales | Cvs Health Corp | Retail trade | 402.067 | 1.197 | 1.145 | 0.971 | 0.012 | 0.027 | -0.011 |  |  |
| largest by 2025 sales | Exxon Mobil Corp | Manufacturing | 332.238 | 1.176 | 1.137 | 1.201 | 0.047 | 0.022 | 0.009 | 1.196 | 0.033 |
| largest by 2025 sales | Cencora, Inc. | Wholesale trade | 321.333 | 1.017 | 1.006 | 1.004 | 0.009 | 0.021 | -0.007 | 0.990 | 0.020 |
| largest by 2025 sales | Microsoft Corp | Business services and software | 281.724 | 4.304 | 2.611 | 3.048 | 0.008 | 0.019 | 0.007 | 1.805 | 0.232 |
| largest by 2025 sales | Costco Wholesale Corp /New | Retail trade | 275.235 | 1.118 | 1.119 | 1.100 | 0.010 | 0.018 | -0.004 | 1.007 | 0.091 |
| largest by 2025 sales | Cardinal Health Inc | Wholesale trade | 222.578 | 1.030 | 1.037 | 1.012 | 0.011 | 0.015 | -0.002 | 0.994 | 0.024 |
| largest by 2025 sales | Nvidia Corp | Manufacturing | 215.938 | 2.179 | 2.414 | 3.322 | 0.000 | 0.014 | 0.026 | 2.491 | 0.107 |
| largest by 2025 sales | Meta Platforms, Inc. | Business services and software | 200.966 |  | 17.937 | 10.876 |  | 0.013 | 0.125 | 1.990 | 0.406 |
| largest by 2025 sales | Chevron Corp | Manufacturing | 189.031 | 1.290 | 1.164 | 1.204 | 0.027 | 0.013 | 0.002 | 1.209 | 0.027 |
| largest by 2025 sales | Ford Motor Co | Manufacturing | 187.267 |  |  | 0.966 |  | 0.012 | -0.007 | 0.947 | 0.058 |
| largest by 2025 sales | Home Depot, Inc. | Retail trade | 164.683 | 1.480 | 1.461 | 1.426 | 0.008 | 0.011 | -0.001 | 1.127 | 0.186 |
| largest by 2025 sales | Kroger Co | Retail trade | 147.642 | 1.000 | 1.009 | 0.984 | 0.010 | 0.010 | -0.000 |  |  |
| largest by 2025 sales | Verizon Communications Inc | Information | 138.191 | 2.109 | 2.063 | 2.199 | 0.012 | 0.009 | -0.001 | 1.419 | 0.245 |
| largest by 2025 sales | Marathon Petroleum Corp | Manufacturing | 132.699 |  |  | 1.033 |  | 0.009 | -0.004 | 1.045 | 0.025 |
| largest by 2025 sales | At&T Inc. | Information | 125.648 | 1.913 | 1.822 | 2.197 | 0.014 | 0.008 | 0.000 | 1.450 | 0.230 |
| largest contribution to the rise | Meta Platforms, Inc. | Business services and software | 200.966 |  | 17.937 | 10.876 |  | 0.013 | 0.125 | 1.990 | 0.406 |
| largest contribution to the rise | Mastercard Inc | Business services and software | 32.791 | 3.995 | 12.417 | 21.745 | 0.001 | 0.002 | 0.042 | 2.524 | 0.345 |
| largest contribution to the rise | Alphabet Inc. | Business services and software | 402.836 |  | 2.413 | 2.707 |  | 0.027 | 0.032 | 1.565 | 0.276 |
| largest contribution to the rise | Nvidia Corp | Manufacturing | 215.938 | 2.179 | 2.414 | 3.322 | 0.000 | 0.014 | 0.026 | 2.491 | 0.107 |
| largest contribution to the rise | Salesforce, Inc. | Business services and software | 41.525 | 6.552 | 4.946 | 6.339 | 0.000 | 0.003 | 0.012 | 1.378 | 0.562 |
| largest contribution to the rise | Exxon Mobil Corp | Manufacturing | 332.238 | 1.176 | 1.137 | 1.201 | 0.047 | 0.022 | 0.009 | 1.196 | 0.033 |
| largest contribution to the rise | Microsoft Corp | Business services and software | 281.724 | 4.304 | 2.611 | 3.048 | 0.008 | 0.019 | 0.007 | 1.805 | 0.232 |
| largest contribution to the rise | General Electric Co | Manufacturing | 45.855 | 0.889 | 1.184 | 1.365 | 0.012 | 0.003 | 0.007 | 1.199 | 0.124 |
| largest contribution to the rise | Apple Inc | Manufacturing | 416.161 | 1.637 | 1.659 | 1.824 | 0.012 | 0.028 | 0.007 | 1.463 | 0.149 |
| largest contribution to the rise | Regeneron Pharmaceuticals, Inc. | Manufacturing | 14.343 |  |  | 7.873 |  | 0.001 | 0.006 | 1.339 | 0.596 |
| largest contribution to the rise | T-Mobile Us, Inc. | Information | 88.309 | 1.185 | 2.045 | 2.413 | 0.002 | 0.006 | 0.006 | 1.453 | 0.266 |
| largest contribution to the rise | Exelixis, Inc. | Manufacturing | 2.320 |  |  | 28.320 |  | 0.000 | 0.004 | 1.560 | 0.579 |
| largest contribution to the rise | Abbvie Inc. | Manufacturing | 61.160 |  | 4.253 | 2.525 |  | 0.004 | 0.004 | 1.287 | 0.378 |
| largest contribution to the rise | Autodesk, Inc. | Business services and software | 7.206 |  | 6.055 | 9.458 |  | 0.000 | 0.004 | 1.302 | 0.653 |
| largest contribution to the rise | Servicenow, Inc. | Business services and software | 13.278 |  | 2.229 | 5.620 |  | 0.001 | 0.004 | 1.216 | 0.638 |
