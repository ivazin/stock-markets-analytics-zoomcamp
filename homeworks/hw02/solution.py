"""
Homework 2 Solutions - Stock Markets Analytics Zoomcamp (2026 Cohort)
Author: Automated Pair Programmer & Quantitative Analyst
"""

import io
import re
import os
import numpy as np
import pandas as pd
import yfinance as yf
from curl_cffi import requests
import gdown


def solve_q1():
    print("=" * 60)
    print("QUESTION 1: [IPO] Withdrawn IPOs by Company Type")
    print("=" * 60)

    url = "https://www.iposcoop.com/ipos-recently-filed/"
    resp = requests.get(url, impersonate="chrome")
    df = pd.read_html(io.StringIO(resp.text))[0]

    # Filter 'Expected To Trade' == 'Withdrawn'
    df_w = df[df["Expected To Trade"] == "Withdrawn"].copy()
    print(f"Total withdrawn IPO entries identified: {len(df_w)}")

    # Company classification (strict rule order):
    # 1. "Technologies" -> Technologies
    # 2. "Acquisition Corp", "Acquisition Corporation", or "Corp" -> Acquisition Corp
    # 3. "Inc" or "Incorporated" -> Inc.
    # 4. "Group" -> Group
    # 5. "Ltd" or "Limited" -> Limited
    # 6. "Holdings" or "Holding" -> Holdings
    # 7. Others -> Other
    def classify_company(name: str) -> str:
        if re.search(r"\bTechnologies\b", name):
            return "Technologies"
        if re.search(r"\b(Acquisition Corp|Acquisition Corporation|Corp)\b", name):
            return "Acquisition Corp"
        if re.search(r"\b(Inc|Incorporated)\b", name):
            return "Inc."
        if re.search(r"\bGroup\b", name):
            return "Group"
        if re.search(r"\b(Ltd|Limited)\b", name):
            return "Limited"
        if re.search(r"\b(Holdings|Holding)\b", name):
            return "Holdings"
        return "Other"

    df_w["Company Type"] = df_w["Company"].apply(classify_company)

    # Parsing price fields
    def parse_currency(val):
        if pd.isna(val):
            return None
        val_clean = str(val).replace("$", "").replace(",", "").strip()
        try:
            return float(val_clean)
        except ValueError:
            return None

    df_w["price_low_num"] = df_w["Price Low"].apply(parse_currency)
    df_w["price_high_num"] = df_w["Price High"].apply(parse_currency)
    df_w["Avg_price"] = (df_w["price_low_num"] + df_w["price_high_num"]) / 2.0

    df_w["shares_num"] = df_w["Shares (millions)"].apply(parse_currency)
    df_w["est_vol_num"] = df_w["Est $ Vol (millions)"].apply(parse_currency)

    # Value Calculation:
    # If Shares (millions) * Avg_price is not null, use that value; otherwise use Est $ Vol (millions)
    calc_val = df_w["shares_num"] * df_w["Avg_price"]
    df_w["Shares_offered_value"] = calc_val.combine_first(df_w["est_vol_num"])

    # Aggregation
    agg_all = df_w.groupby("Company Type")["Shares_offered_value"].sum().sort_values(ascending=False)
    print("\nTotal Withdrawn Value by Company Type (All 34 entries):")
    print(agg_all.to_frame())

    # Aggregation before Sep 11, 2026 (31-32 entries)
    df_w_sep11 = df_w[df_w["File Date"] < "2026-09-11"].copy()
    agg_sep11 = df_w_sep11.groupby("Company Type")["Shares_offered_value"].sum().sort_values(ascending=False)
    print(f"\nTotal Withdrawn Value by Company Type (Before Sep 11, 2026: {len(df_w_sep11)} entries):")
    print(agg_sep11.to_frame())

    top_class = agg_all.index[0]
    top_val = agg_all.iloc[0]
    print(f"\n>>> Answer Q1: {top_class} with ${top_val:.2f}M (or ${agg_sep11.iloc[0]:.2f}M before Sep 11)")
    return df_w


