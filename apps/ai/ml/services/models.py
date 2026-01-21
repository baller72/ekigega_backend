from .features import expense_features, sales_features
from .anomalies import detect_expense_anomalies, detect_sales_anomalies
from .predictors import expense_drift_score, predict_sales_trend

def sales_ml_analysis(ventes_qs):
    features = sales_features(ventes_qs)
    if features is None:
        return {}

    anomalies = detect_sales_anomalies(features)
    trend = predict_sales_trend(features)

    return {
        "predicted_next_sales": trend,
        "anomalies_count": len(anomalies),
        "anomalies": anomalies.head(5).to_dict()
    }


def expense_ml_analysis(depenses_qs):
    features = expense_features(depenses_qs)
    if features is None:
        return {}

    anomalies = detect_expense_anomalies(features)
    drift = expense_drift_score(features)

    risk_score = min(100, len(anomalies) * 10 + drift["drift_ratio"] * 10)

    return {
        "risk_score": int(risk_score),
        "anomalies_count": len(anomalies),
        "drift": drift,
        "anomalies": anomalies.head(5).to_dict()
    }