"""
Local test server to receive AxDraft webhooks via ngrok.

Usage:
    1. Run this server:    python3 webhook_test.py
    2. In another terminal: ngrok http 5555
    3. Copy the ngrok public URL and paste it into AxDraft webhook preferences
       (e.g. https://xxxx.ngrok-free.app/webhooks/axdraft)
"""

import json
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

LOG_FILE = "webhook_log.json"


@app.route("/webhooks/axdraft", methods=["POST"])
def axdraft_webhook():
    """Receive and log AxDraft after-draft webhook payloads."""
    payload = request.get_json(silent=True) or {}
    headers = dict(request.headers)

    entry = {
        "received_at": datetime.now().isoformat(),
        "method": request.method,
        "content_type": request.content_type,
        "headers": headers,
        "payload": payload,
        "raw_data": request.get_data(as_text=True),
    }

    # Log to console
    print("\n" + "=" * 60)
    print(f"WEBHOOK RECEIVED at {entry['received_at']}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    if not payload:
        print(f"Raw body: {entry['raw_data']}")
    print("=" * 60 + "\n")

    # Append to log file
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    return {"status": "ok", "message": "Webhook received"}, 200


@app.route("/webhooks/axdraft", methods=["GET"])
def axdraft_health():
    """Health check — verify the endpoint is reachable."""
    return {"status": "ok", "endpoint": "/webhooks/axdraft"}, 200


if __name__ == "__main__":
    print("Starting AxDraft webhook test server on port 5555...")
    print("Endpoint: http://localhost:5555/webhooks/axdraft")
    print("\nNext step: run 'ngrok http 5555' in another terminal")
    print("Then paste the ngrok URL + /webhooks/axdraft into AxDraft webhook preferences\n")
    app.run(host="0.0.0.0", port=5555, debug=True)
