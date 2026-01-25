import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

# ---------------- CONFIG ----------------
EMAIL_FROM = "jacefink2@gmail.com"
EMAIL_TO = "jacebfink@icloud.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "jacefink2@gmail.com"
SMTP_PASSWORD = "yimn jlao kzli bctp"  # Gmail App Password

# Weather score threshold
WEATHER_SCORE_THRESHOLD = 450  # instant email

# Thresholds for scoring
TEMP_EXTREME_HIGH = 90
TEMP_EXTREME_LOW = 32
TEMP_MODERATE_HIGH = 80
TEMP_MODERATE_LOW = 40

WIND_STRONG = 25
WIND_MODERATE = 15
PRECIP_ALERT = 0.1  # inches/hour
HUMIDITY_HIGH = 90
HUMIDITY_LOW = 20

# ---------------- QUIET HOURS ----------------
def is_quiet_hours(now):
    cutoff = date(2026, 5, 28)
    if now.date() > cutoff:
        return False

    weekday = now.weekday()  # Monday=0, Sunday=6
    current_time = now.time()

    # Weekday quiet hours: 8pm–6am, Weekend: 8pm–8am
    if weekday < 5:  # Mon–Fri
        start = time(20, 0)
        end = time(6, 0)
    else:  # Sat–Sun
        start = time(20, 0)
        end = time(8, 0)

    if start < end:
        return start <= current_time < end
    else:
        return current_time >= start or current_time < end

# ---------------- NWS DATA ----------------
def get_nws_observation(lat, lon):
    try:
        stations_url = f"https://api.weather.gov/points/{lat},{lon}/stations"
        stations_resp = requests.get(stations_url).json()
        if not stations_resp.get("features"):
            print("No NWS stations found")
            return None
        station_id = stations_resp["features"][0]["properties"]["stationIdentifier"]

        obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        obs_resp = requests.get(obs_url).json()
        props = obs_resp["properties"]

        temp = props["temperature"]["value"] * 9/5 + 32 if props["temperature"]["value"] is not None else None
        wind_speed = props["windSpeed"]["value"] * 2.23694 if props["windSpeed"]["value"] is not None else 0
        humidity = props["relativeHumidity"]["value"] if props.get("relativeHumidity") else 50
        precip = props["precipitationLastHour"]["value"] if props.get("precipitationLastHour") else 0
        precip_in = precip * 0.0393701  # mm → in

        return temp, wind_speed, humidity, precip_in
    except Exception as e:
        print(f"Error fetching NWS data: {e}")
        return None

# ---------------- WEATHER SCORE ----------------
def calculate_weather_score(temp, wind_speed, humidity, precip_in):
    score = 0
    if temp is not None:
        if temp >= TEMP_EXTREME_HIGH or temp <= TEMP_EXTREME_LOW:
            score += 150
        elif temp >= TEMP_MODERATE_HIGH or temp <= TEMP_MODERATE_LOW:
            score += 75
    if wind_speed >= WIND_STRONG:
        score += 125
    elif wind_speed >= WIND_MODERATE:
        score += 75
    if precip_in > PRECIP_ALERT:
        score += 100
    if humidity >= HUMIDITY_HIGH or humidity <= HUMIDITY_LOW:
        score += 50
    return min(score, 500)

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

def format_email_body(score, temp, wind_speed, humidity, precip_in, lat, lon):
    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    return (
        f"⚠ High Weather Intensity Alert!\n\n"
        f"Weather Score: {score}/500\n"
        f"Temperature: {temp} °F\n"
        f"Wind Speed: {wind_speed} mph\n"
        f"Humidity: {humidity} %\n"
        f"Precipitation: {precip_in} in/hr\n"
        f"Location: {lat},{lon}\n"
        f"Time: {now_cst.strftime('%Y-%m-%d %H:%M:%S CST')}\n"
    )

# ---------------- MAIN ----------------
def main():
    lat, lon = 44.9778, -93.2650  # Example: Minneapolis, MN
    obs = get_nws_observation(lat, lon)
    if not obs:
        print("No observation data")
        return

    temp, wind_speed, humidity, precip_in = obs
    score = calculate_weather_score(temp, wind_speed, humidity, precip_in)
    print(f"Weather Score: {score}/500 | Temp={temp}°F Wind={wind_speed} mph Precip={precip_in} in")

    now_cst = datetime.now(ZoneInfo("America/Chicago"))
    quiet = is_quiet_hours(now_cst)

    # Send email instantly if score >= 450 (ignore quiet hours)
    if score >= WEATHER_SCORE_THRESHOLD:
        body = format_email_body(score, temp, wind_speed, humidity, precip_in, lat, lon)
        send_email(f"⚠ High Weather Intensity (Score {score})", body)
        return

    # Otherwise, respect quiet hours
    if quiet:
        print("Quiet hours active, skipping alert")
        return

    # Optional: Normal alert logic here if you want
    if score > 200:
        body = format_email_body(score, temp, wind_speed, humidity, precip_in, lat, lon)
        send_email(f"Weather Intensity Moderate (Score {score})", body)

if __name__ == "__main__":
    main()
