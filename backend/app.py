from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

bundle = joblib.load("stroke_rf_bundle.pkl")
bmi_imputer = bundle["bmi_imputer"]
encoders = bundle["encoders"]
scaler = bundle["scaler"]
model = bundle["model"]
categorical_cols = bundle["categorical_cols"]
feature_order = bundle["feature_order"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()

    age_raw = data.get("age")
    if age_raw in [None, ""]:
        return jsonify({"error":"Missing age"}), 400


    # Build row with dataset column names
    row = {
        "gender": data.get("gender", "Male"),
        "age": float(data.get("age")),
        "hypertension": int(data.get("hypertension")),
        "heart_disease": int(data.get("heart_disease")),
        "ever_married": data.get("ever_married", "No"),
        "work_type": data.get("work_type", "Private"),
        "Residence_type": data.get("Residence_type", "Urban"),
        "avg_glucose_level": float(data.get("avg_glucose_level")),
        "bmi": None if data.get("bmi") in [None, "", "null"] else float(data.get("bmi")),
        "smoking_status": data.get("smoking_status", "Unknown")
    }

    X = pd.DataFrame([row])

    # 1) BMI imputation
    X["bmi"] = bmi_imputer.transform(X[["bmi"]])

    # 2) Label encode categoricals (safe for unseen)
    for col in categorical_cols:
        le = encoders[col]
        v = str(X.loc[0, col])

        known = set(le.classes_)
        fallback = "Unknown" if "Unknown" in known else le.classes_[0]
        if v not in known:
            v = fallback

        X.loc[0, col] = le.transform([v])[0]

    # 3) Ensure same column order as training
    X = X[feature_order]

    # 4) Scale then predict proba
    Xs = scaler.transform(X)
    proba = float(model.predict_proba(Xs)[:, 1][0])
    percent = round(proba * 100, 1)

    # Risk label (UI thresholds; you can tweak)
    if proba < 0.15:
        risk_level = "low"
    elif proba < 0.35:
        risk_level = "moderate"
    else:
        risk_level = "high"

    # Simple factors (rule-based explainer)
    factors = []
    if row["age"] >= 60:
        factors.append("Âge élevé (≥ 60)")
    if row["avg_glucose_level"] >= 140:
        factors.append("Glucose élevé (≥ 140 mg/dL)")
    if row["bmi"] is not None and float(bmi_imputer.transform([[row["bmi"]]])[0][0]) >= 30:
        factors.append("IMC élevé (≥ 30)")
    if row["hypertension"] == 1:
        factors.append("Hypertension")
    if row["heart_disease"] == 1:
        factors.append("Maladie cardiaque")
    if row["smoking_status"] == "smokes":
        factors.append("Fumeur actif")

    return jsonify({
        "probability": proba,
        "percentage": percent,
        "risk_level": risk_level,
        "factors": factors
    })

if __name__ == "__main__":
    app.run(debug=True)
