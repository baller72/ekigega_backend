from .models import sales_ml_analysis, expense_ml_analysis
from .health_score import compute_health_score

def enterprise_health_analysis(entreprise):
    sales = sales_ml_analysis(entreprise)
    expenses = expense_ml_analysis(entreprise.depenses.all())

    stock_score = entreprise.produits.filter(quantite__gt=0).count() * 10
    subscription_score = entreprise.abonnements.filter(active=True).count() * 15

    return {
        "health_score": compute_health_score(
            sales_score=sales.get("score", 0),
            expense_risk=expenses.get("risk_score", 0),
            stock_score=min(stock_score, 100),
            subscription_score=min(subscription_score, 100),
        ),
        "details": {
            "sales": sales,
            "expenses": expenses,
            "stock_score": stock_score,
            "subscription_score": subscription_score
        }
    }