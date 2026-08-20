def get_recommendations(mitre_tactic: str, risk_level: str) -> list[str]:
    base = {
        "Credential Access": [
            "Forcer la réinitialisation du mot de passe du compte ciblé",
            "Vérifier l'activation du MFA sur le service SSH exposé",
            "Analyser les logs d'authentification pour d'éventuelles connexions réussies suite aux tentatives",
        ],
        "Reconnaissance": [
            "Vérifier que la segmentation réseau limite bien la portée du scan",
            "Confirmer qu'aucun service non nécessaire n'est exposé sur l'hôte ciblé",
            "Surveiller la source pour une éventuelle escalade vers une tentative d'exploitation",
        ],
        "Unmapped": [
            "Analyser manuellement la signature pour un mapping MITRE ultérieur",
        ],
    }
    recs = base.get(mitre_tactic, base["Unmapped"])
    if risk_level in ("Critical", "High"):
        recs.insert(0, "Action prioritaire : traiter cet incident avant les incidents de niveau inférieur")
    return recs