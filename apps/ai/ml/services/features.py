import pandas as pd

def sales_features(ventes_qs):
    df = pd.DataFrame(list(ventes_qs.values(
        "quantite", "produit__prix", "created_at"
    )))

    if df.empty:
        return None

    df["montant"] = df["quantite"] * df["produit__prix"]
    df["day"] = df["created_at"].dt.day
    df["month"] = df["created_at"].dt.month

    return df[["quantite", "montant", "day", "month"]]

def expense_features(depenses_qs):
    df = pd.DataFrame(list(depenses_qs.values(
        "montant", "categorie", "created_at"
    )))

    if df.empty:
        return None

    df["day"] = df["created_at"].dt.day
    df["month"] = df["created_at"].dt.month

    # Encodage simple catégorie
    df["categorie_code"] = df["categorie"].astype("category").cat.codes

    return df[["montant", "categorie_code", "day", "month"]]