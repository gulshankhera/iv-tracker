"""
IV History Viewer
View historical IV data for any stock in your database
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import sys

DB_PATH = 'iv_data.db'


def view_stock_history(ticker, days=30):
    """View IV history for a specific stock"""

    if not ticker:
        print("❌ Please provide a ticker symbol")
        return

    ticker = ticker.upper()

    conn = sqlite3.connect(DB_PATH)

    # Get history
    query = '''
        SELECT 
            date as "Date",
            iv_30day as "IV %",
            price as "Price"
        FROM iv_history
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT ?
    '''

    df = pd.read_sql_query(query, conn, params=(ticker, days))
    conn.close()

    if len(df) == 0:
        print(f"\n❌ No data found for {ticker}")
        print("   Make sure ticker is in your watchlist and you've run scans")
        return

    # Calculate daily changes
    df = df.sort_values('Date')
    df['IV Change'] = df['IV %'].diff()
    df['Price Change'] = df['Price'].diff()
    df = df.sort_values('Date', ascending=False)

    # Display
    print(f"\n{'=' * 70}")
    print(f"📊 {ticker} - IV HISTORY (Last {len(df)} days)")
    print(f"{'=' * 70}\n")

    # Summary stats
    print(f"Current IV: {df.iloc[0]['IV %']:.2f}%")
    print(f"Avg IV (period): {df['IV %'].mean():.2f}%")
    print(f"Min IV: {df['IV %'].min():.2f}%")
    print(f"Max IV: {df['IV %'].max():.2f}%")
    print(f"Volatility Range: {df['IV %'].max() - df['IV %'].min():.2f}%\n")

    # Format display
    print(f"{'Date':<12} {'IV %':<10} {'Change':<10} {'Price':<12} {'Price Chg':<12}")
    print("-" * 70)

    for idx, row in df.iterrows():
        date = row['Date']
        iv = row['IV %']
        iv_change = row['IV Change']
        price = row['Price']
        price_change = row['Price Change']

        # Color coding for IV changes
        if pd.notna(iv_change):
            if iv_change > 5:
                change_str = f"+{iv_change:.2f}% 📈"
            elif iv_change < -5:
                change_str = f"{iv_change:.2f}% 📉"
            else:
                change_str = f"{iv_change:+.2f}%"
        else:
            change_str = "-"

        # Price change
        if pd.notna(price_change):
            price_chg_str = f"${price_change:+.2f}"
        else:
            price_chg_str = "-"

        print(f"{date:<12} {iv:<9.2f}% {change_str:<10} ${price:<10.2f} {price_chg_str:<12}")

    print(f"\n{'=' * 70}\n")


def view_all_stocks_summary():
    """View summary of all stocks in database"""

    conn = sqlite3.connect(DB_PATH)

    query = '''
        WITH LatestData AS (
            SELECT 
                ticker,
                iv_30day,
                price,
                date,
                ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) as rn
            FROM iv_history
        )
        SELECT 
            ticker as "Ticker",
            iv_30day as "Current IV",
            price as "Price",
            date as "Last Updated"
        FROM LatestData
        WHERE rn = 1
        ORDER BY ticker
    '''

    df = pd.read_sql_query(query, conn)
    conn.close()

    if len(df) == 0:
        print("\n❌ No data in database yet")
        print("   Run: python iv_tracker.py first\n")
        return

    print(f"\n{'=' * 70}")
    print(f"📊 ALL STOCKS SUMMARY - {len(df)} tickers tracked")
    print(f"{'=' * 70}\n")

    print(f"{'Ticker':<10} {'Current IV':<15} {'Price':<15} {'Last Updated':<15}")
    print("-" * 70)

    for idx, row in df.iterrows():
        ticker = row['Ticker']
        iv = row['Current IV']
        price = row['Price']
        date = row['Last Updated']

        print(f"{ticker:<10} {iv:<14.2f}% ${price:<13.2f} {date:<15}")

    print(f"\n{'=' * 70}\n")


def compare_stocks(tickers):
    """Compare IV for multiple stocks"""

    if not tickers or len(tickers) < 2:
        print("❌ Please provide at least 2 ticker symbols")
        return

    tickers = [t.upper() for t in tickers]

    conn = sqlite3.connect(DB_PATH)

    print(f"\n{'=' * 70}")
    print(f"📊 COMPARING: {', '.join(tickers)}")
    print(f"{'=' * 70}\n")

    for ticker in tickers:
        query = '''
            SELECT 
                iv_30day,
                price,
                date
            FROM iv_history
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT 1
        '''

        result = pd.read_sql_query(query, conn, params=(ticker,))

        if len(result) == 0:
            print(f"{ticker:<10} No data")
            continue

        iv = result.iloc[0]['iv_30day']
        price = result.iloc[0]['price']
        date = result.iloc[0]['date']

        print(f"{ticker:<10} IV: {iv:.2f}%  |  Price: ${price:.2f}  |  Updated: {date}")

    conn.close()
    print(f"\n{'=' * 70}\n")


def view_alerts_history(days=30):
    """View all historical alerts"""

    conn = sqlite3.connect(DB_PATH)

    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    query = '''
        SELECT 
            ticker as "Ticker",
            alert_date as "Date",
            iv_change_pct as "IV Change %",
            iv_current as "Current IV",
            iv_previous as "Previous IV",
            analysis as "Analysis"
        FROM alerts
        WHERE alert_date >= ?
        ORDER BY alert_date DESC, abs(iv_change_pct) DESC
    '''

    df = pd.read_sql_query(query, conn, params=(cutoff,))
    conn.close()

    if len(df) == 0:
        print(f"\n✅ No alerts in last {days} days")
        print("   Alerts trigger when IV changes >20% in 7 days\n")
        return

    print(f"\n{'=' * 70}")
    print(f"🚨 ALERT HISTORY - Last {days} days")
    print(f"{'=' * 70}\n")

    for idx, row in df.iterrows():
        ticker = row['Ticker']
        date = row['Date']
        change = row['IV Change %']
        current = row['Current IV']
        previous = row['Previous IV']
        analysis = row['Analysis']

        emoji = "📈" if change > 0 else "📉"
        signal = "SELL PREMIUM" if change > 0 else "BUY PREMIUM"

        print(f"{emoji} {ticker} ({date}): {change:+.1f}%")
        print(f"   IV: {current:.1f}% (was {previous:.1f}%)")
        print(f"   Signal: {signal}")

        if analysis and len(analysis) > 0:
            print(f"   💡 {analysis[:150]}{'...' if len(analysis) > 150 else ''}")

        print()

    print(f"{'=' * 70}\n")


def main():
    """Main menu"""

    if len(sys.argv) == 1:
        # No arguments - show menu
        print("\n" + "=" * 70)
        print("📊 IV HISTORY VIEWER")
        print("=" * 70 + "\n")
        print("Usage:")
        print("  python view_history.py <ticker> [days]     - View stock history")
        print("  python view_history.py all                 - View all stocks")
        print("  python view_history.py alerts [days]       - View alert history")
        print("  python view_history.py compare AAPL MSFT   - Compare stocks")
        print("\nExamples:")
        print("  python view_history.py AAPL                - AAPL last 30 days")
        print("  python view_history.py AAPL 60             - AAPL last 60 days")
        print("  python view_history.py all                 - All stocks summary")
        print("  python view_history.py alerts              - Recent alerts")
        print("  python view_history.py compare AAPL MSFT GOOGL - Compare 3 stocks")
        print("\n" + "=" * 70 + "\n")

    elif sys.argv[1].lower() == 'all':
        view_all_stocks_summary()

    elif sys.argv[1].lower() == 'alerts':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        view_alerts_history(days)

    elif sys.argv[1].lower() == 'compare':
        if len(sys.argv) < 4:
            print("❌ Need at least 2 tickers to compare")
            print("   Usage: python view_history.py compare AAPL MSFT")
        else:
            compare_stocks(sys.argv[2:])

    else:
        ticker = sys.argv[1]
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        view_stock_history(ticker, days)


if __name__ == "__main__":
    main()