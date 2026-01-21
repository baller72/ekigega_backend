from sklearn.linear_model import LinearRegression
import numpy as np

def predict_sales_trend(features):
    X = np.arange(len(features)).reshape(-1, 1)
    y = features["montant"].values

    model = LinearRegression()
    model.fit(X, y)

    next_value = model.predict([[len(features)]])[0]
    return round(float(next_value), 2)

def expense_drift_score(features):
    avg = features["montant"].mean()
    max_val = features["montant"].max()

    drift_ratio = round(max_val / avg, 2) if avg > 0 else 0

    return {
        "average_expense": round(avg, 2),
        "max_expense": round(max_val, 2),
        "drift_ratio": drift_ratio
    }