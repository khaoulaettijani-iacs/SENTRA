import os
import requests
import geoip2.database

# Récupération de la clé depuis l'environnement
ABUSEIPDB_API_KEY = os.environ.get("ABUSEIPDB_API_KEY")

# Chemin vers la base de données locale MaxMind
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOIP_DB_PATH = os.path.join(BASE_DIR, "GeoLite2-City.mmdb")

def enrich_ip(ip_address: str) -> dict:
    """
    Enrichit une adresse IP avec ses données géographiques et sa réputation.
    """
    result = {
        "ip": ip_address,
        "geo": {},
        "reputation": {}
    }

    # 1. Enrichissement Géographique (MaxMind local)
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.city(ip_address)
            result["geo"]["country"] = response.country.name
            result["geo"]["city"] = response.city.name
    except FileNotFoundError:
        result["geo"]["error"] = "Base de données MaxMind (.mmdb) introuvable"
    except Exception as e:
        result["geo"]["error"] = str(e)

    # 2. Enrichissement Réputation (API AbuseIPDB)
    if ABUSEIPDB_API_KEY:
        try:
            headers = {
                'Accept': 'application/json',
                'Key': ABUSEIPDB_API_KEY
            }
            # On vérifie l'historique de l'IP sur les 90 derniers jours
            params = {'ipAddress': ip_address, 'maxAgeInDays': 90}
            resp = requests.get('https://api.abuseipdb.com/api/v2/check', headers=headers, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()["data"]
                result["reputation"]["abuse_confidence_score"] = data.get("abuseConfidenceScore")
                result["reputation"]["total_reports"] = data.get("totalReports")
                result["reputation"]["usage_type"] = data.get("usageType")
            else:
                result["reputation"]["error"] = f"Erreur API HTTP {resp.status_code}"
        except Exception as e:
            result["reputation"]["error"] = str(e)
    else:
        result["reputation"]["error"] = "Clé API ABUSEIPDB non configurée dans .env"

    return result

# Bloc de test : s'exécute uniquement si on lance ce script directement
if __name__ == "__main__":
    # Test avec une IP malveillante connue ou publique (Serveur DNS Google)
    test_ip = "8.8.8.8"
    print(f"--- Lancement du test d'enrichissement pour l'IP : {test_ip} ---")
    donnees_enrichies = enrich_ip(test_ip)
    
    import json
    print(json.dumps(donnees_enrichies, indent=4, ensure_ascii=False))