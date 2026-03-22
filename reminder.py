"""
NUML Class Reminder System
============================
Sends email reminders:
- 8:20 AM  → First class starting in 10 mins
- 9:45 AM  → Slot 2 starting in 10 mins
- 11:10 AM → Second class starting in 10 mins
- 12:35 PM → Slot 4 starting in 10 mins

Timetable:
  Monday:    Slots 1&2 = Digital Logic Design  | Slot 3     = Linear Algebra
  Tuesday:   Slots 1&2 = Database Systems      | Slots 3&4  = DLD Lab
  Wednesday: Slots 1&2 = Data Structures       | Slots 3&4  = Digital Marketing
  Thursday:  Slots 1&2 = DB Systems Lab        | Slots 3&4  = Data Structures
  Friday:    Slots 1&2 = Tech Entrepreneurship | Slot 3     = Linear Algebra
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

# Pakistan Standard Time = UTC+5
PKT = timezone(timedelta(hours=5))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("reminder.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────
#  SLOT DEFINITIONS
# ─────────────────────────────────────────────────────

SLOTS = {
    1: {"start": (8,  30), "end": (9,  45), "label": "Slot 1 (8:30 - 9:45 AM)"},
    2: {"start": (9,  55), "end": (11, 10), "label": "Slot 2 (9:55 - 11:10 AM)"},
    3: {"start": (11, 20), "end": (12, 35), "label": "Slot 3 (11:20 AM - 12:35 PM)"},
    4: {"start": (12, 45), "end": (14,  0), "label": "Slot 4 (12:45 - 2:00 PM)"},
}

# Reminder times = 10 mins before each slot starts
# Slot 1 starts 8:30 → remind at 8:20
# Slot 2 starts 9:55 → remind at 9:45 (end of slot 1)
# Slot 3 starts 11:20 → remind at 11:10 (end of slot 2)
# Slot 4 starts 12:45 → remind at 12:35 (end of slot 3)

REMINDER_TIMES = {
    1: (8,  20),   # 10 mins before Slot 1
    2: (9,  45),   # End of Slot 1 = 10 mins before Slot 2
    3: (11, 10),   # End of Slot 2 = 10 mins before Slot 3
    4: (12, 35),   # End of Slot 3 = 10 mins before Slot 4
}

# ─────────────────────────────────────────────────────
#  TIMETABLE
# ─────────────────────────────────────────────────────
# Format per day: list of (slot_numbers, subject, teacher, room)
# slot_numbers = which slots this course occupies

TIMETABLE = {
    0: [  # Monday
        ([1, 2], "Digital Logic Design",          "Mr. Zarkhtab",          "Room 216"),
        ([3],    "Linear Algebra",                "Ms. Zainab",             "Room 217"),
    ],
    1: [  # Tuesday
        ([1, 2], "Database Systems",              "Ms. Sobia Shafiq",       "Room 216"),
        ([3, 4], "Digital Logic Design Lab",      "Mr. Tahir",              "Room 217"),
    ],
    2: [  # Wednesday
        ([1, 2], "Data Structures",               "Ms. Kahkishan Sanam",    "Room 216"),
        ([3, 4], "Digital Marketing",             "Mr. Azaz Ahmed Kayani",  "Room 216"),
    ],
    3: [  # Thursday
        ([1, 2], "Database Systems Lab",          "Mr. Tayyab Hussain",     "LAB 07"),
        ([3, 4], "Data Structures",               "Ms. Kahkishan Sanam",    "Room 217"),
    ],
    4: [  # Friday
        ([1, 2], "Technology Entrepreneurship",   "Ms. Shaguita Ejaz",      "Room 217"),
        ([3],    "Linear Algebra",                "Ms. Zainab",             "Room 217"),
    ],
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

SUBJECT_EMOJIS = {
    "Digital Logic Design":          "💡",
    "Digital Logic Design Lab":      "🔬",
    "Linear Algebra":                "📐",
    "Database Systems":              "🗄️",
    "Database Systems Lab":          "🔬",
    "Data Structures":               "🌳",
    "Digital Marketing":             "📱",
    "Technology Entrepreneurship":   "🚀",
}

def _accent(subject: str) -> tuple:
    if "Lab" in subject:
        return "#2e7d32", "#a5d6a7", "#e8f5e9"
    elif "Linear Algebra" in subject:
        return "#1565c0", "#90caf9", "#e3f2fd"
    elif "Data Structures" in subject:
        return "#0277bd", "#81d4fa", "#e1f5fe"
    elif "Database" in subject:
        return "#6a1b9a", "#ce93d8", "#f3e5f5"
    elif "Digital Logic" in subject:
        return "#e65100", "#ffcc80", "#fff3e0"
    elif "Digital Marketing" in subject:
        return "#c62828", "#ef9a9a", "#ffebee"
    elif "Technology" in subject:
        return "#00695c", "#80cbc4", "#e0f2f1"
    return "#1a56b0", "#b8d4f8", "#e8f0fc"

# ─────────────────────────────────────────────────────
#  EMAIL TEMPLATE
# ─────────────────────────────────────────────────────

_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;padding:0;background:#f0f2f5;font-family:Arial,Helvetica,sans-serif}}
.wrap{{max-width:600px;margin:30px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.12)}}
.header{{padding:28px 32px;background:{accent}}}
.header h1{{margin:0;color:#fff;font-size:22px;font-weight:700}}
.header p{{margin:6px 0 0;color:{accent_light};font-size:14px}}
.body{{padding:32px}}
.countdown{{text-align:center;background:{accent_bg};border-radius:12px;padding:24px;margin-bottom:24px}}
.countdown .mins{{font-size:64px;font-weight:700;color:{accent};line-height:1}}
.countdown .label{{font-size:15px;color:#555;margin-top:6px}}
.slot-badge{{display:inline-block;background:{accent};color:#fff;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:700;margin-bottom:20px}}
.info-card{{background:#f8f9fa;border-radius:10px;padding:4px 20px;margin-bottom:16px}}
.info-row{{display:flex;align-items:center;padding:12px 0;border-bottom:1px solid #eee}}
.info-row:last-child{{border-bottom:none}}
.info-label{{color:#888;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;width:90px;flex-shrink:0}}
.info-value{{color:#222;font-size:14px;font-weight:500}}
.continuing{{background:#fff8e1;border-left:4px solid #f9a825;border-radius:6px;padding:12px 16px;font-size:13px;color:#5d4037;margin-bottom:16px}}
.tip{{background:#e8f5e9;border-left:4px solid #43a047;border-radius:6px;padding:12px 16px;font-size:13px;color:#2e7d32}}
.footer{{background:#f8f8f8;padding:14px 28px;font-size:12px;color:#aaa;text-align:center;border-top:1px solid #eee}}
</style></head><body>
<div class="wrap">
  <div class="header">
    <h1>{emoji} {subject}</h1>
    <p>{day} &nbsp;•&nbsp; {slot_label}</p>
  </div>
  <div class="body">
    <div class="countdown">
      <div class="mins">10</div>
      <div class="label">minutes until {slot_label} begins</div>
    </div>
    {continuing_banner}
    <div class="info-card">
      <div class="info-row">
        <span class="info-label">Subject</span>
        <span class="info-value"><strong>{subject}</strong></span>
      </div>
      <div class="info-row">
        <span class="info-label">Teacher</span>
        <span class="info-value">{teacher}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Room</span>
        <span class="info-value"><strong>{room}</strong></span>
      </div>
      <div class="info-row">
        <span class="info-label">Slot Time</span>
        <span class="info-value">{slot_time}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Date</span>
        <span class="info-value">{day}, {date}</span>
      </div>
    </div>
    <div class="tip">💡 Head to <strong>{room}</strong> now. Don't be late!</div>
  </div>
  <div class="footer">NUML Class Reminder &nbsp;•&nbsp; {timestamp}</div>
</div>
</body></html>"""

