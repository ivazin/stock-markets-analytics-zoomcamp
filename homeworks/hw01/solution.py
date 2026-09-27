"""
Solution for Module 1 Homework (2026 Cohort)
Stock Markets Analytics Zoomcamp
"""

import io
import requests
import numpy as np
import pandas as pd
import yfinance as yf


def solve_question_1():
    print("=" * 70)
    print("QUESTION 1: S&P 500 Stocks Added to the Index")
    print("=" * 70)

    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    tables = pd.read_html(io.StringIO(response.text))
    sp500_table = tables[0]

    # Clean and parse Date added
    sp500_table["Date added"] = pd.to_datetime(
        sp500_table["Date added"], errors="coerce"
    )
    sp500_table["Year added"] = sp500_table["Date added"].dt.year

    additions_from_2020 = (
        sp500_table[sp500_table["Year added"] >= 2020]["Year added"]
        .value_counts()
        .sort_index()
    )

    print("\nNumber of additions per year (>= 2020):")
    for year, count in additions_from_2020.items():
        print(f"  {int(year)}: {count} companies")

    # We evaluate full years (2020-2025)
    full_years = additions_from_2020[additions_from_2020.index <= 2025]
    max_year = int(full_years.idxmax())
    max_count = int(full_years.max())

    print(f"\n-> Answer Q1: {max_year} had the highest number of additions ({max_count} stocks).")

    # Additional
    older_than_20y = sp500_table[sp500_table["Date added"] < "2006-01-01"]
    print(f"-> Additional: {len(older_than_20y)} stocks have been in the index for > 20 years.")


