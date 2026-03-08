# 🚀 COMPLETE SETUP: IV Tracker with Email/Telegram Alerts

**Your automated options trading assistant is ready!**

---

## ✅ What You Have Now

A complete IV tracking system that:

1. **Runs automatically** (cloud/scheduled) or on-demand
2. **Sends daily email alerts** with IV changes and AI analysis
3. **Works via Telegram** for mobile access from anywhere
4. **Costs under $1/month** to run (ChatGPT API only)
5. **Deploys anywhere** - laptop, cloud, GitHub

---

## 📦 Files Included

### Core Scripts
- `iv_tracker.py` - Main scanner (fetches IV, compares history, triggers alerts)
- `generate_dashboard.py` - Creates Excel reports
- `email_alerts.py` - Email notification engine (Gmail SMTP)
- `telegram_alerts.py` - Telegram notification module
- `telegram_bot.py` - Interactive bot (on-demand scans)
- `setup_test.py` - Verify installation

### Configuration
- `.env.template` - Credentials template (copy to `.env`)
- `watchlist.txt` - Your tickers (edit this)
- `requirements.txt` - Python dependencies
- `.gitignore` - Git exclusions

### Documentation
- `README_GITHUB.md` - For GitHub repository
- `DEPLOYMENT.md` - All deployment options
- `QUICK_REFERENCE.md` - One-page cheat sheet
- `IV_Tracker_Implementation_Guide.docx` - Professional guide

---

## 🎯 Quick Start Paths

### Path 1: GitHub → Your Laptop (5 minutes)

**Best for**: Learning, testing, full control

```bash
# 1. Upload to GitHub
cd /path/to/files
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/iv-tracker.git
git push -u origin main

# 2. Clone on your laptop
git clone https://github.com/YOUR_USERNAME/iv-tracker.git
cd iv-tracker

# 3. Install and configure
pip install -r requirements.txt
cp .env .env
# Edit .env with your keys

# 4. Run
python iv_tracker.py
```

**Result**: ✅ Scan runs, email sent, Telegram notified

---

### Path 2: GitHub → PythonAnywhere (15 minutes)

**Best for**: Free automated daily scans forever

**Steps:**

1. **Upload to GitHub** (see Path 1)

2. **Sign up PythonAnywhere**: https://www.pythonanywhere.com (free)

3. **Clone in PythonAnywhere**:
   - Open "Bash" console
   ```bash
   git clone https://github.com/YOUR_USERNAME/iv-tracker.git
   cd iv-tracker
   pip3 install --user -r requirements.txt
   ```

4. **Add credentials**:
   ```bash
   nano .env
   # Paste your API keys
   # Ctrl+X, Y, Enter to save
   ```

5. **Schedule task**:
   - Click "Tasks" tab
   - Add scheduled task:
     - Command: `python3 /home/YOUR_USERNAME/iv-tracker/iv_tracker.py`
     - Time: 16:15 (4:15 PM ET)

6. **Done!** You'll get daily emails automatically.

**Cost**: $0 forever (free tier)

---

### Path 3: GitHub → Oracle Cloud + Telegram Bot (30 minutes)

**Best for**: Free VM, run Telegram bot 24/7

**Steps:**

1. **Upload to GitHub** (see Path 1)

2. **Create Oracle Cloud VM**:
   - Sign up: https://www.oracle.com/cloud/free/
   - Create instance: Ubuntu 22.04, Always Free tier
   - Note public IP address

3. **SSH and setup**:
   ```bash
   ssh ubuntu@YOUR_IP_ADDRESS
   
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip git -y
   
   # Clone repo
   git clone https://github.com/YOUR_USERNAME/iv-tracker.git
   cd iv-tracker
   pip3 install -r requirements.txt
   
   # Add credentials
   nano .env
   # Paste all your keys (OpenAI, Email, Telegram)
   # Save and exit
   ```

4. **Schedule daily scans**:
   ```bash
   crontab -e
   # Add: 15 16 * * 1-5 cd /home/ubuntu/iv-tracker && python3 iv_tracker.py
   ```

5. **Start interactive Telegram bot** (optional):
   ```bash
   nohup python3 telegram_bot.py &
   ```

6. **Test from Telegram**:
   - Open Telegram
   - Message your bot: `/scan`
   - Get instant results!

