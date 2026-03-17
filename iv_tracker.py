"""
IV Tracker - Options Implied Volatility Monitor
Tracks IV changes across your watchlist and alerts on significant moves
"""

import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from openai import OpenAI

# Configuration
DB_PATH = 'iv_data.db'
THRESHOLD_SPIKE = 20  # % increase to trigger alert
THRESHOLD_CRUSH = -20  # % decrease to trigger alert
LOOKBACK_DAYS = 7  # Compare IV to 7 days ago

class IVTracker:
    def __init__(self, api_key=None):
        self.db_path = DB_PATH
        self.init_database()
        self.client = OpenAI(api_key=api_key) if api_key else None
        
    def init_database(self):
        """Initialize SQLite database for storing IV history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iv_history (
                ticker TEXT,
                date TEXT,
                iv_30day REAL,
                price REAL,
                PRIMARY KEY (ticker, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                ticker TEXT,
                alert_date TEXT,
                iv_change_pct REAL,
                iv_current REAL,
                iv_previous REAL,
                analysis TEXT,
                PRIMARY KEY (ticker, alert_date)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_iv_history(self, ticker, days_back):
        """Get IV from N days ago"""
        from datetime import datetime, timedelta
        try:
            target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get closest date to target (within 2 days)
            query = '''
                SELECT iv_30day, date 
                FROM iv_history 
                WHERE ticker = ? 
                AND date >= date(?, '-2 days')
                AND date <= date(?, '+2 days')
                ORDER BY ABS(julianday(date) - julianday(?))
                LIMIT 1
            '''

            cursor.execute(query, (ticker, target_date, target_date, target_date))
            result = cursor.fetchone()
            conn.close()

            if result:
                return result[0]  # Return IV value
            return None

        except Exception as e:
            return None
    def get_iv_data(self, ticker):
        """
        Fetch current IV for a ticker using Yahoo Finance
        Returns: (iv_30day, current_price)
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get ATM options (at-the-money) for 30-day expiry
            expirations = stock.options
            if not expirations:
                return None, None
            
            # Find expiration closest to 30 days
            target_date = datetime.now() + timedelta(days=30)
            closest_exp = min(expirations, 
                            key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d') - target_date).days))
            
            opt_chain = stock.option_chain(closest_exp)
            calls = opt_chain.calls
            
            if calls.empty:
                return None, None
            
            # Get current stock price
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            
            # Find ATM option (strike closest to current price)
            calls['strike_diff'] = abs(calls['strike'] - current_price)
            atm_call = calls.loc[calls['strike_diff'].idxmin()]
            
            iv = atm_call['impliedVolatility'] * 100  # Convert to percentage
            
            return round(iv, 2), round(current_price, 2)
            
        except Exception as e:
            print(f"Error fetching IV for {ticker}: {str(e)}")
            return None, None
    
    def store_iv_data(self, ticker, iv, price):
        """Store IV data point in database"""
        if iv is None:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO iv_history (ticker, date, iv_30day, price)
            VALUES (?, ?, ?, ?)
        ''', (ticker, today, iv, price))
        
        conn.commit()
        conn.close()
    
    def get_iv_change(self, ticker, days_back=LOOKBACK_DAYS):
        """Calculate IV change percentage over specified days"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT iv_30day, date 
            FROM iv_history 
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT {days_back + 1}
        '''
        
        df = pd.read_sql_query(query, conn, params=(ticker,))
        conn.close()
        
        if len(df) < 2:
            return None, None, None
        
        iv_current = df.iloc[0]['iv_30day']
        iv_previous = df.iloc[-1]['iv_30day']
        
        change_pct = ((iv_current - iv_previous) / iv_previous) * 100
        
        return round(change_pct, 2), iv_current, iv_previous

    def get_gpt_analysis(self, ticker, change_pct, iv_current):
        """Get GPT-4o-mini analysis with actual news context"""
        if not self.client:
            return "GPT analysis disabled (no API key)"

        try:
            # Get real news and earnings context
            from news_fetcher import get_comprehensive_context, format_enhanced_prompt

            context = get_comprehensive_context(ticker, change_pct, iv_current)
            prompt = format_enhanced_prompt(ticker, change_pct, iv_current, context)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                     "content": "You are a factual options trading analyst. Cite specific events with dates. Be concise and actionable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"GPT Error: {str(e)}"
    
    def scan_watchlist(self, tickers, use_gpt=True):
        """
        Scan all tickers in watchlist and return alerts
        Returns: DataFrame with alerts
        """
        alerts = []
        
        print(f"\n{'='*60}")
        print(f"IV SCAN STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}\n")
        
        for ticker in tickers:
            print(f"Scanning {ticker}...", end=" ")
            
            # Fetch current IV
            iv, price = self.get_iv_data(ticker)
            
            if iv is None:
                print("❌ No data")
                continue
            
            # Store in database
            self.store_iv_data(ticker, iv, price)
            
            # Calculate change
            change_pct, iv_current, iv_previous = self.get_iv_change(ticker)
            
            if change_pct is None:
                print(f"✓ IV: {iv}% (baseline)")
                continue
            
            # Check if significant move
            if abs(change_pct) >= abs(THRESHOLD_SPIKE):
                analysis = ""
                
                if use_gpt and self.client:
                    print(f"🔥 {change_pct:+.1f}% - Getting GPT analysis...")
                    analysis = self.get_gpt_analysis(ticker, change_pct, iv_current)
                else:
                    print(f"🔥 {change_pct:+.1f}%")
                
                alerts.append({
                    'ticker': ticker,
                    'iv_current': iv_current,
                    'iv_7d_ago': iv_previous,
                    'change_pct': change_pct,
                    'price': price,
                    'analysis': analysis,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
                # Store alert
                self.store_alert(ticker, change_pct, iv_current, iv_previous, analysis)
            else:
                print(f"✓ {change_pct:+.1f}% (normal)")
        
        return pd.DataFrame(alerts)
    
    def store_alert(self, ticker, change_pct, iv_current, iv_previous, analysis):
        """Store alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO alerts 
            (ticker, alert_date, iv_change_pct, iv_current, iv_previous, analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, today, change_pct, iv_current, iv_previous, analysis))
        
        conn.commit()
        conn.close()
    
    def get_recent_alerts(self, days=7):
        """Retrieve recent alerts from database"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = '''
            SELECT * FROM alerts 
            WHERE alert_date >= ?
            ORDER BY alert_date DESC, abs(iv_change_pct) DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        return df


def load_watchlist(filepath='watchlist.txt'):
    """Load ticker symbols from file (one per line)"""
    if not os.path.exists(filepath):
        # Create sample watchlist
        sample_tickers = ['AAPL', 'NVDA', 'TSLA', 'SPY', 'QQQ']
        with open(filepath, 'w') as f:
            f.write('\n'.join(sample_tickers))
        print(f"Created sample watchlist: {filepath}")
        return sample_tickers
    
    with open(filepath, 'r') as f:
        tickers = [line.strip().upper() for line in f if line.strip()]
    
    return tickers


if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Load API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found. GPT analysis will be disabled.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'\n")
    
    # Initialize tracker
    tracker = IVTracker(api_key=api_key)
    
    # Load watchlist
    watchlist = load_watchlist()
    print(f"Loaded watchlist: {len(watchlist)} tickers\n")
    
    # Run scan
    alerts_df = tracker.scan_watchlist(watchlist, use_gpt=(api_key is not None))
    
    # Display results
    print(f"\n{'='*60}")
    print("SCAN COMPLETE")
    print(f"{'='*60}")
    
    if len(alerts_df) > 0:
        print(f"\n🚨 {len(alerts_df)} ALERTS TRIGGERED:\n")
        for _, alert in alerts_df.iterrows():
            emoji = "📈" if alert['change_pct'] > 0 else "📉"
            print(f"{emoji} {alert['ticker']}: {alert['change_pct']:+.1f}% (IV: {alert['iv_current']:.1f}%)")
            if alert['analysis']:
                print(f"   💡 {alert['analysis']}\n")
    else:
        print("\n✅ No significant IV moves detected")
    
    # Send email alert if configured
    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    email_password = os.getenv('EMAIL_PASSWORD')

    if all([email_from, email_to, email_password]):
        print("\n📧 Sending email alert...")
        try:
            from email_alerts import send_email_alert
            send_email_alert(alerts_df, email_from, email_to, email_password, attach_dashboard=False, tracker=tracker)
        except Exception as e:
            print(f"❌ Email error: {str(e)}")
    
    # Send Telegram alert if configured
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if all([telegram_token, telegram_chat_id]):
        print("\n📱 Sending Telegram alert...")
        try:
            from telegram_alerts import TelegramBot
            bot = TelegramBot(telegram_token, telegram_chat_id)
            bot.send_alert_summary(alerts_df)
        except Exception as e:
            print(f"❌ Telegram error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("ALL NOTIFICATIONS SENT")
    print(f"{'='*60}\n")
