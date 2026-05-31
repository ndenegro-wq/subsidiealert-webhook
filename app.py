import os, smtplib, threading, json, urllib.request, urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, request, jsonify

app = Flask(__name__)

SMTP_USER = os.environ.get("SMTP_USER", "subsidiescan.alerts@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "febgoqotranvirxj")
NOTIF_EMAIL = os.environ.get("NOTIF_EMAIL", "subsidiescan.alerts@gmail.com")

# Logs bijhouden in geheugen (zichtbaar in Render logs)
aanmeldingen_log = []

def stuur_mail(aan, onderwerp, tekst):
    """Probeer meerdere SMTP poorten"""
    for poort, ssl in [(465, True), (587, False), (2525, False)]:
        try:
            if ssl:
                with smtplib.SMTP_SSL("smtp.gmail.com", poort, timeout=10) as s:
                    s.login(SMTP_USER, SMTP_PASS)
                    msg = MIMEText(tekst, "plain", "utf-8")
                    msg["Subject"] = onderwerp
                    msg["From"] = SMTP_USER
                    msg["To"] = aan
                    s.sendmail(SMTP_USER, aan, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", poort, timeout=10) as s:
                    s.starttls()
                    s.login(SMTP_USER, SMTP_PASS)
                    msg = MIMEText(tekst, "plain", "utf-8")
                    msg["Subject"] = onderwerp
                    msg["From"] = SMTP_USER
                    msg["To"] = aan
                    s.sendmail(SMTP_USER, aan, msg.as_string())
            print(f"Mail OK via poort {poort} naar {aan}")
            return True
        except Exception as e:
            print(f"Poort {poort} mislukt: {e}")
    print(f"Alle SMTP poorten mislukt voor {aan}")
    return False

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

@app.route("/", methods=["GET"])
def home():
    return f"SubsidieAlert Webhook API actief | {len(aanmeldingen_log)} aanmeldingen ontvangen"

@app.route("/log", methods=["GET"])
def log():
    return jsonify(aanmeldingen_log[-20:])

@app.route("/aanmelding", methods=["GET", "POST", "OPTIONS"])
def aanmelding():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    if request.method == "GET":
        return jsonify({"ok": True, "info": "POST hier een aanmelding"})

    data = request.get_json(silent=True) or {}
    naam   = data.get("naam", "").strip()
    email  = data.get("email", "").strip()
    pakket = data.get("pakket", "basis").strip()

    if not naam or not email or "@" not in email:
        return jsonify({"ok": False, "fout": "Naam of email ontbreekt"}), 400

    datum = datetime.now().strftime("%d-%m-%Y %H:%M")
    print(f"AANMELDING: {naam} | {email} | {pakket} | {datum}")

    # Opslaan in geheugen log
    aanmeldingen_log.append({"naam": naam, "email": email, "pakket": pakket, "datum": datum})

    # Mails in achtergrond
    def verstuur():
        stuur_mail(
            NOTIF_EMAIL,
            f"Nieuwe aanmelding SubsidieAlert: {naam}",
            f"Naam:   {naam}\nEmail:  {email}\nPakket: {pakket}\nDatum:  {datum}"
        )
        stuur_mail(
            email,
            f"Welkom bij SubsidieAlert, {naam.split()[0]}!",
            f"Hallo {naam},\n\nWelkom bij SubsidieAlert! Je gratis proefperiode van 14 dagen is gestart.\n\nElke ochtend voor 08:00 ontvang je nieuwe subsidies en aanbestedingen.\n\nPakket: {pakket.upper()}\n\nGroet,\nNick\nSubsidieAlert\nwww.subsidiealert.nl"
        )

    threading.Thread(target=verstuur, daemon=True).start()
    return jsonify({"ok": True, "bericht": "Aanmelding ontvangen"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
