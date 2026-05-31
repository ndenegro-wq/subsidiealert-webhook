"""
SubsidieAlert Webhook API
Ontvangt aanmeldingen van de website en stuurt een notificatiemail
"""

import os, json, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, request, jsonify

app = Flask(__name__)

SMTP_USER = os.environ.get("SMTP_USER", "subsidiescan.alerts@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "febgoqotranvirxj")
NOTIF_EMAIL = os.environ.get("NOTIF_EMAIL", "subsidiescan.alerts@gmail.com")

def stuur_notificatie(naam, email, pakket):
    try:
        tekst = f"""Nieuwe aanmelding op SubsidieAlert!

Naam:   {naam}
Email:  {email}
Pakket: {pakket}
Datum:  {datetime.now().strftime('%d-%m-%Y %H:%M')}

Voeg deze persoon toe aan abonnees.json als dat nog niet automatisch is gebeurd.
"""
        msg = MIMEText(tekst, "plain", "utf-8")
        msg["Subject"] = f"Nieuwe aanmelding SubsidieAlert: {naam}"
        msg["From"] = SMTP_USER
        msg["To"] = NOTIF_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, NOTIF_EMAIL, msg.as_string())
        print(f"Notificatie verstuurd: {naam} <{email}>")
    except Exception as e:
        print(f"Notificatie mislukt: {e}")

def stuur_welkomstmail(naam, email, pakket):
    try:
        tekst = f"""Hallo {naam},

Welkom bij SubsidieAlert! Je gratis proefperiode van 14 dagen is gestart.

Elke ochtend voor 08:00 ontvang je een overzicht van nieuwe subsidies en aanbestedingen in de duurzaamheidssector.

Pakket: {pakket.upper()}
- Basis: RVO subsidies + TenderNed aanbestedingen
- Pro: alle bronnen + gemeenten + sectorfilter

Vragen? Stuur een reply op deze mail.

Groet,
Nick
SubsidieAlert
www.subsidiealert.nl
"""
        msg = MIMEText(tekst, "plain", "utf-8")
        msg["Subject"] = f"Welkom bij SubsidieAlert, {naam.split()[0]}!"
        msg["From"] = SMTP_USER
        msg["To"] = email
        msg["Reply-To"] = NOTIF_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, email, msg.as_string())
        print(f"Welkomstmail verstuurd naar {email}")
    except Exception as e:
        print(f"Welkomstmail mislukt: {e}")

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

@app.route("/aanmelding", methods=["POST", "OPTIONS"])
def aanmelding():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    naam  = data.get("naam", "").strip()
    email = data.get("email", "").strip()
    pakket = data.get("pakket", "basis").strip()

    if not naam or not email or "@" not in email:
        return jsonify({"ok": False, "fout": "Naam of email ontbreekt"}), 400

    print(f"AANMELDING: {naam} | {email} | {pakket}")

    stuur_notificatie(naam, email, pakket)
    stuur_welkomstmail(naam, email, pakket)

    return jsonify({"ok": True, "bericht": "Aanmelding ontvangen"})

@app.route("/", methods=["GET"])
def home():
    return "SubsidieAlert Webhook API — actief"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5055)))