def solve_question_2():
    print("\n" + "=" * 70)
    print("QUESTION 2: [Macro] Indexes YTD (as of 21 August 2026)")
    print("=" * 70)

    indexes = {
        "United States - S&P 500": "^GSPC",
        "China - Shanghai Composite": "000001.SS",
        "Hong Kong - HANG SENG INDEX": "^HSI",
        "Australia - S&P/ASX 200": "^AXJO",
        "India - Nifty 50": "^NSEI",
        "Canada - S&P/TSX Composite": "^GSPTSE",
        "Germany - DAX": "^GDAXI",
        "United Kingdom - FTSE 100": "^FTSE",
        "Japan - Nikkei 225": "^N225",
        "Mexico - IPC Mexico": "^MXX",
        "Brazil - Ibovespa": "^BVSP",
    }

    returns = {}
    print("\nDownloading index data (2026-01-01 to 2026-08-22)...")
    for name, ticker in indexes.items():
        df = yf.download(ticker, start="2026-01-01", end="2026-08-22", progress=False)
        if not df.empty and len(df) > 1:
            close = df["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            close = close.dropna()
            first_val = close.iloc[0]
            last_val = close.iloc[-1]
            ytd = (last_val - first_val) / first_val * 100
            returns[name] = ytd
            print(f"  {name:32s} ({ticker:10s}): {ytd:+.2f}%")

    us_return = returns["United States - S&P 500"]
    outperforming = {
        k: v for k, v in returns.items() if k != "United States - S&P 500" and v > us_return
    }

    print(f"\nS&P 500 Return: {us_return:+.2f}%")
    print(
        f"-> Answer Q2: {len(outperforming)} indexes (out of 10) have better YTD returns than S&P 500."
    )
    for name, val in outperforming.items():
        print(f"   * {name}: {val:+.2f}%")


def solve_question_3():
    print("\n" + "=" * 70)
    print("QUESTION 3: S&P 500 Market Corrections Analysis (1950 - present)")
    print("=" * 70)

    df = yf.download("^GSPC", start="1950-01-01", progress=False)
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()

    running_max = close.cummax()
    is_ath = close == running_max
    ath_dates = close[is_ath].index

    corrections = []
    for i in range(len(ath_dates) - 1):
        start_ath = ath_dates[i]
        end_ath = ath_dates[i + 1]

        period = close.loc[start_ath:end_ath]
        if len(period) <= 2:
            continue

        min_price = period.min()
        min_date = period.idxmin()
        high_price = close.loc[start_ath]

        drawdown_pct = (high_price - min_price) / high_price * 100
        duration_days = (min_date - start_ath).days  # Days to trough (matches Hint)
        duration_recovery_days = (end_ath - start_ath).days  # Full cycle to next ATH

        if drawdown_pct >= 5.0:
            corrections.append(
                {
                    "start_ath": start_ath.strftime("%Y-%m-%d"),
                    "end_ath": end_ath.strftime("%Y-%m-%d"),
                    "min_date": min_date.strftime("%Y-%m-%d"),
                    "drawdown_pct": drawdown_pct,
                    "duration_days": duration_days,
                    "duration_recovery_days": duration_recovery_days,
                }
            )

    corr_df = pd.DataFrame(corrections)
    p25_dd = np.percentile(corr_df["drawdown_pct"], 25)
    p50_dd = np.percentile(corr_df["drawdown_pct"], 50)
    p75_dd = np.percentile(corr_df["drawdown_pct"], 75)

    p25_dur = np.percentile(corr_df["duration_days"], 25)
    p50_dur = np.percentile(corr_df["duration_days"], 50)
    p75_dur = np.percentile(corr_df["duration_days"], 75)

    p25_rec = np.percentile(corr_df["duration_recovery_days"], 25)
    p50_rec = np.percentile(corr_df["duration_recovery_days"], 50)
    p75_rec = np.percentile(corr_df["duration_recovery_days"], 75)

    print(f"\nTotal corrections identified (>= 5%): {len(corr_df)}")
    print(f"-> Drawdowns (%): 25th={p25_dd:.2f}%, Median (50th)={p50_dd:.2f}%, 75th={p75_dd:.2f}%")
    print(f"-> Duration to Trough (days): 25th={p25_dur:.1f}d, Median (50th)={p50_dur:.1f}d, 75th={p75_dur:.1f}d")
    print(f"-> Full Cycle to next ATH (days): 25th={p25_rec:.1f}d, Median (50th)={p50_rec:.1f}d, 75th={p75_rec:.1f}d")
    print(f"\n-> Answer Q3: Median drawdown is {p50_dd:.2f}% (median duration to trough is {p50_dur:.1f} days, full cycle is {p50_rec:.1f} days).")


def solve_question_4():
    print("\n" + "=" * 70)
    print("QUESTION 4: Earnings Surprise Analysis for Amazon (AMZN)")
    print("=" * 70)

    ticker = "AMZN"
    ticker_obj = yf.Ticker(ticker)
    earnings_df = ticker_obj.get_earnings_dates()

    price_df = yf.download(ticker, start="2020-01-01", progress=False)
    close = price_df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    earnings_clean = earnings_df.dropna(subset=["Surprise(%)"]).copy()
    pos_surprises = earnings_clean[earnings_clean["Surprise(%)"] > 0].copy()

    returns_2d = []
    surprises = []

    close_dates = (
        close.index.tz_localize(None).normalize()
        if close.index.tz is not None
        else close.index.normalize()
    )

    for date_idx, row in pos_surprises.iterrows():
        dt = (
            date_idx.tz_localize(None).normalize()
            if hasattr(date_idx, "tz_localize") and date_idx.tz is not None
            else pd.Timestamp(date_idx).normalize()
        )
        surprise = row["Surprise(%)"]

        matches = np.where(close_dates >= dt)[0]
        if len(matches) > 0:
            day2_idx = matches[0]
            day1_idx = day2_idx - 1
            day3_idx = day2_idx + 1

            if day1_idx >= 0 and day3_idx < len(close):
                c1 = close.iloc[day1_idx]
                c3 = close.iloc[day3_idx]
                ret_2d = (c3 / c1 - 1) * 100
                returns_2d.append(ret_2d)
                surprises.append(surprise)

    res_df = pd.DataFrame({"Surprise(%)": surprises, "2d_Return(%)": returns_2d})
    median_ret = res_df["2d_Return(%)"].median()
    corr = res_df.corr().iloc[0, 1]

    print(f"\nPositive surprise events analyzed: {len(res_df)}")
    print(f"-> Answer Q4: Median 2-day return after positive surprise is {median_ret:.2f}%.")
    print(f"   Correlation between surprise magnitude and 2-day return: {corr:.4f}")


def main():
    solve_question_1()
    solve_question_2()
    solve_question_3()
    solve_question_4()


if __name__ == "__main__":
    main()
