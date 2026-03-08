# IV Tracker - Deployment Guide

**Get daily email/Telegram alerts automatically**

---

## 🎯 Quick Setup Overview

```
1. Clone from GitHub → 2 minutes
2. Set up credentials → 3 minutes  
3. Choose deployment → 5-30 minutes
4. Done! Receive daily alerts
```

---

## 📥 Step 1: Get the Code from GitHub

### Method A: Clone Repository (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/iv-tracker.git
cd iv-tracker
```

### Method B: Download ZIP

1. Go to GitHub repository page
2. Click green "Code" button
3. Download ZIP
4. Extract to a folder

---

## ⚙️ Step 2: Configure Credentials

### 2.1 Create .env File

Copy the template:
```bash
cp .env .env
```

### 2.2 Edit .env File

Open `.env` in text editor and fill in:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Required for Email: Gmail credentials
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNO
TELEGRAM_CHAT_ID=123456789
```

### 2.3 Get Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already)
3. Go to "App passwords"
4. Generate password for "Mail"
5. Copy 16-character password (no spaces)
6. Paste in `.env` as `EMAIL_PASSWORD`

### 2.4 Get Telegram Credentials (Optional)

**Get Bot Token:**
```
1. Open Telegram
2. Search @BotFather
3. Send: /newbot
4. Follow prompts
5. Copy token
```

**Get Chat ID:**
```
1. Search @userinfobot
2. Start chat
3. Copy your ID
```

### 2.5 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Step 3: Choose Your Deployment

**Pick ONE that fits your needs:**

| Method | Best For | Cost | Setup Time |
|--------|----------|------|------------|
| **A. Your Laptop** | Learning, testing | Free | 5 min |
| **B. Cloud (Free Tier)** | Set & forget | Free | 15 min |
| **C. Cloud (Paid)** | Production | $5/mo | 30 min |
| **D. Docker** | Advanced users | Free | 20 min |

---

## 📍 Deployment Method A: Your Laptop (Manual/Scheduled)

**Best for**: Testing and learning

### Option A1: Run Manually

```bash
python iv_tracker.py
```

**Pros**: Full control, easy debugging  
**Cons**: Must remember to run daily

### Option A2: Schedule with Cron (Mac/Linux)

```bash
crontab -e
```

Add this line (runs 4:15 PM weekdays):
```bash
15 16 * * 1-5 cd /path/to/iv-tracker && python3 iv_tracker.py
```

### Option A3: Schedule with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 4:15 PM, Monday-Friday
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\iv-tracker\iv_tracker.py`
   - Start in: `C:\path\to\iv-tracker`

**Pros**: Free, runs locally  
**Cons**: Laptop must be on and connected

---

## ☁️ Deployment Method B: Cloud - Free Tier

### Option B1: PythonAnywhere (Free Forever)

**Perfect for daily scans, completely free**

**Setup:**

1. Sign up: https://www.pythonanywhere.com (free tier)

2. Upload files:
   - Click "Files" tab
   - Upload all `.py` files
   - Upload `requirements.txt`, `.env`, `watchlist.txt`

3. Open Bash console:
   ```bash
   pip3 install --user -r requirements.txt
   ```

4. Set up scheduled task:
   - Click "Tasks" tab
   - Add: `python3 /home/YOUR_USERNAME/iv_tracker.py`
   - Time: 16:15 (4:15 PM ET)

5. Done! You'll get daily emails automatically

**Limitations:**
- Free tier: 1 scheduled task, 100 seconds CPU/day
- More than enough for IV scanning

---

### Option B2: Oracle Cloud (Always Free)

**Free forever with generous limits**

**Setup:**

1. Sign up: https://www.oracle.com/cloud/free/

2. Create VM instance (Always Free eligible):
   - Shape: VM.Standard.E2.1.Micro
   - OS: Ubuntu 22.04

3. SSH into instance and run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/iv-tracker.git
   cd iv-tracker
   pip3 install -r requirements.txt
   
   # Create .env file
   nano .env
   # Paste your credentials, save (Ctrl+X, Y, Enter)
   ```

4. Set up cron job:
   ```bash
   crontab -e
   ```
   Add: `15 16 * * 1-5 cd /home/ubuntu/iv-tracker && python3 iv_tracker.py`

5. Test:
   ```bash
   python3 iv_tracker.py
   ```

**Pros**: 
- Free forever
- Always on
- Can run Telegram bot 24/7

---

## 💰 Deployment Method C: Cloud - Paid (Production)

### Option C1: AWS Lambda (Pay-per-use)

**Best for**: Minimal cost, serverless

**Cost**: ~$0.50/month

**Setup:**

1. Create Lambda function (Python 3.11)
2. Upload code as ZIP
3. Set environment variables (OpenAI key, email creds)
4. Add EventBridge trigger (cron: `15 16 ? * MON-FRI *`)
5. Increase timeout to 5 minutes

**Guide**: See `docs/aws_lambda_setup.md`

---

### Option C2: Digital Ocean Droplet

