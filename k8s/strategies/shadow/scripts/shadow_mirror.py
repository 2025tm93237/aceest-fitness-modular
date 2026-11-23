"""
Minimal shadow-traffic mirror.
Listens for requests meant for the primary service, forwards a copy to the
shadow service in the background, and returns only the primary's response
to the real caller. Run with: python3 shadow_mirror.py
"""
import threading
import requests
from flask import Flask, request, Response

PRIMARY_URL = "http://localhost:30080"          # the real, user-facing service
SHADOW_URL  = "http://aceest-shadow:5000"       # only reachable from inside the cluster
MIRROR_PORT = 8090

app = Flask(__name__)

def mirror_to_shadow(path, method, data):
    try:
        requests.request(method, f"{SHADOW_URL}/{path}", data=data, timeout=2)
    except requests.exceptions.RequestException as exc:
        print(f"[shadow] mirrored call failed (expected to be harmless): {exc}")

@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    threading.Thread(
        target=mirror_to_shadow, args=(path, request.method, request.data)
    ).start()
    primary_resp = requests.request(
        request.method, f"{PRIMARY_URL}/{path}", data=request.data, timeout=5
    )
    return Response(primary_resp.content, status=primary_resp.status_code)

if __name__ == "__main__":
    app.run(port=MIRROR_PORT)
