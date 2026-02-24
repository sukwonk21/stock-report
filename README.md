# Stock Market Report Generator

Fetches daily stock data for major AI & tech companies from Yahoo Finance and generates a self-contained HTML dashboard with interactive Chart.js visualizations.

## Tickers

NVDA, MSFT, GOOGL, META, AMZN, AAPL, TSLA, AMD, ORCL, IBM

## Dashboard

- **Daily % Change** — horizontal bar chart, green/red by gain/loss
- **30-Day Price History** — normalized multi-line chart (% from start)
- **Volume Today** — bar chart
- **52-Week Range** — floating bar showing low→high with current price marker
- **Summary Table** — price, change, market cap, volume for all tickers

## Setup

```bash
pip install yfinance pandas jinja2
```

## Usage

```bash
python generate_report.py
open reports/report_$(date +%Y-%m-%d).html
```

Reports are saved to the `reports/` directory as `report_YYYY-MM-DD.html`.

## Project Structure

```
stock-report/
├── config.py           # Tickers and settings
├── fetch_data.py       # yfinance data fetching and processing
├── generate_report.py  # Main entrypoint
├── template.html       # Jinja2 template with Chart.js
└── reports/            # Generated HTML reports (gitignored)
```

## Data Source

[Yahoo Finance](https://finance.yahoo.com) via [yfinance](https://github.com/ranaroussi/yfinance). Not financial advice.
