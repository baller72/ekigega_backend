

def normalize(value, max_value):
    return min(100, int((value / max_value) * 100)) if max_value > 0 else 0


def compute_health_score(
    sales_score,
    expense_risk,
    stock_score,
    subscription_score
):
    weights = {
        "sales": 0.35,
        "expenses": 0.30,
        "stock": 0.20,
        "subscriptions": 0.15
    }

    score = (
        sales_score * weights["sales"]
        + (100 - expense_risk) * weights["expenses"]
        + stock_score * weights["stock"]
        + subscription_score * weights["subscriptions"]
    )

    return int(score)