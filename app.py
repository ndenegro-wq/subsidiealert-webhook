import os, json, smtplib
from datetime import datetime
from flask import Flask, request, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

SMTP_USER  = "subsidiescan.alerts@gmail.com"
SMTP_PASS  = "febgoqotranvirxj"
NICK_EMAIL = "nickdenegro@icloud.com"

# ── Mail versturen ────────────────────────────────────────────────
def stuur_mail(aan, onderwerp, html, tekst):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = onderwerp
        msg["From"]    = f"SubsidieAlert <{SMTP_USER}>"
        msg["To"]      = aan
        msg.attach(MIMEText(tekst, "plain", "utf-8"))
        msg.attach(MIMEText(html,  "html",  "utf-8"))
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, aan, msg.as_string())
        print(f"  Mail verstuurd naar {aan}")
        return True
    except Exception as e:
        print(f"  Mail fout: {e}")
        return False

def stuur_bevestiging(naam, email, pakket, telefoon):
    voornaam = naam.strip().split()[0] if naam.strip() else "daar"
    prijs_map = {"basis": "€19/maand", "pro": "€29/maand", "volledig": "€299 eenmalig",
                 "starter": "€19/maand", "professional": "€29/maand"}
    prijs = prijs_map.get(pakket.lower(), pakket)

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#1a3a6e;padding:28px;text-align:center;">
        <h1 style="color:#fff;margin:0;font-size:22px;">SubsidieAlert</h1>
        <p style="color:#a0c4ff;margin:6px 0 0;font-size:14px;">Dagelijkse subsidie-alerts voor MKB Nederland</p>
      </div>
      <div style="padding:32px;background:#fff;">
        <h2 style="color:#1a3a6e;margin-top:0;">Bedankt voor je aanmelding, {voornaam}!</h2>
        <p style="color:#444;line-height:1.7;">
          Geweldig dat je erbij bent! Om jouw persoonlijke subsidie-alerts zo goed mogelijk af te stemmen,
          hebben we nog een paar gegevens van je nodig. <strong>Beantwoord deze mail</strong> met de onderstaande informatie:
        </p>
        <div style="background:#f0f7ff;border-left:4px solid #1a3a6e;padding:16px;margin:20px 0;border-radius:4px;">
          <strong style="color:#1a3a6e;">Vul dit in en stuur terug:</strong><br><br>
          1. <strong>Bedrijfsnaam:</strong> ...<br>
          2. <strong>Sector / branche:</strong> (bijv. bouw, zorg, tech, horeca) ...<br>
          3. <strong>Postcode:</strong> ...<br>
          4. <strong>Aantal medewerkers:</strong> ...<br>
          5. <strong>Waar ben je naar op zoek?</strong> (bijv. innovatie, verduurzaming, groei) ...
        </div>
        <p style="color:#444;line-height:1.7;">
          Zodra we dit ontvangen, stellen we jouw profiel in en ontvang je elke ochtend voor 08:00
          een persoonlijk overzicht van subsidies en aanbestedingen die bij jouw bedrijf passen.
        </p>
        <div style="background:#f0f7ff;border-left:4px solid #1a3a6e;padding:16px;margin:20px 0;border-radius:4px;">
          <strong style="color:#1a3a6e;">Jouw aanmelding</strong><br><br>
          Pakket: <strong>{pakket.upper()}</strong> &mdash; {prijs}<br>
          Datum: {datetime.now().strftime('%d %B %Y om %H:%M')}
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
        <p style="color:#999;font-size:12px;margin:0;">
          SubsidieAlert &bull; <a href="https://www.subsidiealert.nl" style="color:#1a3a6e;">www.subsidiealert.nl</a>
        </p>
      </div>
    </div>"""

    tekst = f"""Hallo {voornaam},

Bedankt voor je aanmelding bij SubsidieAlert!

Om jouw alerts goed af te stemmen, hebben we nog wat gegevens nodig.
Beantwoord deze mail met het volgende:

