import os, ipaddress, requests, geoip2.database

GEOIP_DB_PATH = os.environ.get("GEOIP_DB_PATH", "/app/data/GeoLite2-City.mmdb")
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_API_KEY")
_geo_reader = geoip2.database.Reader(GEOIP_DB_PATH) if os.path.exists(GEOIP_DB_PATH) else None

def is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True

def geoip_lookup(ip: str) -> dict:
    if is_private_ip(ip) or not _geo_reader:
        return {"country": None, "city": None, "note": "private/lab IP or GeoIP DB unavailable"}
    try:
        r = _geo_reader.city(ip)
        return {"country": r.country.name, "city": r.city.name,
                "lat": r.location.latitude, "lon": r.location.longitude}
    except Exception:
        return {"country": None, "city": None, "note": "lookup failed"}

def abuseipdb_lookup(ip: str) -> dict:
    if is_private_ip(ip) or not ABUSEIPDB_KEY:
        return {"abuse_score": None, "note": "private/lab IP or API key missing"}
    try:
        r = requests.get("https://api.abuseipdb.com/api/v2/check",
            headers={"Key": ABUSEIPDB_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90}, timeout=5)
        d = r.json()["data"]
        return {"abuse_score": d["abuseConfidenceScore"], "total_reports": d["totalReports"]}
    except Exception as e:
        return {"abuse_score": None, "note": f"lookup failed: {e}"}

def enrich(ip: str) -> dict:
    return {"geoip": geoip_lookup(ip), "abuseipdb": abuseipdb_lookup(ip)}