def solve_q2_and_q3():
    print("\n" + "=" * 60)
    print("QUESTIONS 2 & 3: [IPO] Sharpe Ratio & Holding Period Strategy")
    print("=" * 60)

    parquet_file = "homeworks/hw02/stocks_df.parquet"
    if os.path.exists(parquet_file):
        print(f"Loading cached {parquet_file}...")
        stocks_df = pd.read_parquet(parquet_file)
    else:
        print("Downloading 2025 pricings table...")
        url = "https://www.iposcoop.com/2025-pricings/"
        resp = requests.get(url, impersonate="chrome")
        df_pricing = pd.read_html(io.StringIO(resp.text))[0]

        df_pricing["Offer Date Parsed"] = pd.to_datetime(df_pricing["Offer Date"], errors="coerce")
        filtered = df_pricing[(df_pricing["Offer Date Parsed"] < "2025-09-01") & (df_pricing["Return"] != "0.00%")].copy()
        tickers = filtered["Symbol"].dropna().unique().tolist()
        tickers_clean = [t.strip().replace(".", "-") for t in tickers]
        print(f"Filtered {len(tickers_clean)} tickers before 1 Sep 2025 with non-zero return.")

        print("Downloading OHLCV data from Yahoo Finance...")
        records = []
        for t in tickers_clean:
            try:
                t_df = yf.download(t, start="2025-01-01", end="2026-09-15", progress=False, auto_adjust=False)
                if t_df is not None and not t_df.empty:
                    if isinstance(t_df.columns, pd.MultiIndex):
                        t_df.columns = t_df.columns.get_level_values(0)
                    t_df["Ticker"] = t
                    records.append(t_df)
            except Exception:
                pass
        stocks_df = pd.concat(records).reset_index()
        stocks_df["Date"] = pd.to_datetime(stocks_df["Date"])
        stocks_df.to_parquet(parquet_file)

    stocks_df = stocks_df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    print(f"Total tickers available in stocks_df: {stocks_df['Ticker'].nunique()}")

    # Feature Engineering for Q2
    # growth_252d = Close / Close.shift(252)
    stocks_df["growth_252d"] = stocks_df.groupby("Ticker")["Close"].shift(0) / stocks_df.groupby("Ticker")["Close"].shift(252)
    # Volatility = Close.rolling(30).std() * sqrt(252)
    # Note: rolling is computed per ticker
    stocks_df["volatility"] = stocks_df.groupby("Ticker")["Close"].transform(lambda s: s.rolling(30).std() * np.sqrt(252))
    # Sharpe = (growth_252d - 0.05) / volatility
    stocks_df["Sharpe"] = (stocks_df["growth_252d"] - 0.05) / stocks_df["volatility"]

    # Filter for trading day '2026-09-11'
    df_sep11 = stocks_df[stocks_df["Date"].dt.strftime("%Y-%m-%d") == "2026-09-11"].copy()
    stats_q2 = df_sep11[["growth_252d", "volatility", "Sharpe"]].describe()
    print("\nDescriptive Statistics on 2026-09-11:")
    print(stats_q2)

    median_sharpe = df_sep11["Sharpe"].median()
    median_growth = df_sep11["growth_252d"].median()
    mean_growth = df_sep11["growth_252d"].mean()
    count_252 = df_sep11["growth_252d"].notna().sum()
    print(f"\nTickers reaching 252d milestone: {count_252} / {len(df_sep11)}")
    print(f"Median growth_252d: {median_growth:.4f} vs Mean growth_252d: {mean_growth:.4f}")
    print(f">>> Answer Q2: Median Sharpe Ratio as of 2026-09-11 = {median_sharpe:.4f} (~0.049 / 0.05)")

    # Feature Engineering for Q3: Fixed Months Holding Strategy
    # future_growth_m_m = Close.shift(-21*m) / Close
    for m in range(1, 13):
        days = m * 21
        stocks_df[f"future_growth_{m}_m"] = stocks_df.groupby("Ticker")["Close"].shift(-days) / stocks_df["Close"]

    # Identify entry point: min_date per ticker
    min_dates = stocks_df.groupby("Ticker")["Date"].min().reset_index().rename(columns={"Date": "min_date"})
    entry_df = pd.merge(stocks_df, min_dates, left_on=["Ticker", "Date"], right_on=["Ticker", "min_date"], how="inner")

    cols = [f"future_growth_{m}_m" for m in range(1, 13)]
    desc_q3 = entry_df[cols].describe().T
    print("\nHolding Period Growth Statistics (Months 1 to 12):")
    print(desc_q3[["count", "mean", "std", "50%"]])

    medians = entry_df[cols].median()
    best_holding_col = medians.idxmax()
    best_month = int(re.search(r"\d+", best_holding_col).group())
    best_median_val = medians[best_holding_col]

    print(f"\n>>> Answer Q3: Optimal holding period is {best_month} month(s) with max median growth = {best_median_val:.4f} (Return: {(best_median_val - 1) * 100:+.2f}%)")
    return stocks_df, entry_df


def solve_q4():
    print("\n" + "=" * 60)
    print("QUESTION 4: [Strategy] Simple RSI-Based Trading Strategy")
    print("=" * 60)

    parquet_file = "homeworks/hw02/data.parquet"
    if not os.path.exists(parquet_file):
        file_id = "1grCTCzMZKY5sJRtdbLVCXg8JXA8VPyg-"
        gdown.download(f"https://drive.google.com/uc?id={file_id}", parquet_file, quiet=False)

    df = pd.read_parquet(parquet_file, engine="pyarrow")
    df["Date_dt"] = pd.to_datetime(df["Date"])

    # Strategy Setup: RSI < 30 between 2000-01-01 and 2025-06-01
    cond = (df["Date_dt"] >= "2000-01-01") & (df["Date_dt"] <= "2025-06-01") & (df["rsi"] < 30)
    selected_df = df[cond].copy()

    trades_count = len(selected_df)
    net_income = 1000.0 * (selected_df["growth_future_30d"] - 1.0).sum()
    net_income_k = net_income / 1000.0
    avg_return = (selected_df["growth_future_30d"] - 1.0).mean()
    win_rate = (selected_df["growth_future_30d"] > 1.0).mean()

    print(f"Total trades: {trades_count}")
    print(f"Average 30-day return: {avg_return:.4%}")
    print(f"Win rate: {win_rate:.2%}")
    print(f"Net income: ${net_income:,.2f}")
    print(f">>> Answer Q4: Net income = ${net_income_k:,.2f} thousand (~${round(net_income_k)}k)")


if __name__ == "__main__":
    solve_q1()
    solve_q2_and_q3()
    solve_q4()
