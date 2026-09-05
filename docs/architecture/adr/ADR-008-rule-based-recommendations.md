# ADR-008 : Génération des Recommandations (Rule-based vs LLM)

Le moteur de reporting (`reporting-engine`) de SENTRA a pour rôle de générer des "Evidence Packs" (PDF/TXT) pour chaque incident corrélé. Outre les métriques techniques, ce rapport doit fournir des recommandations de remédiation (Playbooks) pour guider l'analyste SOC. Nous devions choisir la méthode de génération de ce texte.

## Alternatives Envisagées

1.  **IA Générative (LLM via API externe, ex: OpenAI GPT-4) :** Envoyer les détails de l'alerte à une API externe pour générer un texte naturel et des conseils sur mesure.
2.  **IA Générative Locale (LLM via Ollama/Llama3) :** Héberger un modèle de langage directement sur l'infrastructure du SOC pour générer le texte sans fuite de données.
3.  **Système Expert Déterministe (Rule-based Mapping) :** Utiliser un dictionnaire Python associant statiquement des recommandations pré-approuvées aux tactiques du MITRE ATT&CK et aux niveaux de risque.


Nous avons opté pour le **Système Expert Déterministe (Rule-based Mapping)** implémenté dans `recommendations.py`.

## Justification 

*   **Sécurité et Confidentialité (Air-Gapped SOC) :** L'utilisation d'une API externe (Option 1) implique d'envoyer des traces réseau internes et des adresses IP à un tiers. Cela viole les politiques strictes de confidentialité des données inhérentes à un SOC.
*   **Contraintes Matérielles :** L'hébergement d'un LLM local (Option 2) exige des ressources GPU considérables ou une consommation massive de RAM/CPU, ce qui est incompatible avec notre architecture de microservices déjà gourmande (Elasticsearch, Kibana, Modèles de ML Scikit-Learn).
*   **Risque d'Hallucination (Fiabilité) :** Un SOC requiert une précision absolue. Un LLM pourrait générer des commandes irréalisables ou recommander des procédures qui ne correspondent pas à la politique de sécurité réelle de l'entreprise.
*   **Déterminisme et Playbooks :** En cybersécurité de niveau 1 (L1), les actions doivent suivre des *Playbooks* stricts et répétables. Le dictionnaire déterministe garantit que face à une attaque "Credential Access", l'analyste recevra toujours exactement les 3 mêmes directives validées par l'équipe L3, avec un flag de priorité automatique si le risque est "High" ou "Critical".

## Conséquences
*   Génération instantanée des rapports (aucune latence liée à l'inférence texte).
*   Consommation CPU/RAM proche de zéro pour cette fonctionnalité.
*   Nécessité de mettre à jour manuellement le dictionnaire `recommendations.py` si de nouvelles tactiques MITRE sont intégrées au SOC à l'avenir (compromis accepté).