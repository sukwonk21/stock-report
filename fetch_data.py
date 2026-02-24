import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import config


def fetch_stock_data():
    end = datetime.today()
    start = end - timedelta(days=config.LOOKBACK_DAYS + 5)  # extra buffer for weekends

    # Fetch OHLCV for all tickers in one call
    raw = yf.download(
        config.TICKERS,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )

    stocks = {}

    for ticker in config.TICKERS:
        try:
            # Handle single vs multi-ticker DataFrame structure
            if len(config.TICKERS) == 1:
                df = raw.copy()
            else:
                df = raw[ticker].copy()

            df = df.dropna(subset=["Close"])

            if df.empty or len(df) < 2:
                print(f"Warning: insufficient data for {ticker}, skipping.")
                continue

            # Keep only the last LOOKBACK_DAYS trading days
            df = df.tail(config.LOOKBACK_DAYS)

            today = df.iloc[-1]
            prev = df.iloc[-2]

            close = float(today["Close"])
            open_ = float(today["Open"])
            high = float(today["High"])
            low = float(today["Low"])
            volume = int(today["Volume"])
            prev_close = float(prev["Close"])
            daily_change_pct = ((close - prev_close) / prev_close) * 100

            # Normalized 30-day price history (% change from first day)
            first_close = float(df["Close"].iloc[0])
            history_dates = [d.strftime("%Y-%m-%d") for d in df.index]
            history_pct = [
                round(((float(c) - first_close) / first_close) * 100, 2)
                for c in df["Close"]
            ]
            history_volume = [int(v) for v in df["Volume"]]

            # 52-week high/low via Ticker.info
            info = {}
            try:
                t = yf.Ticker(ticker)
                info = t.info or {}
            except Exception:
                pass

            fifty_two_week_high = info.get("fiftyTwoWeekHigh") or float(df["High"].max())
            fifty_two_week_low = info.get("fiftyTwoWeekLow") or float(df["Low"].min())
            market_cap = info.get("marketCap")

            stocks[ticker] = {
                "ticker": ticker,
                "close": round(close, 2),
                "open": round(open_, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": volume,
                "prev_close": round(prev_close, 2),
                "daily_change_pct": round(daily_change_pct, 2),
                "fifty_two_week_high": round(fifty_two_week_high, 2),
                "fifty_two_week_low": round(fifty_two_week_low, 2),
                "market_cap": market_cap,
                "history_dates": history_dates,
                "history_pct": history_pct,
                "history_volume": history_volume,
            }

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return stocks


def format_market_cap(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def format_volume(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)