**Cost**: $0 forever (always free tier)

---

## 📧 Email Setup (Required for All Paths)

### Get Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" (if not already)
3. Scroll to "App passwords"
4. Select app: "Mail"
5. Select device: "Other" (name it "IV Tracker")
6. Copy 16-character password (e.g., `abcd efgh ijkl mnop`)
7. Paste in `.env` file:
   ```
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=your_email@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   ```

**Test**:
```bash
python email_alerts.py
```

Should receive test email immediately.

---

## 📱 Telegram Setup (Optional but Recommended)

### Create Telegram Bot:

1. Open Telegram app
2. Search for `@BotFather`
3. Send: `/newbot`
4. Name your bot: "IV Tracker Bot"
5. Username: "YOUR_NAME_iv_bot"
6. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Get Your Chat ID:

1. Search for `@userinfobot`
2. Start a chat
3. **Copy your ID** (looks like: `123456789`)

### Add to .env:

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### Test:

```bash
python telegram_alerts.py --test
```

Should receive "Test Message" in Telegram.

---

## 🔄 Daily Workflow

### Automatic (No Action Needed)

**4:15 PM ET every weekday:**
1. Scanner runs automatically (cloud/cron)
2. Compares IV to 7 days ago
3. Finds significant moves (>20% change)
4. ChatGPT analyzes WHY
5. Sends email summary
6. Sends Telegram alert
7. Done!

### On-Demand (From Anywhere)

**In Telegram:**
- Send `/scan` → Get instant IV update
- Send `/status` → See recent alerts
- Send `/dashboard` → Download Excel report

**On laptop:**
```bash
python iv_tracker.py
```

---

## 💰 Cost Breakdown

### Completely Free:
- ✅ Data (Yahoo Finance)
- ✅ Email (Gmail SMTP)
- ✅ Telegram (Bot API)
- ✅ Hosting (PythonAnywhere or Oracle Cloud free tiers)

### Paid:
- ⚠️ ChatGPT API: $0.0002 per alert
- **Example**: 50 stocks, 5 alerts/day, 22 days/month = 110 alerts = **$0.22/month**

### Total Cost: $0.22 - $0.50/month

**Free trial**: $5 free credit from OpenAI (lasts months)

---

## 🎨 Customization Options

### Adjust Alert Thresholds

Edit `iv_tracker.py` lines 15-17:

```python
THRESHOLD_SPIKE = 20     # Higher = fewer alerts
THRESHOLD_CRUSH = -20    # Lower = more alerts
LOOKBACK_DAYS = 7        # Longer = smoother trends
```

**Or** edit `.env`:
```
THRESHOLD_SPIKE=25
THRESHOLD_CRUSH=-25
LOOKBACK_DAYS=14
```

### Edit Watchlist

Just edit `watchlist.txt`:
```
AAPL
NVDA
TSLA
MSFT
AMD
```

One ticker per line. Add as many as you want.

---

## 📊 What You'll Receive

### Daily Email Example:

```
Subject: 🚨 IV Alerts - March 15, 2024

━━━━━━━━━━━━━━━━━━━━
📊 Quick Summary
2 stocks triggered alerts

📈 1 IV Spike (sell premium)
📉 1 IV Crush (buy premium)
━━━━━━━━━━━━━━━━━━━━

📈 NVDA: +32.5%
   Current IV: 58.2%
   7 Days Ago: 44.0%
   Price: $875.50
   Signal: SELL PREMIUM
   
   💡 Analysis: IV spike ahead of 
   earnings (Mar 20). Historical 
   pattern shows 40% crush post-
   announcement. Consider iron condors.

📉 TSLA: -24.1%
   Current IV: 42.3%
   7 Days Ago: 55.8%
   Price: $195.25
   Signal: BUY PREMIUM
   
   💡 Analysis: Post-earnings collapse.
   Good opportunity for calendar spreads.
```

### Telegram Message Example:

```
🚨 IV ALERT SUMMARY
📅 March 15, 2024
📊 2 alerts triggered

📈 1 IV Spikes (sell premium)
📉 1 IV Crushes (buy premium)

━━━━━━━━━━━━━━

📈 NVDA: +32.5%
   IV: 58.2% (was 44.0%)
   Price: $875.50
   Signal: SELL PREMIUM
   💡 Earnings tomorrow...

📉 TSLA: -24.1%
   ...
```