**Best for**: Full control, easy setup

**Cost**: $4-6/month

**Setup:**

1. Create Droplet: https://www.digitalocean.com/
   - Ubuntu 22.04
   - Basic plan ($4/mo)

2. SSH and setup:
   ```bash
   git clone https://github.com/YOUR_USERNAME/iv-tracker.git
   cd iv-tracker
   pip3 install -r requirements.txt
   nano .env  # Add credentials
   crontab -e  # Add schedule
   ```

**Pros**: 
- Simple, reliable
- Can run Telegram bot 24/7
- Easy to access and debug

---

## 🐳 Deployment Method D: Docker (Advanced)

**Best for**: Containerized deployment

**Setup:**

```bash
# Build image
docker build -t iv-tracker .

# Run container with cron
docker run -d --name iv-tracker \
  --env-file .env \
  -v $(pwd)/iv_data.db:/app/iv_data.db \
  iv-tracker
```

See `Dockerfile` in repo for details.

---

## 📱 Mobile Access Options

### Option 1: Email Alerts (Already Configured)

**Setup**: Done! If `.env` has email credentials.

**Pros**: 
- Works on any phone
- No additional app needed
- Email can include attachments

---

### Option 2: Telegram Bot (Recommended)

**Two modes:**

**Mode A: Daily Alerts Only**
```bash
# Already works if TELEGRAM_BOT_TOKEN is in .env
python iv_tracker.py  # Sends to Telegram automatically
```

**Mode B: Interactive Bot (On-Demand Scans)**

```bash
# Start bot (keeps running, listens for commands)
python telegram_bot.py
```

**Commands in Telegram:**
- `/scan` - Run IV scan now
- `/status` - Show recent alerts
- `/dashboard` - Get Excel file
- `/help` - Show commands

**Where to run Mode B:**
- Cloud server (Oracle, Digital Ocean) - recommended
- Your laptop (if always on)
- Docker container

**Example on Oracle Cloud:**
```bash
# SSH into server
cd iv-tracker
nohup python3 telegram_bot.py &
```

Now you can trigger scans from anywhere by messaging the bot!

---

### Option 3: WhatsApp (Alternative)

**Use Twilio WhatsApp API:**

1. Sign up: https://www.twilio.com
2. Set up WhatsApp sandbox
3. Modify `email_alerts.py` to use Twilio API instead of Gmail

**Code snippet:**
```python
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=alert_text,
    to='whatsapp:+1YOUR_NUMBER'
)
```

**Cost**: ~$0.005 per message

---

## 🧪 Testing Your Setup

### Test 1: Manual Run

```bash
python iv_tracker.py
```

Should see:
- ✅ Scans complete
- ✅ Email sent (check inbox)
- ✅ Telegram sent (check app)

### Test 2: Email Only

```bash
python -c "from email_alerts import test_email_connection; test_email_connection()"
```

### Test 3: Telegram Only

```bash
python telegram_alerts.py --test
```

---

## 📊 Sample Daily Workflow

**Morning (9:00 AM):**
1. Check email for IV alerts
2. Open dashboard Excel attachment
3. Review red/green highlighted stocks

**On the Road:**
- Open Telegram
- Send `/scan` to bot
- Get instant results

**Evening:**
- Automated scan runs at 4:15 PM
- Receive email + Telegram summary
- Plan next day's trades

---

## 🔧 Troubleshooting

**No email received:**
```bash
# Check Gmail app password (16 chars, no spaces)
# Verify 2-step verification is enabled
# Test: python -c "from email_alerts import send_simple_summary; send_simple_summary()"
```

**No Telegram messages:**
```bash
# Test bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Verify chat ID
python telegram_alerts.py --test
```

**Scan fails:**
```bash
# Check logs
tail -f scan.log

# Verify API key
echo $OPENAI_API_KEY
```

---

## 💡 Recommendations

**For Beginners:**
- Start with **PythonAnywhere** (100% free, no server management)
- Use **Email alerts** (no Telegram setup needed)
- Run **manually** for first week to learn

**For Active Traders:**
- Use **Oracle Cloud** (free VM, run Telegram bot 24/7)
- Enable both **Email + Telegram**
- Set up **on-demand scanning** via Telegram

**For Tech-Savvy:**
- Use **Docker on Digital Ocean**
- Customize alerts and thresholds
- Add your own indicators

---

## 📚 Next Steps

1. **Choose deployment** from options above
2. **Test thoroughly** for 1 week
3. **Adjust thresholds** in `iv_tracker.py`
4. **Track results** - which alerts led to wins
5. **Scale up** - add more tickers, features

---

## 🆘 Get Help

**Common issues:**
- Email setup: `docs/email_setup.md`
- Telegram setup: `docs/telegram_setup.md`
- Cloud deployment: `docs/cloud_deployment.md`

**Still stuck?**
- Check GitHub Issues
- Review code comments
- Test with minimal watchlist (2-3 stocks)

---

**You're all set! Pick a deployment method and start receiving automated IV alerts. 🚀**
