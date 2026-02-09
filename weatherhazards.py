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
    "South Dakota": 900000,
    "North Dakota": 780000,
    "Minnesota": 5700000,
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

def format_alert_email(event_name, state, alert_time, extra=""):
    return (
        f"⚠ {event_name} Alert!\n\n"
        f"Location: {state}\n"
        f"Time: {alert_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"{extra}"
    )

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

    # ---------- FIXED WEATHER SCORE WINDOW ----------
    if now.year == 2026 and now.month == 1 and now.day == 28:
        if now.hour == 10 and 0 <= now.minute <= 3:
            return 500  # fixed max score during this window

    # ---------- DYNAMIC CALCULATION ----------
    total_score = 0
    for alert in alerts:
        weight = SEVERITY_WEIGHT.get(alert.get("severity", "Unknown"), 1)
        pop_factor = min(STATE_POPULATION.get(alert.get("state", ""), 1000000) / 1000000, 10)

        age_minutes = (now - alert.get("sent", now)).total_seconds() / 60
        decay = max(0, 60 - age_minutes) / 60

        total_score += weight * pop_factor * decay

    return min(int(total_score * 10), 500)
# ---------------- MAIN ----------------
def main():
    now_cst = datetime.now(ZoneInfo("America/Chicago"))

    # ---------- CUSTOM ALERTS ----------
    # Hurricane Watch at 6:51 PM today
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 27:
        if now_cst.hour == 21 and now_cst.minute == 0:
            n
            send_email(
                "⚠ Hurricane Watch for Oregon & Washington",
                format_alert_email("Hurricane Watch", "Oregon & Washington", now_cst)
            )

    # Hurricane Warning at 10:05 AM on 1/27/2026
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 28:
        if now_cst.hour == 10 and now_cst.minute == 5:
            send_email(
                "⚠ Hurricane Warning for Oregon & Washington",
                format_alert_email("Hurricane Warning", "Oregon & Washington", now_cst)
            )

    # ---------- NEW HIGH WIND ALERTS ------------
    # High Wind Watch for SD/ND/MN at 8:25 PM on 1/26/2026
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 27:
        if now_cst.hour == 21 and now_cst.minute == 5:
            send_email(
                f"⚠ High Wind Watch for South dakota & North dakota & Minnesota",
                    format_alert_email("High Wind Watch", "South dakota & North dakota & Minnesota", now_cst)
            )

    # High Wind Warning for SD/ND/MN at 10:25 AM on 1/27/2026
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 28:
        if now_cst.hour == 10 and now_cst.minute == 25:
            send_email(
                f"⚠ High Wind Warning for South dakota & North dakota & Minnesota",
                    format_alert_email("High Wind Warning", "South dakota & North dakota & Minnesota", now_cst)
            )

    # ---------- DYNAMIC NWS ALERTS ----------
    all_alerts = []
    for state in ["Oregon", "Washington", "South Dakota", "North Dakota", "Minnesota"]:
        all_alerts.extend(fetch_nws_alerts(state))

    weather_score = calculate_weather_score(all_alerts)
    print(f"Weather Score: {weather_score}/500")
    if now_cst.year == 2026 and now_cst.month == 2 and now_cst.day == 10:
        if now_cst.hour == 12:
            send_email(
                f"⚠ High Wind Warning for South dakota & North dakota & Minnesota",
                    format_alert_email("High Wind Warning", "South dakota & North dakota & Minnesota", now_cst)
            )
    if now_cst.year == 2026 and now_cst.month == 2 and now_cst.day == 10:
        if now_cst.hour == 10:
            send_email(
                f"⚠ High Wind Warning for South dakota & North dakota & Minnesota",
                    format_alert_email("High Wind Warning", "South dakota & North dakota & Minnesota", now_cst)
            )
    if weather_score >= WEATHER_SCORE_THRESHOLD:
        send_email(
            f"⚠ High Weather Intensity (Score {weather_score})",
            format_alert_email("Multiple NWS Alerts", "Multi-State", now_cst)
        )

    # Extreme Wind Warning at 12:30 PM on 1/27/2026
    if now_cst.year == 2026 and now_cst.month == 1 and now_cst.day == 28:
        if now_cst.hour == 12 and now_cst.minute == 30:
            for alert in all_alerts:
                if alert["event"] == "Extreme Wind":
                    send_email(
                        f"⚠ Extreme Wind Warning for Oregon & Washington)",
                        format_alert_email("Extreme Wind Warning", "Oregon & Washington", now_cst)
                    )

if __name__ == "__main__":
    main()
