"""
Telegram Bot Handler - Interactive IV Tracker
Responds to commands like /scan, /status, /dashboard
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

class InteractiveTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
    
    def get_updates(self):
        """Poll for new messages"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': self.last_update_id + 1, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['result']:
                    self.last_update_id = data['result'][-1]['update_id']
                    return data['result']
        except Exception as e:
            print(f"Error getting updates: {e}")
        
        return []
    
    def send_message(self, text, parse_mode='HTML'):
        """Send message to user"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        requests.post(url, json=payload)
    
    def send_document(self, filepath, caption=""):
        """Send file to user"""
        url = f"{self.base_url}/sendDocument"
        with open(filepath, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': self.chat_id, 'caption': caption}
            requests.post(url, files=files, data=data)
    
    def handle_command(self, command, message_text):
        """Process bot commands"""
        
        if command == '/start':
            self.send_message("""
🤖 <b>IV Tracker Bot</b>

Welcome! I monitor implied volatility for your watchlist.

<b>Commands:</b>
/scan - Run IV scan now
/status - Show recent alerts
/dashboard - Get Excel report
/help - Show this message

Set up daily auto-scans with cron or Task Scheduler.
""")
        
        elif command == '/scan':
            self.send_message("🔄 <b>Starting IV scan...</b>\n\nThis may take 30-60 seconds.")
            self.run_scan()
        
        elif command == '/status':
            self.show_status()
        
        elif command == '/dashboard':
            self.send_dashboard()
        
        elif command == '/help':
            self.handle_command('/start', '')
        
        else:
            self.send_message("❓ Unknown command. Send /help for available commands.")
    
    def run_scan(self):
        """Execute IV scan and send results"""
        try:
            from iv_tracker import IVTracker, load_watchlist
            
            api_key = os.getenv('OPENAI_API_KEY')
            tracker = IVTracker(api_key=api_key)
            watchlist = load_watchlist()
            
            alerts_df = tracker.scan_watchlist(watchlist, use_gpt=(api_key is not None))
            
            # Send results
            from telegram_alerts import TelegramBot
            bot = TelegramBot()
            bot.send_alert_summary(alerts_df)
            
        except Exception as e:
            self.send_message(f"❌ <b>Scan failed:</b>\n\n{str(e)}")
    
    def show_status(self):
        """Show recent alerts from database"""
        try:
            import sqlite3
            import pandas as pd
            from datetime import timedelta
            
            conn = sqlite3.connect('iv_data.db')
            
            cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            query = '''
                SELECT ticker, alert_date, iv_change_pct 
                FROM alerts 
                WHERE alert_date >= ?
                ORDER BY alert_date DESC
                LIMIT 10
            '''
            
            df = pd.read_sql_query(query, conn, params=(cutoff,))
            conn.close()
            
            if len(df) == 0:
                self.send_message("✅ <b>No alerts in last 7 days</b>")
            else:
                message = f"📊 <b>Recent Alerts (Last 7 Days)</b>\n\n"
                for _, row in df.iterrows():
                    emoji = "📈" if row['iv_change_pct'] > 0 else "📉"
                    message += f"{emoji} <b>{row['ticker']}</b>: {row['iv_change_pct']:+.1f}% ({row['alert_date']})\n"
                
                self.send_message(message)
        
        except Exception as e:
            self.send_message(f"❌ Error: {str(e)}")
    
    def send_dashboard(self):
        """Generate and send Excel dashboard"""
        try:
            from generate_dashboard import create_dashboard
            
            self.send_message("📊 <b>Generating dashboard...</b>")
            
            filepath = create_dashboard()
            
            self.send_document(
                filepath,
                caption=f"IV Dashboard - {datetime.now().strftime('%B %d, %Y')}"
            )
            
        except Exception as e:
            self.send_message(f"❌ Dashboard error: {str(e)}")
    
    def start_polling(self):
        """Start bot and listen for commands"""
        print("🤖 Telegram bot started. Listening for commands...")
        print("Send /scan in Telegram to trigger IV scan")
        
        self.send_message("🤖 <b>Bot is now online!</b>\n\nSend /help for commands.")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if 'message' in update:
                        message = update['message']
                        text = message.get('text', '')
                        
                        if text.startswith('/'):
                            command = text.split()[0].lower()
                            self.handle_command(command, text)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)


if __name__ == "__main__":
    bot = InteractiveTelegramBot()
    bot.start_polling()
