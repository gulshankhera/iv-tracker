# IV Tracker 📊

**Automated Implied Volatility monitoring with AI-powered analysis for options trading**

Get daily alerts via email/Telegram when IV spikes or crushes, with ChatGPT context analysis.

---

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/iv-tracker.git
cd iv-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials
cp .env .env
# Edit .env with your API keys

# 4. Create watchlist
echo "AAPL\nNVDA\nTSLA" > watchlist.txt

# 5. Run first scan
python iv_tracker.py
```

**That's it!** You'll get a terminal summary + email/Telegram alerts (if configured).

---

## 💰 Cost

**Monthly**: $0.05 - $0.50 (depending on watchlist size)

- Data fetching: **FREE** (Yahoo Finance)
- ChatGPT analysis: **$0.0002 per alert** (GPT-4o-mini)
- Email: **FREE** (Gmail SMTP)
- Telegram: **FREE** (Telegram Bot API)

**Example**: 50 stocks, 5 alerts/day = **$0.30/month**

---

## 🎯 Features

- ✅ **Automated IV tracking** across unlimited stocks
- ✅ **Smart alerts** only on significant moves (>20% by default)
- ✅ **AI analysis** explains WHY IV changed (earnings, news, events)
- ✅ **Email reports** with color-coded Excel dashboards
- ✅ **Telegram bot** for mobile access and on-demand scans
- ✅ **Local database** stores history for trend analysis
- ✅ **Customizable thresholds** for different trading styles
- ✅ **Free deployment options** (PythonAnywhere, Oracle Cloud)

---

## 📧 Notification Channels

### Email (Gmail)
![Email Alert Example](docs/images/email_alert.png)

- Professional HTML formatting
- Color-coded alerts (red=spike, green=crush)
- Optional Excel attachment
- Works on all devices

### Telegram Bot
![Telegram Alert Example](docs/images/telegram_alert.png)

**Two modes:**

1. **Daily Alerts**: Automatic notifications after scan
2. **Interactive Bot**: On-demand scanning from anywhere

**Commands:**
- `/scan` - Run IV scan now
- `/status` - Recent alerts
- `/dashboard` - Get Excel report

---

## 📊 How It Works

```
Daily at 4:15 PM ET:
┌─────────────────────────────────────┐
│  1. Fetch IV for all tickers        │
│     (Yahoo Finance API - free)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Compare to 7 days ago           │
│     (SQLite database)               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Detect >20% changes             │
│     (Configurable threshold)        │
└──────────────┬──────────────────────┘
               │
         ┌─────┴─────┐
         │  Alerts?  │
         └─────┬─────┘
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
  ┌─────────┐    ┌─────────┐
  │  Email  │    │Telegram │
  └─────────┘    └─────────┘
        │              │
        └──────┬───────┘
               ▼
    ┌──────────────────────┐
    │  GPT-4o-mini         │
    │  "Why did NVDA IV    │
    │   spike 32%?"        │
    └──────────────────────┘
```

---

## 🚀 Deployment Options

| Method | Best For | Cost | Always On? |
|--------|----------|------|------------|
| **Your Laptop** | Testing | Free | ❌ |
| **PythonAnywhere** | Beginners | Free | ✅ |
| **Oracle Cloud** | Telegram bot | Free | ✅ |
| **AWS Lambda** | Serverless | $0.50/mo | ✅ |
| **Digital Ocean** | Full control | $4/mo | ✅ |

📖 **Full guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📁 Project Structure

```
iv-tracker/
├── iv_tracker.py           # Main scanner (fetches IV, triggers alerts)
├── generate_dashboard.py   # Excel report generator
├── email_alerts.py         # Email notification module
├── telegram_alerts.py      # Telegram notification module
├── telegram_bot.py         # Interactive Telegram bot
├── setup_test.py          # Verify installation
├── watchlist.txt          # Your tickers (one per line)
├── .env                   # Credentials (create from .env.template)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── DEPLOYMENT.md          # Deployment guide
└── QUICK_REFERENCE.md     # One-page cheat sheet
```

---

## ⚙️ Configuration

Edit `iv_tracker.py` (lines 15-17) or `.env` file:

```python
THRESHOLD_SPIKE = 20     # Alert on X% increase
THRESHOLD_CRUSH = -20    # Alert on X% decrease
LOOKBACK_DAYS = 7        # Compare to X days ago
```

**Recommended by trading style:**
- Conservative: 25%
- Moderate: 20% (default)
- Aggressive: 15%
- Day traders: 10%

---

## 🎓 Usage Examples

### Example 1: Daily Email Alert

```
Subject: 🚨 IV Alerts - March 15, 2024

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Quick Summary
2 stocks triggered alerts today

