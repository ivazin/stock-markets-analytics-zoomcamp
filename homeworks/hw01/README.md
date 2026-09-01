# Homework 1 (Module 1 Homework — 2026 Cohort)
**Course:** [Stock Markets Analytics Zoomcamp](https://github.com/DataTalksClub/stock-markets-analytics-zoomcamp)

---

## 📌 Summary and Answers to Questions

| # | Question | Key Result / Answer |
|---|---|---|
| **Q1** | Year with the highest number of additions to the S&P 500 (since 2020) | **2025** (18 new companies). *(In 2026 as of calculation date: 13)*. >20 years in index: **218** stocks. |
| **Q2** | How many global indexes out of 10 outperformed S&P 500 YTD (as of Aug 21, 2026) | **2 indexes**: **Canada (TSX Composite: +14.86%)** and **Japan (Nikkei 225: +27.36%)** compared to S&P 500 return of **+11.90%**. |
| **Q3** | Median drawdown during S&P 500 market corrections ($\ge 5\%$) since 1950 | **7.99%** (median recovery/cycle duration: **92.5 days**). 25th percentile: 6.23%, 75th percentile: 14.02%. |
| **Q4** | Median 2-day return for AMZN after a positive Earnings Surprise | **+0.35%** (correlation between surprise magnitude and 2-day return: **+0.33**). |
| **Q5** | Capstone Project Idea | **"Market Dashboard & Breadth Indicator"**: 3-level system (Global Trend -> Market Breadth % > SMA 50/200 -> Momentum/RSI) with traffic light signal generation (Green / Yellow / Red). |
| **Q6** | New metrics to explore for the project | 1) % of stocks above 50-day and 200-day SMA; 2) Cumulative Advance-Decline Line (A/D Line); 3) Volatility Index (VIX); 4) Divergences between index price and market breadth. |

---

## 🚀 How to Run the Solution

All computations are automated in a single script:

```bash
# Via Makefile
make hw1

# Or directly via uv
uv run homeworks/hw01/solution.py
```
