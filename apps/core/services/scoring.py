def compute_kigega_score(kpis):
    score = 0

    if kpis["revenus"] > kpis["depenses"]:
        score += 40

    if kpis["total_ventes"] > 20:
        score += 30

    if kpis["depenses"] < kpis["revenus"] * 0.7:
        score += 30

    return min(score, 100)
