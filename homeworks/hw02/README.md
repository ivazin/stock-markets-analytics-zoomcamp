# Homework 2 (Module 2 Homework — 2026 Cohort)
**Course:** [Stock Markets Analytics Zoomcamp](https://github.com/DataTalksClub/stock-markets-analytics-zoomcamp)

---

## 📌 Summary and Answers to Questions

| # | Question | Key Result / Answer |
|---|---|---|
| **Q1** | **[IPO] Withdrawn IPOs by Company Type**<br>Which company class had the highest total value of withdrawals, and what was that value? | **Acquisition Corp** with **$499.99M** (or ~$500M).<br>*(Next highest: Inc. with $351.00M, Holdings with $311.66M, Other with $290.45M)*. |
| **Q2** | **[IPO] Median Sharpe Ratio for 2025 IPOs (First 8 Months)**<br>Median Sharpe ratio as of 11 September 2026 for companies that went public before 1 September 2025? | **0.0490** (~**0.05**).<br>*(130 of 132 downloadable tickers reached 252-day milestone. Median 252d growth: 0.5945, Mean 252d growth: 1.0521)*. |
| **Q3** | **[IPO] 'Fixed Months Holding Strategy'**<br>Optimal holding period (1 to 12 months) to maximize median growth value? | **1 month** (`future_growth_1_m` = 21 trading days) with max median growth ratio of **0.9354** (return: **-6.46%**).<br>*(Clear monotonic decay pattern: typical IPO post-market performance degrades over time)*. |
| **Q4** | **[Strategy] Simple RSI-Based Trading Strategy**<br>Total profit (in $ thousands) earned investing $1,000 every time RSI < 30? | **$65.81 thousand** (~**$66k** / **$65,805.59**).<br>*(Total trades: 5,206; Win rate: 55.13%; Average 30-day return: 1.26%)*. |
| **Q5** | **[Exploratory] Predicting a Positive-Return IPO**<br>How would you change the strategy if you want to increase profitability? | Propose **Quality & Momentum Screening Filter**:<br>1. **Fundamental Quality Filters**: Screen for positive EBITDA / GAAP net income and institutional backing.<br>2. **First-Day Breakout Momentum**: Avoid buying on day 1 close unconditionally; only enter if the stock closes in the top quartile of its first-day range or above day 1 high.<br>3. **Strict Stop-Loss & Lockup Expiration Timing**: Implement tight trailing stops (-7% to -10%) and exit before day 90/180 lockup expirations. |

---

## 🛠️ Execution & Reproducibility

The solution script is located at [`homeworks/hw02/solution.py`](solution.py).

To reproduce the answers:
```bash
# Run the complete pipeline
python homeworks/hw02/solution.py
```

### Detailed Breakdown

### Question 1: Withdrawn IPOs by Company Type
- **Source:** Scraped recently filed IPO table from `https://www.iposcoop.com/ipos-recently-filed/`.
- **Classification hierarchy:** Checked sequentially with word-boundary regular expressions:
  1. `Technologies`
  2. `Acquisition Corp` / `Acquisition Corporation` / `Corp`
  3. `Inc` / `Incorporated`
  4. `Group`
  5. `Ltd` / `Limited`
  6. `Holdings` / `Holding`
  7. `Other`
- **Valuation:** Computed `Shares (millions) * Avg_price` when both exist, falling back to `Est $ Vol (millions)` for deals with zero shares or missing price bands.
- **Result:**
  - `Acquisition Corp`: **$499.985M**
  - `Inc.`: **$351.000M**
  - `Holdings`: **$311.658M**
  - `Other`: **$290.445M**
  - `Limited`: **$219.250M** ($197.25M before Sep 11)
  - `Technologies`: **$184.900M**
  - `Group`: **$56.575M** ($32.50M before Sep 11)

### Question 2: Median Sharpe Ratio for 2025 IPOs
- **Source:** Scraped `https://www.iposcoop.com/2025-pricings/`, filtered `Offer Date < 2025-09-01` and `Return != '0.00%'` (146 companies).
- **Download:** Downloaded daily OHLCV from Yahoo Finance (132 active tickers, 14 delisted/missing).
- **Milestone:** 130 stocks had $\ge 252$ trading days by `2026-09-11`.
- **Key Stats on 2026-09-11:**
  - `growth_252d`: Median = **0.5945** (-40.55%), Mean = **1.0521** (+5.21%) — heavy positive skew by rare multibaggers.
  - `volatility`: Median = **7.89**
  - `Sharpe`: Median = **0.0490** (~0.05)

### Question 3: 'Fixed Months Holding Strategy'
- Evaluated forward returns for holding periods $m \in \{1, \dots, 12\}$ months ($21 \times m$ trading days) from the IPO closing price:
  - **Month 1 (21d):** Median = **0.9354** (-6.46%), Mean = 95.75
  - **Month 2 (42d):** Median = **0.8930** (-10.70%), Mean = 67.98
  - **Month 3 (63d):** Median = **0.8272** (-17.28%), Mean = 51.25
  - **Month 6 (126d):** Median = **0.7009** (-29.91%), Mean = 64.01
  - **Month 12 (252d):** Median = **0.4918** (-50.82%), Mean = 5.82
- **Conclusion:** **Month 1** maximizes median return (or minimizes median loss). Post-IPO prices show steady median degradation over time.

### Question 4: Simple RSI-Based Trading Strategy
- **Dataset:** 25-year daily signals and forward returns (`data.parquet`).
- **Filter:** `2000-01-01 <= Date <= 2025-06-01` and `rsi < 30`.
- **Trade count:** **5,206** signals.
- **Performance:**
  - Average 30-day return: **+1.2640%**
  - Win rate: **55.13%**
  - Total Net Income: **$65,805.59** (**$65.81k**)

### Question 5: Exploratory Brainstorming
- **Observation:** The median IPO loses ~50% in its first year, but average return is positive due to rare hyper-performers (like biotech/AI spikes).
- **Enhanced Strategies:**
  1. **Long Winner / Short Loser Pairs Strategy:** Short IPOs trading below their offer price / 20-day moving average after month 1, and long top-tier institutional IPOs showing positive earnings growth.
  2. **Wait for Lockup Expiration Dump:** Buy quality companies 10–14 days *after* the 180-day insider lockup expires, once early VC selling pressure has cleared.
  3. **Momentum Consolidation Breakout (IPO Base):** Avoid day-1 hype; wait for a minimum 6–8 week base, entering only when price breaks out of the range on high relative volume.
