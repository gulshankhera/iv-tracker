"""
Email Alert Module
Sends daily IV summary emails with formatted alerts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import pandas as pd

def send_email_alert(alerts_df, email_from, email_to, email_password, attach_dashboard=False):
    """
    Send formatted email with IV alerts
    
    Args:
        alerts_df: DataFrame with alert data
        email_from: Sender email
        email_to: Recipient email
        email_password: Gmail app password
        attach_dashboard: Whether to attach Excel file
    """
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = f"🚨 IV Alerts - {datetime.now().strftime('%B %d, %Y')}"
    
    # Create email body
    if len(alerts_df) == 0:
        body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
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
</body>
</html>
"""
    else:
        # Build HTML table for alerts
        alerts_html = build_alert_html(alerts_df)
        
        body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #E74C3C; color: white; padding: 20px; text-align: center; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-left: 4px solid #E74C3C; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th {{ background-color: #2C3E50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
        .spike {{ background-color: #ffe5e5; color: #c92a2a; font-weight: bold; }}
        .crush {{ background-color: #e5ffe5; color: #2b8a3e; font-weight: bold; }}
        .analysis {{ background-color: #f1f3f5; padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 14px; }}
        .ticker {{ font-weight: bold; font-size: 16px; }}
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


def build_alert_html(alerts_df):
    """Build HTML table for alerts"""
    
    html = '<div style="margin: 20px 0;">'
    
    for idx, alert in alerts_df.iterrows():
        change_class = 'spike' if alert['change_pct'] > 0 else 'crush'
        emoji = '📈' if alert['change_pct'] > 0 else '📉'
        signal = 'SELL PREMIUM' if alert['change_pct'] > 0 else 'BUY PREMIUM'
        
        html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 15px 0; background-color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span class="ticker">{emoji} {alert['ticker']}</span>
                <span class="{change_class}" style="font-size: 18px; padding: 5px 15px; border-radius: 4px;">
                    {alert['change_pct']:+.1f}%
                </span>
            </div>
            
            <table style="width: 100%; margin: 10px 0;">
                <tr>
                    <td style="border: none; padding: 5px;"><strong>Current IV:</strong></td>
                    <td style="border: none; padding: 5px;">{alert['iv_current']:.1f}%</td>
                    <td style="border: none; padding: 5px;"><strong>7 Days Ago:</strong></td>
                    <td style="border: none; padding: 5px;">{alert['iv_7d_ago']:.1f}%</td>
                </tr>
                <tr>
                    <td style="border: none; padding: 5px;"><strong>Price:</strong></td>
                    <td style="border: none; padding: 5px;">${alert['price']:.2f}</td>
                    <td style="border: none; padding: 5px;"><strong>Signal:</strong></td>
                    <td style="border: none; padding: 5px; color: #E74C3C; font-weight: bold;">{signal}</td>
                </tr>
            </table>
            
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
{"="*60}

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
    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if all([email_from, email_to, email_password]):
        send_email_alert(test_df, email_from, email_to, email_password)
    else:
        print("Set EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD in .env file")
