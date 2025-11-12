# app.py
from flask import Flask, request, jsonify, render_template_string
import joblib
import os
import numpy as np

app = Flask(__name__)

MODEL_PATHS = ["models/savedmodel.pth", "model.pkl", "models/model.pkl"]
model = None

for p in MODEL_PATHS:
    if os.path.exists(p):
        try:
            obj = joblib.load(p)
            # If the saved object is the model itself or a dict
            if isinstance(obj, dict) and "model" in obj:
                model = obj["model"]
            else:
                model = obj
            print(f"Loaded model from {p}")
            break
        except Exception as e:
            print(f"Failed to load {p}: {e}")

if model is None:
    print("Warning: no model file found. /predict will error until you train/save a model.")

ROOT_HTML = """
<!doctype html>
<title>Predict</title>
<h1>Simple Predict</h1>
<form method="post" action="/predict-json">
  <label>X:</label>
  <input name="x" type="text" value="1"/>
  <input type="submit" value="Predict (form)">
</form>
<p>Or use POST /predict with JSON: {"X": 1}</p>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(ROOT_HTML)

@app.route("/predict-json", methods=["POST"])
def predict_form():
    # simple form submit wrapper that returns JSON
    try:
        x = float(request.form.get("x", 0))
    except Exception:
        return jsonify({"error": "invalid input"}), 400
    if model is None:
        return jsonify({"error": "no model loaded"}), 500
    arr = np.array([[x]])
    pred = model.predict(arr).tolist()
    return jsonify({"prediction": pred})

@app.route("/predict", methods=["POST"])
def predict():
    """
    Accept JSON like: {"X": 1} or {"X": [1,2,3]}
    Returns {"prediction": ...}
    """
    if model is None:
        return jsonify({"error": "no model loaded"}), 500
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400

    if data is None or "X" not in data:
        return jsonify({"error": "missing 'X' in json body"}), 400

    x = data["X"]
    try:
        arr = np.array(x).reshape(1, -1) if np.ndim(x) == 1 else np.array(x)
    except Exception:
        # fallback: try single value
        arr = np.array([[float(x)]])
    try:
        pred = model.predict(arr).tolist()
        return jsonify({"prediction": pred})
    except Exception as e:
        return jsonify({"error": "prediction failed", "detail": str(e)}), 500

if __name__ == "__main__":
    # Use 0.0.0.0 so Docker container can be bound
    app.run(host="0.0.0.0", port=5000, debug=True)