def build_and_send(slot_num: int, subject: str, teacher: str, room: str,
                   is_continuing: bool, day_name: str, now: datetime):
    slot      = SLOTS[slot_num]
    emoji     = SUBJECT_EMOJIS.get(subject, "📚")
    ac, al, ab = _accent(subject)
    date_str  = now.strftime("%d %B %Y")
    timestamp = now.strftime("%d %b %Y, %I:%M %p")
    sh, sm    = slot["start"]
    eh, em    = slot["end"]
    slot_time = f"{sh:02d}:{sm:02d} {'AM' if sh < 12 else 'PM'} — {eh % 12 or 12:02d}:{em:02d} {'AM' if eh < 12 else 'PM'}"

    continuing_banner = ""
    if is_continuing:
        continuing_banner = f'<div class="continuing">🔄 This is a continuation of the same class — same room, same teacher!</div>'

    html = _HTML.format(
        emoji=emoji, subject=subject, day=day_name,
        slot_label=slot["label"], teacher=teacher, room=room,
        slot_time=slot_time, date=date_str, timestamp=timestamp,
        accent=ac, accent_light=al, accent_bg=ab,
        continuing_banner=continuing_banner,
    )

    plain = (
        f"CLASS REMINDER — 10 minutes!\n{'='*40}\n"
        f"Subject:  {subject}\n"
        f"Teacher:  {teacher}\n"
        f"Room:     {room}\n"
        f"Slot:     {slot['label']}\n"
        f"Time:     {slot_time}\n"
        f"Day:      {day_name}, {date_str}\n"
        + ("(Continuation of same class)\n" if is_continuing else "")
    )

    cont_tag = " (cont.)" if is_continuing else ""
    email_subject = f"[NUML] ⏰ {slot['label']}{cont_tag}: {subject} — {room}"
    send_email(email_subject, html, plain)

