"""
Telegram Bot Module
Send IV alerts to Telegram and enable on-demand scans
"""

import os
import requests
from datetime import datetime
import pandas as pd

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text, parse_mode='HTML'):
        """Send text message to Telegram"""
        if not self.bot_token or not self.chat_id:
            print("⚠️  Telegram not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("✅ Telegram message sent")
                return True
            else:
                print(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Telegram exception: {str(e)}")
            return False
    
    def send_alert_summary(self, alerts_df):
        """Send formatted IV alert summary"""
        
        if len(alerts_df) == 0:
            message = f"""
✅ <b>No IV Alerts</b>

📅 {datetime.now().strftime('%B %d, %Y')}

All stocks in watchlist had normal IV changes (<20%)
"""
        else:
            spikes = len(alerts_df[alerts_df['change_pct'] > 0])
            crushes = len(alerts_df[alerts_df['change_pct'] < 0])
            
            message = f"""
🚨 <b>IV ALERT SUMMARY</b>

📅 {datetime.now().strftime('%B %d, %Y')}
📊 {len(alerts_df)} alerts triggered

📈 {spikes} IV Spikes (sell premium)
📉 {crushes} IV Crushes (buy premium)

<b>━━━━━━━━━━━━━━━━━━━━</b>

"""
            
            for _, alert in alerts_df.iterrows():
                emoji = "📈" if alert['change_pct'] > 0 else "📉"
                signal = "SELL" if alert['change_pct'] > 0 else "BUY"
                
                message += f"""
{emoji} <b>{alert['ticker']}</b>: <code>{alert['change_pct']:+.1f}%</code>

   IV: {alert['iv_current']:.1f}% (was {alert['iv_7d_ago']:.1f}%)
   Price: ${alert['price']:.2f}
   Signal: <b>{signal} PREMIUM</b>
"""
                
                if alert.get('analysis'):
                    # Truncate analysis for Telegram (max 200 chars)
                    analysis = alert['analysis'][:200]
                    if len(alert['analysis']) > 200:
                        analysis += "..."
                    message += f"\n   💡 {analysis}\n"
                
                message += "\n"
        
        return self.send_message(message)
    
    def send_document(self, filepath, caption=""):
        """Send file to Telegram"""
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return False
        
        url = f"{self.base_url}/sendDocument"
        
        try:
            with open(filepath, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                print("✅ File sent to Telegram")
                return True
            else:
                print(f"❌ Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending file: {str(e)}")
            return False


def setup_telegram_bot():
    """
    Interactive setup guide for Telegram bot
    """
    print("="*60)
    print("TELEGRAM BOT SETUP GUIDE")
    print("="*60)
    
    print("""
1. Open Telegram and search for @BotFather
2. Send: /newbot
3. Choose a name (e.g., "IV Tracker Bot")
4. Choose a username (e.g., "myname_iv_bot")
5. Copy the API token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)

6. Get your Chat ID:
   a. Search for @userinfobot in Telegram
   b. Start a chat
   c. Copy your ID (looks like: 123456789)

7. Add to .env file:
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
""")
    
    print("\nOnce configured, you can:")
    print("• Get daily alerts on your phone")
    print("• Trigger scans on-demand by messaging the bot")
    print("• Receive Excel reports directly in Telegram")


def test_telegram_connection():
    """Test Telegram bot configuration"""
    bot = TelegramBot()
    
    if not bot.bot_token or not bot.chat_id:
        print("❌ Telegram not configured")
        print("Run: python telegram_alerts.py --setup")
        return False
    
    test_message = f"""
🧪 <b>Test Message</b>

✅ Your IV Tracker bot is working!

{datetime.now().strftime('%B %d, %Y %H:%M')}
"""
    
    return bot.send_message(test_message)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_telegram_bot()
    elif len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_telegram_connection()
    else:
        # Demo
        demo_data = {
            'ticker': ['NVDA', 'AAPL'],
            'iv_current': [58.2, 35.8],
            'iv_7d_ago': [44.0, 28.5],
            'change_pct': [32.3, 25.6],
            'price': [875.50, 182.40],
            'analysis': [
                'Earnings tomorrow. Historical IV crush of 40% expected post-announcement.',
                'Product launch event drove IV spike. Consider iron condors.'
            ]
        }
        
        df = pd.DataFrame(demo_data)
        bot = TelegramBot()
        bot.send_alert_summary(df)
