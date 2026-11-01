# Methods review: De Loecker, Eeckhout and Unger (2020)

- **Paper:** De Loecker, J., Eeckhout, J. & Unger, G. (2020). "The Rise of Market Power and the Macroeconomic
  Implications." *Quarterly Journal of Economics* 135(2), 561–644. doi:10.1093/qje/qjz041.
- **Statistical focus:** the sales-weighted aggregate markup rising from 1.21 in 1980 to 1.61 in 2016 (Section III.A,
  Figure I), and the decomposition attributing about two-thirds of that rise to reallocation of sales toward
  high-markup firms (Section III.C, Figure IV).
- **Review standard:** current AEA Data and Code Availability Policy and standard reporting of estimates, uncertainty
  and sample construction; internal consistency of the identifying assumptions of the production approach.
- **What was read:** the full published article, including Appendices A to F, from a PDF of the journal version
  hosted by CREi (crei.cat), read from a text conversion; the abstract and bibliography entries of the paper; the
  RePEc listing for Traina (2018); search-engine abstracts for Bond, Hashemi, Kaplan and Zoch (2021). The Online Appendix was not read. The article states that data and code
  replicating its tables and figures are posted in the Harvard Dataverse (doi:10.7910/DVN/5GH8XO); that package
  was not examined, and the underlying Compustat data are licensed. Figures were read only as described in the text, since plotted
  values cannot be extracted reliably from a text conversion.

## Methods summary

### Research design

Observational, descriptive panel study. Step one assigns each firm to a two-digit NAICS sector and estimates, for each
sector and year (five-year rolling windows, footnote 59), a Cobb-Douglas production function in a variable input
(COGS) and capital by a control-function method (Appendix A, equation 23; Olley-Pakes and Ackerberg-Caves-Frazer
variants in Figure A.1). Step two computes each firm's markup as the output elasticity of COGS times sales over COGS
(equation 7). Step three aggregates with sales weights (equation 8) and decomposes changes (equations 9 and 10).
Profit rates (equation 13), market value and dividends (Table II), overhead (Table III) and labor shares (Table V)
are then related to markups. The authors state they are "agnostic about the origins" of the rise (Section I); no
causal claim is made for the markup series itself.

### Sampling strategy

All US-incorporated publicly listed firms in Compustat North America Fundamentals Annual, 1950–2016, downloaded on
25 March 2018 (Appendix B.A). A population of listed firms rather than a sample; selection into listing is
acknowledged (Section II.C) and addressed by reweighting with sector population weights and by repeating parts of
the analysis on the Economic Censuses for manufacturing, retail and wholesale (Section III.D).

### Sample size

247,644 firm-years with sales, COGS and SG&A for 1955–2016 (Sample A, Table B.1); 28,116 firm-years with a wage
bill (Sample B). Table III uses 26,743 and 247,615 observations; Table V uses 24,838. The number of firms per year
and the number of firms in each sector-year production-function estimation are not reported in the main text.

### Inclusion and exclusion criteria

Firms must report an industry code, sales and COGS. Within each year, firms in the top and bottom 1% of COGS/sales
and SG&A/sales are dropped; results are said to be invariant to trimming up to 5% (Appendix B.A). Financial firms
are not stated to be excluded.

### Independent and dependent variables

Firm markup (constructed); sales weights; SG&A as overhead; user cost of capital r = nominal rate − inflation +
12%, applied to gross PP&E deflated by an industry price index (Section II.C). Variables are deflated by the GDP
deflator (Table B.1 notes). Profit rate, market value over sales, dividends over sales and labor share are outcome
variables in Sections IV and V.

### Statistical methods

GMM control-function estimation of production functions by sector-year; sales-weighted means and weighted
percentiles; shift-share decompositions; OLS with year, industry and firm fixed effects for Tables II, III and V,
with firm-clustered standard errors stated in the notes to Tables II and V.

### Reported effect sizes

Aggregate markup 1.21 (1980) and 1.61 (2016); 90th percentile 1.5 to 2.5 (Section III.B); within-term rise from 1.21
to 1.3 by 2000 against a total of 1.21 to 1.47 (Section III.C); Table I ten-year sectoral decompositions; profit rate
1% to 8%; τ 1.08 to 1.18; elasticity of markup to SG&A 0.56 (Table III); labor share elasticity −0.20 to −0.24
(Table V).

### Confidence intervals

None are reported for the aggregate markup, its percentiles or the decomposition terms. Standard errors are reported
for the regressions in Tables II, III and V.

### p-values

Not reported. Regression significance is described in words ("highly significant").

### Missing data treatment

Firm-years lacking sales or COGS are dropped. Firms lacking the wage bill are excluded from the labor share analysis,
which leaves fewer than 10% of firm-years (footnote 46). Imputation is not described.

### Stated limitations