---

## 🧪 Testing Checklist

Before going live:

- [ ] `python setup_test.py` - Verify installation
- [ ] `python iv_tracker.py` - Run manual scan
- [ ] Check email inbox - Should receive alert
- [ ] Check Telegram - Should receive message
- [ ] `python generate_dashboard.py` - Create Excel
- [ ] Open Excel file - Verify formatting
- [ ] Test with 2-3 tickers first (SPY, QQQ, AAPL)
- [ ] Run daily for 7 days to build baseline
- [ ] Then scale to full watchlist

---

## 🐛 Common Issues & Fixes

**"No module named 'yfinance'"**
```bash
pip install -r requirements.txt
```

**"Email authentication failed"**
- Use Gmail **app password**, not regular password
- Must enable 2-step verification first
- Password is 16 chars, no spaces

**"Telegram not configured"**
- Verify bot token in `.env`
- Verify chat ID in `.env`
- Test: `python telegram_alerts.py --test`

**"No IV data for ticker"**
- Stock doesn't have options
- Or options not liquid enough
- Remove from watchlist.txt

**Empty email/Telegram**
- Normal if no stocks exceeded threshold
- Lower threshold to 15% for more alerts
- Or wait for actual volatility event

---

## 🚀 Next Steps

### Week 1: Setup & Baseline
- [ ] Choose deployment method
- [ ] Configure credentials
- [ ] Run daily scans (manually or automated)
- [ ] Build 7 days of historical data

### Week 2: Active Monitoring
- [ ] Review daily emails
- [ ] Note which alerts are actionable
- [ ] Adjust thresholds if too many/few alerts
- [ ] Start paper trading based on signals

### Week 3: Optimization
- [ ] Set up full automation (cron/cloud)
- [ ] Enable Telegram bot for mobile access
- [ ] Track which signals led to profitable trades
- [ ] Fine-tune watchlist (remove illiquid stocks)

### Month 2+: Advanced
- [ ] Add IV percentile tracking
- [ ] Integrate earnings calendar
- [ ] Build custom strategies
- [ ] Share with trading group

---

## 💡 Pro Tips

1. **Start small**: 10-20 liquid stocks (SPY, QQQ, AAPL, NVDA, etc.)
2. **Run manually first**: Understand the system before automating
3. **Track results**: Note which IV alerts led to wins
4. **Combine signals**: IV + technical + fundamentals = better trades
5. **Use filters**: Only trade IV >30% (ensures liquidity)
6. **Adjust for style**: Day traders need lower thresholds (10-15%)
7. **Check before earnings**: IV typically spikes 5-10 days before
8. **Review monthly**: What % of alerts were profitable?

---

## 📞 Support

**Stuck?**

1. Check `DEPLOYMENT.md` for your specific setup
2. Review `QUICK_REFERENCE.md` for common commands
3. Test individual components:
   - Email: `python email_alerts.py`
   - Telegram: `python telegram_alerts.py --test`
   - Scanner: `python iv_tracker.py`

4. Start with minimal setup (2 tickers, laptop only)
5. Then gradually add features (email, Telegram, automation)

**Still having issues?**
- Check GitHub Issues
- Review code comments
- Verify API keys are correct
- Test with fresh `.env` file

---

## 🎉 You're All Set!

**Your IV tracking system is ready to go:**

✅ **Code**: All scripts created  
✅ **Docs**: Comprehensive guides  
✅ **Config**: Templates ready  
✅ **Deploy**: Multiple options available  
✅ **Alerts**: Email + Telegram configured  

**Pick your deployment method and start receiving automated IV alerts today!**

---

## 📚 File Reference

```
iv-tracker/
├── iv_tracker.py              ← Run this for daily scan
├── telegram_bot.py            ← Run for interactive bot
├── generate_dashboard.py      ← Create Excel reports
├── .env                       ← YOUR credentials (create from template)
├── watchlist.txt              ← YOUR tickers
├── DEPLOYMENT.md              ← Choose how to deploy
├── QUICK_REFERENCE.md         ← Daily cheat sheet
└── README_GITHUB.md           ← Upload to GitHub
```

---

**Happy trading! 📊 May your IV signals be profitable and your options strategies successful! 🚀**
