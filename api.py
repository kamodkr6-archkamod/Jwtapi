import time
import requests
from flask import Flask, request, jsonify
from danger_ffjwt import guest_to_jwt

app = Flask(__name__)

DEV_CREDIT = "@kamod90"
DEV_TELEGRAM = "t.me/KAMOD_CODEX"

# -------- Version Cache --------
_versions_cache = {
    "ob_version": "OB52",
    "client_version": "1.120.1",
    "last_fetch": 0
}

def get_versions():
    global _versions_cache
    now = time.time()
    if now - _versions_cache["last_fetch"] > 3600:
        try:
            resp = requests.get(
                "https://raw.githubusercontent.com/dangerapix/danger-ffjwt/main/versions.json",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                _versions_cache["ob_version"] = data.get("ob_version", "OB52")
                _versions_cache["client_version"] = data.get("client_version", "1.120.1")
                _versions_cache["last_fetch"] = now
        except:
            pass
    return _versions_cache["ob_version"], _versions_cache["client_version"]

def add_dev_headers(response):
    response.headers["X-Developer"] = DEV_CREDIT
    return response

@app.route("/")
def home():
    return "JW API Running Successfully 🔥"

@app.route("/token", methods=["GET"])
def token_converter():
    ob_ver, client_ver = get_versions()

    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return add_dev_headers(jsonify({
            "success": False,
            "error": "Use ?uid=UID&password=PASSWORD",
            "credit": DEV_TELEGRAM
        })), 400

    try:
        result = guest_to_jwt(uid.strip(), password.strip(),
                              ob_version=ob_ver,
                              client_version=client_ver)

        if isinstance(result, dict):
            result["credit"] = DEV_TELEGRAM
        else:
            result = {
                "success": True,
                "token": result,
                "credit": DEV_TELEGRAM
            }

        return add_dev_headers(jsonify(result))

    except Exception as e:
        return add_dev_headers(jsonify({
            "success": False,
            "error": str(e),
            "credit": DEV_TELEGRAM
        })), 500