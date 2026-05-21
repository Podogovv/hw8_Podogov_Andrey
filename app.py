from flask import Flask, jsonify, request, Response
import os
import time
from prometheus_client import Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
MODEL_VERSION = os.getenv("MODEL_VERSION", APP_VERSION)
PORT = int(os.getenv("PORT", "8000"))

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
)

REQUEST_TOTAL = Counter(
    "request_total",
    "Total number of requests",
    ["endpoint", "status"]
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    endpoint = request.path
    if endpoint != "/metrics":
        elapsed = time.time() - request.start_time
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
        REQUEST_TOTAL.labels(endpoint=endpoint, status=str(response.status_code)).inc()
    return response

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "model_version": MODEL_VERSION
    })

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    x = payload.get("x", [])

    if payload.get("slow") is True:
        time.sleep(2)

    if not isinstance(x, list):
        return jsonify({
            "status": "error",
            "message": "Поле x должно быть списком чисел"
        }), 400

    try:
        values = [float(v) for v in x]
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Все элементы x должны быть числами"
        }), 400

    prediction = sum(values)

    return jsonify({
        "status": "ok",
        "version": APP_VERSION,
        "model_version": MODEL_VERSION,
        "prediction": prediction
    })

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)