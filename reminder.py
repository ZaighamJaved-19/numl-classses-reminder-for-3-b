"""
NUML Class Reminder — TEST MODE
Sends a test reminder email regardless of day/time.
Replace with reminder.py after testing.
"""

import os, sys, logging, smtplib
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

CFG = {
    "NOTIFY_EMAIL":  os.getenv("NOTIFY_EMAIL",  "zaighamjaved19@gmail.com"),
    "SMTP_HOST":     "smtp.gmail.com",
    "SMTP_PORT":     587,
    "SMTP_USER":     os.getenv("SMTP_USER",      "zaighamjaved19@gmail.com"),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD",  ""),
}

PKT = timezone(timedelta(hours=5))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("reminder.log"), logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body{{margin:0;padding:0;background:#f0f2f5;font-family:Arial,sans-serif}}
.wrap{{max-width:600px;margin:30px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.12)}}
.header{{padding:28px 32px;background:#1565c0}}
.header h1{{margin:0;color:#fff;font-size:22px;font-weight:700}}
.header p{{margin:6px 0 0;color:#90caf9;font-size:14px}}
.body{{padding:32px}}
.countdown{{text-align:center;background:#e3f2fd;border-radius:12px;padding:24px;margin-bottom:24px}}
.countdown .mins{{font-size:64px;font-weight:700;color:#1565c0;line-height:1}}
.countdown .label{{font-size:15px;color:#555;margin-top:6px}}
.info-card{{background:#f8f9fa;border-radius:10px;padding:4px 20px;margin-bottom:16px}}
.info-row{{display:flex;align-items:center;padding:12px 0;border-bottom:1px solid #eee}}
.info-row:last-child{{border-bottom:none}}
.info-label{{color:#888;font-size:12px;font-weight:700;text-transform:uppercase;width:90px;flex-shrink:0}}
.info-value{{color:#222;font-size:14px;font-weight:500}}
.tip{{background:#e8f5e9;border-left:4px solid #43a047;border-radius:6px;padding:12px 16px;font-size:13px;color:#2e7d32}}
.test-badge{{background:#ff6f00;color:#fff;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;display:inline-block;margin-bottom:16px}}
.footer{{background:#f8f8f8;padding:14px 28px;font-size:12px;color:#aaa;text-align:center;border-top:1px solid #eee}}
</style></head><body>
<div class="wrap">
  <div class="header">
    <h1>💡 Digital Logic Design</h1>
    <p>Monday &nbsp;•&nbsp; Slot 1 (8:30 - 9:45 AM) — TEST EMAIL</p>
  </div>
  <div class="body">
    <span class="test-badge">🧪 TEST MODE — System is working!</span>
    <div class="countdown">
      <div class="mins">10</div>
      <div class="label">minutes until Slot 1 begins</div>
    </div>
    <div class="info-card">
      <div class="info-row">
        <span class="info-label">Subject</span>
        <span class="info-value"><strong>Digital Logic Design</strong></span>
      </div>
      <div class="info-row">
        <span class="info-label">Teacher</span>
        <span class="info-value">Mr. Zarkhtab</span>
      </div>
      <div class="info-row">
        <span class="info-label">Room</span>
        <span class="info-value"><strong>Room 216</strong></span>
      </div>
      <div class="info-row">
        <span class="info-label">Slot Time</span>
        <span class="info-value">8:30 AM — 9:45 AM</span>
      </div>
      <div class="info-row">
        <span class="info-label">Date</span>
        <span class="info-value">Monday (Test)</span>
      </div>
    </div>
    <div class="tip">✅ Your NUML Class Reminder system is working perfectly!</div>
  </div>
  <div class="footer">NUML Class Reminder &nbsp;•&nbsp; {timestamp}</div>
</div>
</body></html>"""

def run():
    now = datetime.now(PKT)
    timestamp = now.strftime("%d %b %Y, %I:%M %p")
    log.info("Sending TEST reminder email...")

    html  = _HTML.format(timestamp=timestamp)
    plain = (
        "TEST EMAIL — NUML Class Reminder\n"
        "===================================\n"
        "Subject:  Digital Logic Design\n"
        "Teacher:  Mr. Zarkhtab\n"
        "Room:     Room 216\n"
        "Slot:     Slot 1 (8:30 - 9:45 AM)\n"
        "Status:   TEST MODE — System working!\n"
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "[NUML] 🧪 TEST: Class Reminder System Working!"
        msg["From"]    = f"NUML Reminder <{CFG['SMTP_USER']}>"
        msg["To"]      = CFG["NOTIFY_EMAIL"]
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html,  "html",  "utf-8"))
        with smtplib.SMTP(CFG["SMTP_HOST"], CFG["SMTP_PORT"], timeout=30) as s:
            s.ehlo(); s.starttls()
            s.login(CFG["SMTP_USER"], CFG["SMTP_PASSWORD"])
            s.sendmail(CFG["SMTP_USER"], CFG["NOTIFY_EMAIL"], msg.as_string())
        log.info("✅ Test email sent successfully!")
    except Exception as e:
        log.error(f"Email failed: {e}")

if __name__ == "__main__":
    run()