1. Bedrijfsnaam: ...
2. Sector / branche: (bijv. bouw, zorg, tech, horeca) ...
3. Postcode: ...
4. Aantal medewerkers: ...
5. Waar ben je naar op zoek? (bijv. innovatie, verduurzaming, groei) ...

Zodra we dit ontvangen, stellen we jouw profiel in en ontvang je elke ochtend voor 08:00
een persoonlijk overzicht van subsidies die bij jouw bedrijf passen.

Pakket: {pakket.upper()} — {prijs}
Datum:  {datetime.now().strftime('%d-%m-%Y %H:%M')}

Met vriendelijke groet,
SubsidieAlert — www.subsidiealert.nl"""

    stuur_mail(email, f"Bevestiging aanmelding SubsidieAlert — {pakket.upper()}", html, tekst)

def stuur_notificatie(naam, email, pakket, telefoon, datum):
    prijs_map = {"basis": "€19/mnd", "pro": "€29/mnd", "volledig": "€299",
                 "starter": "€19/mnd", "professional": "€29/mnd"}
    prijs = prijs_map.get(pakket.lower(), pakket)

    html = f"""<div style="font-family:Arial,sans-serif;padding:20px;max-width:500px;">
    <h2 style="color:#1a3a6e;margin-top:0;">Nieuwe aanmelding!</h2>
    <table style="width:100%;border-collapse:collapse;">
      <tr><td style="padding:10px 8px;color:#666;width:110px;border-bottom:1px solid #eee;">Naam</td>
          <td style="padding:10px 8px;font-weight:bold;border-bottom:1px solid #eee;">{naam}</td></tr>
      <tr><td style="padding:10px 8px;color:#666;border-bottom:1px solid #eee;">Email</td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;"><a href="mailto:{email}">{email}</a></td></tr>
      <tr><td style="padding:10px 8px;color:#666;border-bottom:1px solid #eee;">Telefoon</td>
          <td style="padding:10px 8px;border-bottom:1px solid #eee;">{telefoon or 'niet opgegeven'}</td></tr>
      <tr><td style="padding:10px 8px;color:#666;border-bottom:1px solid #eee;">Pakket</td>
          <td style="padding:10px 8px;font-weight:bold;color:#1a3a6e;border-bottom:1px solid #eee;">{pakket.upper()} — {prijs}</td></tr>
      <tr><td style="padding:10px 8px;color:#666;">Datum</td>
          <td style="padding:10px 8px;">{datum}</td></tr>
    </table>
    </div>"""

    tekst = f"""NIEUWE AANMELDING SubsidieAlert

Naam:     {naam}
Email:    {email}
Telefoon: {telefoon or 'niet opgegeven'}
Pakket:   {pakket.upper()} — {prijs}
Datum:    {datum}"""

    stuur_mail(NICK_EMAIL, f"Nieuwe aanmelding: {naam} — {pakket.upper()} {prijs}", html, tekst)


# ── CORS ──────────────────────────────────────────────────────────
@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

# ── Routes ────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "SubsidieAlert Webhook API actief"

@app.route("/aanmelding", methods=["GET", "POST", "OPTIONS"])
def aanmelding():
    if request.method in ("OPTIONS", "GET"):
        return jsonify({"ok": True})

    data     = request.get_json(silent=True) or {}
    naam     = data.get("naam",     "").strip()
    email    = data.get("email",    "").strip()
    pakket   = data.get("pakket",   "basis").strip()
    telefoon = data.get("telefoon", "").strip()

    if not naam or not email or "@" not in email:
        return jsonify({"ok": False, "fout": "Naam of email ontbreekt"}), 400

    datum = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(f"AANMELDING: {naam} | {email} | {pakket} | {datum}")

    # Direct mails sturen — aanmelding gaat nooit verloren
    stuur_bevestiging(naam, email, pakket, telefoon)
    stuur_notificatie(naam, email, pakket, telefoon, datum)

    return jsonify({"ok": True, "bericht": "Aanmelding ontvangen, bevestiging verstuurd"})


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "online", "tijd": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
