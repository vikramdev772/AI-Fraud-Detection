from flask import Flask, request, jsonify
import pickle
import numpy as np
import traceback

app = Flask(__name__)
print("Fraud Detection ML Service Starting...")

with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def home():
    return jsonify({"status": "Fraud Detection API Running"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if data is None:
        try:
            data = request.json
        except:
            return jsonify({"error": "Invalid JSON request"}), 400

    amount = float(data["amount"])
    hour = int(data["hour"])
    category = int(data["category"])
    device = int(data["device"])

    features = np.array([[amount, hour, category, device]])

    prediction = int(model.predict(features)[0])

    proba = None
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(features)
        proba = float(probs[0][min(1, probs.shape[1] - 1)])

    return jsonify({
        "fraud": prediction,
        "probability": proba
    })


# 🔥 FORCE JSON FOR ALL 500 ERRORS
@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal Server Error",
        "details": str(e),
        "trace": traceback.format_exc()
    }), 500


@app.errorhandler(Exception)
def all_exception_handler(e):
    return jsonify({
        "error": "Unhandled Exception",
        "details": str(e),
        "trace": traceback.format_exc()
    }), 500


if __name__ == "__main__":
    app.run(port=5050, debug=True)