"""
Email Alert Module
Sends daily IV summary emails with formatted alerts and IV history table
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import pandas as pd
import sqlite3

DB_PATH = 'iv_data.db'


def send_email_alert(alerts_df, email_from, email_to, email_password, attach_dashboard=False, tracker=None):
    """
    Send formatted email with IV alerts and history table

    Args:
        alerts_df: DataFrame with alert data
        email_from: Sender email
        email_to: Recipient email
        email_password: Gmail app password
        attach_dashboard: Whether to attach Excel file
        tracker: IVTracker instance for getting historical data
    """

    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = f"📊 IV Tracker - {datetime.now().strftime('%B %d, %Y')}"

    # Get IV history table
    iv_table_html = build_iv_history_table(tracker) if tracker else ""

    # Create email body
    if len(alerts_df) == 0:
        body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th {{ background-color: #667eea; color: white; padding: 10px; text-align: left; border: 1px solid #ddd; }}
        td {{ padding: 8px; border: 1px solid #ddd; }}
        .trend {{ font-size: 18px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>✅ No Significant IV Moves Today</h2>
    </div>
    <div class="content">
        <p>All stocks in your watchlist had normal IV changes (<20%).</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
    </div>

    {iv_table_html}

</body>
</html>
"""
    else:
        # Build HTML table for alerts
        alerts_html = build_alert_html(alerts_df, tracker)

        body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #E74C3C; color: white; padding: 20px; text-align: center; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #E74C3C; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th {{ background-color: #667eea; color: white; padding: 10px; text-align: left; border: 1px solid #ddd; }}
        td {{ padding: 8px; border: 1px solid #ddd; }}
        .spike {{ background-color: #ffe5e5; color: #c92a2a; font-weight: bold; }}
        .crush {{ background-color: #e5ffe5; color: #2b8a3e; font-weight: bold; }}
        .analysis {{ background-color: #f1f3f5; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 14px; }}
        .ticker {{ font-weight: bold; font-size: 16px; }}
        .trend {{ font-size: 18px; text-align: center; }}
        .alert-detail {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 15px 0; background-color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🚨 IV Alert Summary</h2>
        <p>{datetime.now().strftime('%B %d, %Y')}</p>
    </div>

    <div class="summary">
        <h3>📊 Quick Summary</h3>
        <p><strong>{len(alerts_df)} stocks</strong> triggered alerts today</p>
        <p>
            📈 <strong>{len(alerts_df[alerts_df['change_pct'] > 0])}</strong> IV Spikes (consider selling premium)<br>
            📉 <strong>{len(alerts_df[alerts_df['change_pct'] < 0])}</strong> IV Crushes (consider buying premium)
        </p>
    </div>

    {iv_table_html}

    <hr style="margin: 30px 0; border: none; border-top: 2px solid #667eea;">
    <h3 style="color: #E74C3C;">🚨 Detailed Alerts (>20% IV Change)</h3>

    {alerts_html}

    <div style="margin-top: 30px; padding: 15px; background-color: #e8f4f8; border-radius: 4px;">
        <p style="margin: 0; font-size: 14px; color: #666;">
            <strong>Note:</strong> This is an automated alert. Always verify with your own analysis before trading.
        </p>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(body, 'html'))

    # Attach dashboard if requested and exists
    if attach_dashboard and os.path.exists('iv_dashboard.xlsx'):
        with open('iv_dashboard.xlsx', 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            f'attachment; filename=iv_dashboard_{datetime.now().strftime("%Y%m%d")}.xlsx')
            msg.attach(part)

    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {email_to}")
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False


def build_iv_history_table(tracker):
    """Build IV history table showing Today, 3-Day, and 7-Day IV for all stocks"""

    if not tracker:
        return ""

    try:
        # Get all current IV data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ticker, iv_30day, price
            FROM iv_history 
            WHERE date = (SELECT MAX(date) FROM iv_history)
            ORDER BY ticker
        ''')
        all_stocks = cursor.fetchall()
        conn.close()

        if not all_stocks:
            return ""

        html = """
        <div style="margin: 30px 0;">
            <h3 style="color: #667eea;">📊 IV History - All Stocks</h3>
            <table style="width:100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #667eea; color: white;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Ticker</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Today</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">3-Day Ago</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">7-Day Ago</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Trend</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, (ticker, current_iv, price) in enumerate(all_stocks):
            if current_iv is None:
                continue

            # Get historical IV
            iv_3day = tracker.get_iv_history(ticker, 3)
            iv_7day = tracker.get_iv_history(ticker, 7)

            # Calculate trend
            trend = "➡️"
            if iv_7day:
                change = ((current_iv - iv_7day) / iv_7day) * 100
                if abs(change) >= 20:
                    trend = "🔥"
                elif change > 10:
                    trend = "📈"
                elif change < -10:
                    trend = "📉"

            # Alternating row colors
            row_color = "#f8f9fa" if idx % 2 == 0 else "white"

            html += f"""
                <tr style="background-color: {row_color};">
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{ticker}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{current_iv:.1f}%</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{f'{iv_3day:.1f}%' if iv_3day else '-'}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{f'{iv_7day:.1f}%' if iv_7day else '-'}</td>
                    <td class="trend" style="padding: 8px; border: 1px solid #ddd;">{trend}</td>
                </tr>
            """

        html += """
                </tbody>
            </table>
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                <strong>Legend:</strong> 🔥 = Major move (±20%+) | 📈 = Rising (>10%) | 📉 = Falling (<-10%) | ➡️ = Stable
            </p>
        </div>
        """

        return html

    except Exception as e:
        print(f"Error building IV table: {str(e)}")
        return ""


def build_alert_html(alerts_df, tracker=None):
    """Build HTML for detailed alerts with IV history"""

    html = '<div style="margin: 20px 0;">'

    for idx, alert in alerts_df.iterrows():
        change_class = 'spike' if alert['change_pct'] > 0 else 'crush'
        emoji = '📈' if alert['change_pct'] > 0 else '📉'
        signal = 'SELL PREMIUM' if alert['change_pct'] > 0 else 'BUY PREMIUM'

        # Get 3-day IV if tracker available
        iv_3day = None
        if tracker:
            iv_3day = tracker.get_iv_history(alert['ticker'], 3)

        html += f"""
        <div class="alert-detail">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span class="ticker">{emoji} {alert['ticker']}</span>
                <span class="{change_class}" style="font-size: 18px; padding: 5px 15px; border-radius: 4px;">
                    {alert['change_pct']:+.1f}% (7-day)
                </span>
            </div>

            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0;">
                <p style="margin: 5px 0;"><strong>Today:</strong> {alert['iv_current']:.1f}%</p>
                {f"<p style='margin: 5px 0;'><strong>3 Days Ago:</strong> {iv_3day:.1f}%</p>" if iv_3day else ""}
                <p style="margin: 5px 0;"><strong>7 Days Ago:</strong> {alert['iv_7d_ago']:.1f}%</p>
                <p style="margin: 5px 0;"><strong>Current Price:</strong> ${alert['price']:.2f}</p>
                <p style="margin: 5px 0;"><strong>Trade Signal:</strong> <span style="color: #E74C3C; font-weight: bold;">{signal}</span></p>
            </div>

            {f'<div class="analysis"><strong>💡 Analysis:</strong><br>{alert["analysis"]}</div>' if alert.get('analysis') else ''}
        </div>
        """

    html += '</div>'
    return html


def send_simple_summary(alerts_df, email_from, email_to, email_password):
    """Send plain text summary (fallback if HTML fails)"""

    msg = MIMEText(format_text_summary(alerts_df))
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = f"IV Alerts - {datetime.now().strftime('%Y-%m-%d')}"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Simple email sent to {email_to}")
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False


def format_text_summary(alerts_df):
    """Format plain text summary"""

    if len(alerts_df) == 0:
        return f"""
IV TRACKER - {datetime.now().strftime('%B %d, %Y')}

✅ No significant IV moves today
All stocks had normal volatility (<20% change)
"""

    text = f"""
IV TRACKER - {datetime.now().strftime('%B %d, %Y')}
{"=" * 60}

🚨 {len(alerts_df)} ALERTS TRIGGERED

"""

    for _, alert in alerts_df.iterrows():
        emoji = "📈" if alert['change_pct'] > 0 else "📉"
        signal = "SELL PREMIUM" if alert['change_pct'] > 0 else "BUY PREMIUM"

        text += f"""
{emoji} {alert['ticker']}: {alert['change_pct']:+.1f}%
   Current IV: {alert['iv_current']:.1f}%  |  7 Days Ago: {alert['iv_7d_ago']:.1f}%
   Price: ${alert['price']:.2f}
   Signal: {signal}
"""

        if alert.get('analysis'):
            text += f"   💡 {alert['analysis']}\n"

        text += "\n"

    return text


if __name__ == "__main__":
    # Test email
    test_data = {
        'ticker': ['NVDA', 'TSLA'],
        'iv_current': [58.2, 42.3],
        'iv_7d_ago': [44.0, 55.8],
        'change_pct': [32.3, -24.2],
        'price': [875.50, 195.25],
        'analysis': [
            'IV spike ahead of earnings. Historical pattern shows 40% crush post-announcement.',
            'Post-earnings IV collapse. Good opportunity for calendar spreads.'
        ]
    }

    test_df = pd.DataFrame(test_data)

    # Load credentials
    from dotenv import load_dotenv

    load_dotenv()

    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    email_password = os.getenv('EMAIL_PASSWORD')

    if all([email_from, email_to, email_password]):
        send_email_alert(test_df, email_from, email_to, email_password)
    else:
        print("Set EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD in .env file")