📈 1 IV Spike (consider selling premium)
📉 1 IV Crush (consider buying premium)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 NVDA: +32.5%
   IV: 58.2% (was 44.0%)
   Price: $875.50
   Signal: SELL PREMIUM
   
   💡 IV spike ahead of earnings (Mar 20). 
   Historical pattern shows 40% crush post-
   announcement. Consider iron condors.

📉 TSLA: -24.1%
   IV: 42.3% (was 55.8%)
   Price: $195.25
   Signal: BUY PREMIUM
   
   💡 Post-earnings IV collapse. Stock moved
   less than anticipated. Good opportunity
   for calendar spreads.
```

### Example 2: Telegram On-Demand Scan

```
You: /scan

Bot: 🔄 Starting IV scan...
     This may take 30-60 seconds.

Bot: 🚨 IV ALERT SUMMARY
     📅 March 15, 2024
     📊 2 alerts triggered
     
     📈 1 IV Spikes (sell premium)
     📉 1 IV Crushes (buy premium)
     
     ━━━━━━━━━━━━━━━━━━━━
     
     📈 NVDA: +32.5%
     IV: 58.2% (was 44.0%)
     ...
```

---

## 🧪 Testing

```bash
# Verify setup
python setup_test.py

# Test email
python email_alerts.py

# Test Telegram
python telegram_alerts.py --test

# Run manual scan
python iv_tracker.py
```

---

## 🔧 Customization Ideas

**Advanced features you can add:**

1. **IV Percentile Tracking**
   - See where current IV ranks vs 90-day history
   - Better context than absolute IV values

2. **Multi-Expiration Analysis**
   - Track 30-day vs 60-day IV
   - Identify calendar spread opportunities

3. **Earnings Calendar Integration**
   - Auto-flag tickers with upcoming earnings
   - Predict IV crush timing

4. **Backtesting Module**
   - Test threshold settings on historical data
   - Optimize for your trading style

5. **Portfolio Integration**
   - Track IV for your current positions
   - Alert when to roll or close

6. **Discord/Slack Integration**
   - Team alerts for trading groups
   - Shared watchlists

---

## 📈 Trading Strategies

### IV Spike (>20% ↑) = Sell Premium

**Strategies:**
- Iron Condors
- Credit Spreads
- Covered Calls
- Cash-Secured Puts

**Example Trade:**
```
AAPL IV: 35% → 52% (+48%)
Action: Sell Iron Condor
- Sell 175/180 Call Spread
- Sell 165/160 Put Spread
- Collect: $250 premium
- Close after earnings (expect IV crush)
```

### IV Crush (>20% ↓) = Buy Premium

**Strategies:**
- Long Calls/Puts (directional)
- Debit Spreads
- Calendar Spreads
- Diagonal Spreads

**Example Trade:**
```
NVDA IV: 60% → 38% (-37%)
Action: Buy Calendar Spread
- Sell front-month 480 Call
- Buy back-month 480 Call
- Profit from IV expansion + theta
```

---

## 🐛 Troubleshooting

**Issue**: No email received
```bash
# Verify Gmail app password (not regular password)
# Must enable 2-step verification first
# Test: python -c "from email_alerts import send_simple_summary; send_simple_summary()"
```

**Issue**: No Telegram messages
```bash
# Test bot token is valid
curl https://api.telegram.org/bot<TOKEN>/getMe

# Verify chat ID
python telegram_alerts.py --test
```

**Issue**: "No IV data available"
- Ticker doesn't have liquid options
- Remove from watchlist.txt or use different ticker

---

## 📚 Resources

- [Options Alpha - IV Guide](https://optionalpha.com/implied-volatility)
- [TastyTrade - IV Rank](https://www.tastytrade.com/concepts-strategies/iv-rank)
- [r/thetagang](https://www.reddit.com/r/thetagang/) - Premium selling strategies
- [OpenAI Pricing](https://openai.com/pricing) - API costs

---

## 🤝 Contributing

Contributions welcome! Ideas:

- [ ] Support for other options data sources (CBOE, IB)
- [ ] Web dashboard (Flask/Streamlit)
- [ ] Mobile app (React Native)
- [ ] Advanced ML predictions
- [ ] Integration with brokerage APIs

---

## ⚖️ Disclaimer

**This tool is for informational purposes only.** It is NOT financial advice.

- Always do your own research
- Understand options risks before trading
- Past IV patterns don't guarantee future results
- Use appropriate position sizing and risk management

**Options trading involves substantial risk of loss.**

---

## 📄 License

MIT License - feel free to modify and distribute

---

## 🌟 Show Your Support

If this project helps your trading, consider:

- ⭐ Star the repository
- 🐛 Report bugs or suggest features
- 📢 Share with other traders
- ☕ [Buy me a coffee](https://buymeacoffee.com/YOUR_HANDLE)

---

**Happy trading! May your IV crushes be profitable. 📊📈**
