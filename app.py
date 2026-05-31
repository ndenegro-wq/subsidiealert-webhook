import os, threading, json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Aanmeldingen in geheugen + persistentie via bestand op Render disk
aanmeldingen = []
verwerkt = set()

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

@app.route("/", methods=["GET"])
def home():
    return f"SubsidieAlert Webhook API actief | {len(aanmeldingen)} aanmeldingen"

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
    item = {"naam": naam, "email": email, "pakket": pakket, "datum": datum, "verwerkt": False}
    aanmeldingen.append(item)
    print(f"AANMELDING: {naam} | {email} | {pakket} | {datum}")

    return jsonify({"ok": True, "bericht": "Aanmelding ontvangen"})

@app.route("/pending", methods=["GET"])
def pending():
    """Geeft onverwerkte aanmeldingen terug — Nick's lokale script polt dit"""
    onverwerkt = [a for a in aanmeldingen if not a["verwerkt"]]
    return jsonify(onverwerkt)

@app.route("/bevestig", methods=["POST"])
def bevestig():
    """Markeer aanmeldingen als verwerkt na email vanuit lokaal script"""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    for a in aanmeldingen:
        if a["email"].lower() == email:
            a["verwerkt"] = True
    return jsonify({"ok": True})

@app.route("/log", methods=["GET"])
def log():
    return jsonify(aanmeldingen[-50:])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