Selection of public firms; measurement of COGS as a bundle of inputs; the dependence of markups on the output
elasticity and the production technology; volatility of the capital measure (footnote 17); attrition through mergers
in Compustat (footnote 60); the unrealistic representative-firm reading of aggregate profits (Section IV.B).

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Aggregate markup, 1980 | 1.21 (price over marginal cost) | Section III.A; Figure I | Sales-weighted mean of firm markups with sector-year production-function elasticities | Uncertainty around the level; markups of private firms |
| Aggregate markup, 2016 | 1.61 | Section III.A; Figure I; Table I | Same, at the end of the sample | That any market became less competitive; welfare loss |
| Aggregate markup, 1960s peak | 1.34 | Section III.A | Same, before the decline to 1980 | Comparability of Compustat coverage across decades |
| 90th percentile of markups | about 1.5 (1980) to 2.5 (2016) | Section III.B; Figure III(B) | Sales-weighted percentile | Which firms or industries make up the tail |
| Within-firm term | 1.21 to 1.3 (1980 to 2000) of a total 1.21 to 1.47 | Section III.C; Figure IV | Change with sales shares held at last year's values | Exact cumulative values after 2000; standard errors |
| Reallocation share of the rise | about two-thirds | Section III.C; Section VII | Market share plus cross terms, cumulated from 1980 | Whether reallocation reflects market power or efficiency |
| Ten-year change, 2006 to 2016 | +0.154 (within 0.133, between 0.014, cross 0.007) | Table I | Sectoral decomposition of the aggregate | Firm-level reallocation within sectors |
| Profit rate | 1% (1980) to 8% (2016) of sales | Abstract; Section IV.A; Figure VIII | Sales-weighted net profit rate after COGS, SG&A and rK | Accounting rates of return on capital |
| Overhead share of total cost | 15% to 21% | Section I | SG&A over COGS plus SG&A plus rK | That SG&A is fixed rather than variable |
| Traina's measure τ | 1.08 to 1.18 (1980 to 2016) | Section IV.B, equations 17 to 19 | Markup with COGS plus SG&A as the variable input, θ near 0.95 | That overhead is entirely fixed or entirely variable |
| Fixed-elasticity markup | θ = 0.85; pattern "similar" | Section III.A; Figure II(A) | Sensitivity to the elasticity | Level comparison in numbers (plotted only) |
| Markup on SG&A | 0.56 (SE 0.01), N = 26,743 | Table III, column 1 | Firm-level elasticity of log markup to log SG&A | Causal effect of overhead on prices |
| Labor share on markup | −0.20 to −0.24 (SE 0.03), N = 24,838 | Table V, columns 1 to 4 | Firm-level association, clustered by firm | Aggregate labor share effects; representativeness of the 10% of firms with wage data |
| Market value on markup | 0.71 (SE 0.03) to 0.17 (SE 0.03) with firm fixed effects | Table II | Association of valuation with markups | That higher valuations come from market power rather than intangibles |

## Interpretation notes

- The aggregate markup is a sales-weighted mean of ratios. Firms with very small COGS relative to sales carry
  very large markups, so the aggregate is sensitive to how costs are classified between COGS and SG&A, and to the
  growth of a few such firms.
- The paper is explicit that most of the rise is reallocation. A reader should not take the 1.21 to 1.61 headline as
  the typical firm raising prices by a third; the paper reports the median as unchanged.
- The paper reports τ rising 10 points against 40 for the benchmark markup, and interprets τ as closer to a profit
  rate. Both readings depend on how much of SG&A is variable, which the paper treats as an assumption rather than a
  quantity it estimates.
- Data and code availability: a replication package is posted (Harvard Dataverse, doi:10.7910/DVN/5GH8XO), which
  meets the intent of the AEA policy, but running it requires licensed Compustat access. Whether it reproduces every
  figure was not checked here.
- Reporting gaps, separate from any analytical error: no confidence intervals or standard errors for the headline
  series or decomposition; the number of firms per sector-year in the production-function estimation is not reported
  in the main text; plotted series are not tabulated in the main text (the paper says yearly decomposition values are
  in the Online Appendix, which I did not read).
- No published correction to the article was found in the sources I examined. Bond, Hashemi, Kaplan and Zoch (2021)
  argue, as a general matter for the ratio estimator, that elasticities estimated from revenue data cannot identify
  markups; that is a critique of the method's identification, not a documented error in this paper's computations.

## Unanswered questions

- How sensitive is the 2016 level to the treatment of financial firms, whose Compustat COGS is not a production cost?
- What are the sampling uncertainty and the estimation uncertainty from the first-stage elasticities in the 1980 to
  2016 change?
- How much of the rise survives when the denominator includes the share of SG&A that varies with output, estimated
  rather than assumed?
- Does the reallocation term reflect entry and growth of firms with intangible-heavy cost structures, which would
  produce high COGS markups without higher prices over full marginal cost?

## Items requiring expert verification

- Whether Compustat's SG&A item includes R&D for all firms in the sample, as the paper's statement that R&D reached
  20% of SG&A by 2016 implies.
- Whether the control-function estimator with COGS as the flexible input identifies the output elasticity in this
  setting, given the identification arguments of Bond and coauthors.
- The exact construction of the deflated capital stock and the industry price index used in the user cost.
- The comparison with demand-side estimates in Online Appendix Section 7, which the paper cites as corroboration.

**How the modern rerun relates.** This repository rebuilds the aggregate from SEC XBRL filings for 2011 to 2025 with
cost-share and fixed elasticities rather than the paper's production-function estimates. It is not a reproduction of
the paper's results. Its 2016 aggregate (1.61) is close to the paper's, its decomposition again finds the rise driven
by reallocation, and its version of Traina's measure rises far less than the COGS-based markup.
