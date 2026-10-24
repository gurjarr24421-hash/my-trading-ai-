# Trading AI — Starter Research Dashboard

This is a rule-based daily technical-analysis prototype, **not** a trained AI, validated backtest, investment recommendation, or auto-trading system. No orders are placed.

## Run

Install Python 3.10+ and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter a Yahoo Finance ticker, e.g. `RELIANCE.NS` or `TCS.NS`. Uses third-party historical data, which may be delayed, incomplete, or unavailable. The last close is not a live executable price.

Signals: bullish if Close > EMA20 > EMA50, RSI 50–70 and MACD > signal; bearish if inverse trend, RSI 30–50 and MACD < signal; otherwise no trade. Illustrative stop is 1.5 ATR and target 3 ATR. Position size is based on account risk only; check capital/margin, lot sizes, liquidity, transaction charges, slippage, gap risk, and broker rules separately.

Next engineering steps: point-in-time data quality, walk-forward and out-of-sample testing, realistic costs, paper-trading ledger, broker sandbox integration, audit logs, manual approvals, and regulatory review before any real execution.
