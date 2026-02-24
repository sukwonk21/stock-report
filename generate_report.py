#!/usr/bin/env python3
"""Main entrypoint: fetch stock data → render Jinja2 template → save HTML report."""

import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

import config
from fetch_data import fetch_stock_data, format_market_cap, format_volume


def main():
    print(f"Fetching data for: {', '.join(config.TICKERS)}")
    stocks = fetch_stock_data()

    if not stocks:
        print("No data fetched. Exiting.")
        return

    # Build template context
    tickers_ordered = [t for t in config.TICKERS if t in stocks]
    stock_list = [stocks[t] for t in tickers_ordered]

    # All history dates (use the ticker with most data)
    all_dates = max((stocks[t]["history_dates"] for t in tickers_ordered), key=len)

    # Pad shorter series to align with all_dates
    for s in stock_list:
        pad = len(all_dates) - len(s["history_dates"])
        s["history_pct_padded"] = [None] * pad + s["history_pct"]

    # Colors for the multi-line chart (one per ticker)
    palette = [
        "#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6",
        "#8b5cf6", "#14b8a6", "#f97316", "#ec4899", "#84cc16",
    ]
    for i, s in enumerate(stock_list):
        s["color"] = palette[i % len(palette)]
        s["market_cap_fmt"] = format_market_cap(s["market_cap"])
        s["volume_fmt"] = format_volume(s["volume"])

    # 52-week range: build floating bar data [low, high] + current price overlay
    fifty_two_labels = tickers_ordered
    fifty_two_low = [stocks[t]["fifty_two_week_low"] for t in tickers_ordered]
    fifty_two_high = [stocks[t]["fifty_two_week_high"] for t in tickers_ordered]
    current_prices = [stocks[t]["close"] for t in tickers_ordered]

    context = {
        "title": config.REPORT_TITLE,
        "generated_at": datetime.now().strftime("%B %d, %Y %I:%M %p"),
        "stock_list": stock_list,
        "tickers_json": json.dumps(tickers_ordered),
        "daily_change_json": json.dumps([stocks[t]["daily_change_pct"] for t in tickers_ordered]),
        "daily_change_colors_json": json.dumps(
            ["#10b981" if stocks[t]["daily_change_pct"] >= 0 else "#ef4444" for t in tickers_ordered]
        ),
        "history_dates_json": json.dumps(all_dates),
        "history_series_json": json.dumps([
            {
                "label": s["ticker"],
                "data": s["history_pct_padded"],
                "borderColor": s["color"],
                "backgroundColor": s["color"] + "22",
                "tension": 0.3,
                "pointRadius": 2,
                "borderWidth": 2,
                "fill": False,
                "spanGaps": True,
            }
            for s in stock_list
        ]),
        "volume_json": json.dumps([stocks[t]["volume"] for t in tickers_ordered]),
        "volume_colors_json": json.dumps(
            ["#10b981" if stocks[t]["daily_change_pct"] >= 0 else "#ef4444" for t in tickers_ordered]
        ),
        "fifty_two_labels_json": json.dumps(fifty_two_labels),
        "fifty_two_low_json": json.dumps(fifty_two_low),
        "fifty_two_high_json": json.dumps(fifty_two_high),
        "current_prices_json": json.dumps(current_prices),
    }

    # Render template
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template("template.html")
    html = template.render(**context)

    # Write output
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime(config.DATE_FORMAT)
    output_path = os.path.join(config.OUTPUT_DIR, f"report_{date_str}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
