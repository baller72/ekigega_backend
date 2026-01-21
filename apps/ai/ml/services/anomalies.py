from sklearn.ensemble import IsolationForest

def detect_sales_anomalies(features):
    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )
    preds = model.fit_predict(features)

    features["anomaly"] = preds
    return features[features["anomaly"] == -1]


def detect_expense_anomalies(features):
    model = IsolationForest(
        contamination=0.08,
        random_state=42
    )
    preds = model.fit_predict(features)

    features["anomaly"] = preds
    return features[features["anomaly"] == -1]