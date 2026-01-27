import requests
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
SMTP_PASSWORD = "yimn jlao kzli bctp"

WEATHER_SCORE_THRESHOLD = 450
NWS_API_URL = "https://api.weather.gov/alerts/active?area="

STATE_POPULATION = {
    "Oregon": 4200000,
    "Washington": 7700000,
}

SEVERITY_WEIGHT = {
    "Extreme": 5,
    "Severe": 4,
    "Moderate": 3,
    "Minor": 2,
    "Unknown": 1,
}

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

def format_alert_email(event_name, state, alert_time, score=None, extra=""):
    text = (
        f"⚠ {event_name} Alert!\n\n"
        f"Location: {state}\n"
        f"Time: {alert_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
    )
    if score is not None:
        text += f"Weather Score: {score}/500\n"
    if extra:
        text += f"{extra}\n"
    return text

# ---------------- FETCH NWS ALERTS ----------------
def fetch_nws_alerts(state):
    try:
        res = requests.get(f"{NWS_API_URL}{state}", timeout=10)
        res.raise_for_status()
        data = res.json()
        alerts = []

        for feature in data.get("features", []):
            props = feature.get("properties", {})
            alert = {
                "event": props.get("event"),
                "severity": props.get("severity", "Unknown"),
                "sent": datetime.fromisoformat(props.get("sent").replace("Z", "+00:00")),
                "state": state
            }
            alerts.append(alert)
        return alerts
    except Exception as e:
        print(f"Error fetching NWS alerts for {state}: {e}")
        return []

# ---------------- CALCULATE WEATHER SCORE ----------------
def calculate_weather_score(alerts):
    now = datetime.now(ZoneInfo("America/Chicago"))

    # Fixed full score window: 10:00–10:03 AM on 1/27/2026
    fixed_start = datetime(2026, 1, 27, 10, 0, 0, tzinfo=ZoneInfo("America/Chicago"))
    fixed_end   = datetime(2026, 1, 27, 10, 3, 0, tzinfo=ZoneInfo("America/Chicago"))

    if fixed_start <= now <= fixed_end:
        return 500  # max score during the special window

    # Otherwise calculate dynamically
    total_score = 0
    for alert in alerts:
        severity = alert["severity"]
        weight = SEVERITY_WEIGHT.get(severity, 1)
        state_pop = STATE_POPULATION.get(alert["state"], 1000000)
        pop_factor = min(state_pop / 1000000, 10)

        age_minutes = (now - alert["sent"]).total_seconds() / 60
        decay = max(0, 60 - age_minutes) / 60

        alert_score = weight * pop_factor * decay
        total_score += alert_score

    return min(int(total_score * 10), 500)

# ---------------- MAIN ----------------
def main():
    now_cst = datetime.now(ZoneInfo("America/Chicago"))

    # ---------- CUSTOM ALERTS ----------
    # Hurricane Watch: 6:51 PM today
    today_watch = now_cst.replace(hour=18, minute=51, second=0, microsecond=0)
    if now_cst.date() == today_watch.date() and now_cst.hour == 18 and now_cst.minute == 51:
        send_email(
            "⚠ Hurricane Watch for Oregon & Washington",
            format_alert_email("Hurricane Watch", "Oregon & Washington", now_cst)
        )

    # Hurricane Warning: 10:05 AM on 1/27/2026
    warning_time = datetime(2026, 1, 27, 10, 5, 0, tzinfo=ZoneInfo("America/Chicago"))
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 27:
        if now_cst.hour == 10 and now_cst.minute == 5:
            send_email(
                "⚠ Hurricane Warning for Oregon & Washington",
                format_alert_email("Hurricane Warning", "Oregon & Washington", now_cst)
            )

    # ---------- DYNAMIC NWS ALERTS ----------
    all_alerts = []
    for state in ["Oregon", "Washington"]:
        all_alerts.extend(fetch_nws_alerts(state))

    weather_score = calculate_weather_score(all_alerts)
    print(f"Weather Score: {weather_score}/500")

    # High intensity email
    if weather_score >= WEATHER_SCORE_THRESHOLD:
        send_email(
            f"⚠ High Weather Intensity (Score {weather_score})",
            format_alert_email("Multiple NWS Alerts", "Oregon & Washington", now_cst, weather_score)
        )

    # Extreme Wind Warning at 12:30 PM on 1/27/2026
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 27:
        if now_cst.hour == 12 and now_cst.minute == 30:
            for alert in all_alerts:
                if alert["event"] == "Extreme Wind" and alert["state"] in ["Oregon", "Washington"]:
                    send_email(
                        f"⚠ Extreme Wind Warning ({alert['state']})",
                        format_alert_email(alert["event"], alert["state"], now_cst, weather_score)
                    )

if __name__ == "__main__":
    main()
