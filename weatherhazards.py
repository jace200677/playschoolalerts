import requests
import re
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
        match = re.search(r'id="score">(\d+)<', html)
        if match:
            return int(match.group(1))
        else:
            print("Could not find #score in page")
            return None
    except Exception as e:
        print(f"Error fetching website: {e}")
        return None

# ---------------- MAIN ----------------
def main():
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    sent_alerts = set()

    # ---------- CUSTOM ALERTS ----------
    # 1️⃣ Hurricane Watch at 6:51 PM today
    today_watch = now_cst.replace(hour=18, minute=51, second=0, microsecond=0)
    if now_cst.year == today_watch.year and now_cst.month == today_watch.month and now_cst.day == today_watch.day:
        if now_cst.hour == 18 and now_cst.minute == 51:
            send_email(
                f"⚠ Hurricane Watch for Oregon & Washington",
                format_custom_alert_email("Hurricane Watch", "Oregon & Washington", now_cst)
            )

    # 2️⃣ Hurricane Warning at 10:05 AM on 1/27/2026
    warning_time = datetime(2026, 1, 27, 10, 5, 0, tzinfo=ZoneInfo("America/Chicago"))
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 27:
        if now_cst.hour == 10 and now_cst.minute == 5:
            send_email(
                f"⚠ Hurricane Warning for Oregon & Washington",
                format_custom_alert_email("Hurricane Warning", "Oregon & Washington", now_cst)
            )

    # ---------- REGULAR WEATHER SCORE ALERT ----------
    score = fetch_weather_score()
    if score is not None:
        print(f"Weather Score: {score}/500")
        if score >= WEATHER_SCORE_THRESHOLD:
            send_email(
                f"⚠ High Weather Intensity (Score {score})",
                f"Weather Score: {score}/500\nTime: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}\nSource: {WEBSITE_URL}"
            )

if __name__ == "__main__":
    main()
