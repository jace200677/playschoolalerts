import requests
from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- CONFIG ----------------
EMAIL_FROM = "jacefink2@gmail.com"
EMAIL_TO = "jacebfink@icloud.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "jacefink2@gmail.com"
SMTP_PASSWORD = "yimn jlao kzli bctp"  # Gmail App Password

WEATHER_SCORE_THRESHOLD = 450
WEBSITE_URL = "https://jace200677.github.io/weather-map-playschool/mywebsite.html"

# ---------------- QUIET HOURS ----------------
def is_quiet_hours(now):
    weekday = now.weekday()  # Monday=0, Sunday=6
    current_time = now.time()

    if weekday < 5:  # Mon–Fri
        start = time(20, 0)
        end = time(6, 0)
    else:  # Weekend
        start = time(20, 0)
        end = time(8, 0)

    if start < end:
        return start <= current_time < end
    else:
        return current_time >= start or current_time < end

# ---------------- EMAIL ----------------
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")

def format_custom_alert_email(event_name, state, alert_time):
    return (
        f"⚠ {event_name} Alert!\n\n"
        f"Location: {state}\n"
        f"Time: {alert_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"Source: {WEBSITE_URL}"
    )

# ---------------- FETCH WEATHER SCORE ----------------
def fetch_weather_score():
    try:
        res = requests.get(WEBSITE_URL, timeout=10)
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        score_span = soup.find(id="weather-score")
        if score_span:
            score = int(score_span.text.strip())
            return score
        else:
            print("Could not find #weather-score on page")
            return None
    except Exception as e:
        print(f"Error fetching website: {e}")
        return None

# ---------------- MAIN ----------------
def main():
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    quiet = is_quiet_hours(now_cst)

    # Track alerts sent in this run (in-memory only)
    sent_alerts = set()

    # ---------- CUSTOM ALERTS ----------
    # 1️⃣ Hurricane Watch at 6:20 PM today
    watch_time = now_cst.replace(hour=18, minute=20, second=0, microsecond=0)
    watch_key = f"hurricane_watch_{watch_time.date()}"
    if now_cst >= watch_time and watch_key not in sent_alerts:
        if not quiet:
            send_email(
                f"⚠ Hurricane Watch for Oregon & Washington",
                format_custom_alert_email("Hurricane Watch", "Oregon & Washington", now_cst)
            )
        sent_alerts.add(watch_key)

    # 2️⃣ Hurricane Warning at 10:05 AM tomorrow
    tomorrow = now_cst + timedelta(days=1)
    warning_time = tomorrow.replace(hour=10, minute=5, second=0, microsecond=0)
    warning_key = f"hurricane_warning_{warning_time.date()}"
    if now_cst >= warning_time and warning_key not in sent_alerts:
        if not quiet:
            send_email(
                f"⚠ Hurricane Warning for Oregon & Washington",
                format_custom_alert_email("Hurricane Warning", "Oregon & Washington", now_cst)
            )
        sent_alerts.add(warning_key)

    # ---------- REGULAR WEATHER SCORE ALERT ----------
    score = fetch_weather_score()
    if score is None:
        print("No weather score found")
        return

    print(f"Weather Score: {score}/500")
    if score >= WEATHER_SCORE_THRESHOLD and not quiet:
        send_email(
            f"⚠ High Weather Intensity (Score {score})",
            f"Weather Score: {score}/500\nTime: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}\nSource: {WEBSITE_URL}"
        )

if __name__ == "__main__":
    main()