# ─────────────────────────────────────────────────────
#  EMAIL SENDER
# ─────────────────────────────────────────────────────

def send_email(subject: str, html: str, plain: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"NUML Reminder <{CFG['SMTP_USER']}>"
        msg["To"]      = CFG["NOTIFY_EMAIL"]
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html,  "html",  "utf-8"))
        with smtplib.SMTP(CFG["SMTP_HOST"], CFG["SMTP_PORT"], timeout=30) as s:
            s.ehlo(); s.starttls()
            s.login(CFG["SMTP_USER"], CFG["SMTP_PASSWORD"])
            s.sendmail(CFG["SMTP_USER"], CFG["NOTIFY_EMAIL"], msg.as_string())
        log.info(f"Reminder sent: {subject}")
        return True
    except Exception as e:
        log.error(f"Email failed: {e}")
        return False

# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────

def run():
    now     = datetime.now(PKT)
    weekday = now.weekday()
    hour    = now.hour
    minute  = now.minute

    log.info("=" * 52)
    log.info(f"Class reminder — {now.strftime('%A %d %b %Y %H:%M')} PKT")

    if weekday > 4:
        log.info("Weekend — no classes.")
        return

    day_name = DAY_NAMES[weekday]
    classes  = TIMETABLE.get(weekday, [])
    current  = hour * 60 + minute
    reminded = 0

    for slot_nums, subject, teacher, room in classes:
        for i, slot_num in enumerate(slot_nums):
            rh, rm = REMINDER_TIMES[slot_num]
            reminder = rh * 60 + rm

            # Fire if within 5-minute window
            if reminder <= current < reminder + 5:
                is_continuing = (i > 0)  # Not the first slot of this course
                log.info(f"✅ REMINDER: {subject} — Slot {slot_num} ({'continuing' if is_continuing else 'starting'})")
                build_and_send(slot_num, subject, teacher, room, is_continuing, day_name, now)
                reminded += 1
            else:
                diff = reminder - current
                status = f"in {diff} mins" if diff > 0 else "passed"
                log.info(f"  Slot {slot_num} ({subject}): reminder {status}")

    if reminded == 0:
        log.info("No reminders to send right now.")
    log.info("=" * 52)

if __name__ == "__main__":
    run()

