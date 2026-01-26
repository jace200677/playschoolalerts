import requests
from bs4 import BeautifulSoup
from datetime import datetime
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
    cutoff = datetime(2026, 5, 28)
    if now.date() > cutoff:
        return False

    weekday = now.weekday()  # Monday=0, Sunday=6
    current_time = now.time()

    if weekday < 5:  # Mon–Fri
        start = datetime.strptime("20:00","%H:%M").time()
        end = datetime.strptime("06:00","%H:%M").time()
    else:  # Weekend
        start = datetime.strptime("20:00","%H:%M").time()
        end = datetime.strptime("08:00","%H:%M").time()

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

def format_email_body(score, now_cst):
    return (
        f"⚠ High Weather Intensity Alert!\n\n"
        f"Weather Score: {score}/500\n"
        f"Time: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}\n"
        f"Source: {WEBSITE_URL}"
    )

# ---------------- FETCH WEATHER SCORE ----------------
def fetch_weather_score():
    try:
        res = requests.get(WEBSITE_URL, timeout=10)
        html = res.text

        # Example: assume the page contains <span id="weather-score">123</span>
        from bs4 import BeautifulSoup
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
    score = fetch_weather_score()
    if score is None:
        print("No weather score found")
        return

    print(f"Weather Score: {score}/500")

    quiet = is_quiet_hours(now_cst)

    if score >= WEATHER_SCORE_THRESHOLD:
        body = format_email_body(score, now_cst)
        send_email(f"⚠ High Weather Intensity (Score {score})", body)
        return

    if quiet:
        print("Quiet hours active, skipping alert")
        return

if __name__ == "__main__":
    main()
