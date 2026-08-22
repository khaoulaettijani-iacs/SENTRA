import os, psycopg2, psycopg2.extras
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from notifications import notify_if_critical
from enrichment.enrichment import enrich_ip

app = FastAPI()
DATABASE_URL = os.environ["DATABASE_URL"]

ALLOWED_TRANSITIONS = {
    "new": ["in_investigation", "false_positive"],
    "in_investigation": ["confirmed", "false_positive"],
    "confirmed": ["closed"],
    "false_positive": ["closed"],
    "closed": [],
}

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

class IncidentCreate(BaseModel):
    correlated_event_id: str
    src_ip: str
    dest_ip: str
    signature: str
    mitre_tactic: str
    mitre_technique_id: str
    mitre_technique_name: str
    risk_score: float
    risk_level: str
    enrichment: dict = {}

class StatusUpdate(BaseModel):
    new_status: str
    actor: str = "system"
    reason: Optional[str] = None

class AssignUpdate(BaseModel):
    analyst_id: int
    actor: str = "system"

@app.post("/incidents")
def create_incident(inc: IncidentCreate):
    # Enrich the incident data
    inc.enrichment = enrich_ip(inc.src_ip, inc.dest_ip)

    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO incidents (correlated_event_id, src_ip, dest_ip, signature,
                mitre_tactic, mitre_technique_id, mitre_technique_name,
                risk_score, risk_level, enrichment)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (correlated_event_id) DO NOTHING
            RETURNING id, status;
        """, (inc.correlated_event_id, inc.src_ip, inc.dest_ip, inc.signature,
              inc.mitre_tactic, inc.mitre_technique_id, inc.mitre_technique_name,
              inc.risk_score, inc.risk_level, psycopg2.extras.Json(inc.enrichment)))
        row = cur.fetchone()
        if not row:
            raise HTTPException(409, "Incident déjà existant pour cet événement")
        cur.execute("""
            INSERT INTO incident_audit_log (incident_id, action, field_changed, old_value, new_value, actor)
            VALUES (%s,'created','status',NULL,'new','system');
        """, (row["id"],))

    notif = notify_if_critical({**inc.dict(), "id": row["id"]})
    return {"id": row["id"], "status": row["status"], "notification": notif}

@app.get("/incidents")
def list_incidents(status: Optional[str] = None, risk_level: Optional[str] = None,
                    mitre_tactic: Optional[str] = None, assigned_analyst_id: Optional[int] = None,
                    src_ip: Optional[str] = None, limit: int = 50, offset: int = 0):
    conditions, params = [], []
    for field, value in [("status", status), ("risk_level", risk_level),
                          ("mitre_tactic", mitre_tactic),
                          ("assigned_analyst_id", assigned_analyst_id),
                          ("src_ip", src_ip)]:
        if value is not None:
            conditions.append(f"{field} = %s")
            params.append(value)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute(f"SELECT * FROM incidents {where} ORDER BY created_at DESC LIMIT %s OFFSET %s;",
                    (*params, limit, offset))
        return cur.fetchall()

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM incidents WHERE id=%s;", (incident_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Incident introuvable")
        return row

@app.patch("/incidents/{incident_id}/status")
def update_status(incident_id: int, upd: StatusUpdate):
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT status FROM incidents WHERE id=%s;", (incident_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Incident introuvable")
        current = row["status"]
        if upd.new_status not in ALLOWED_TRANSITIONS.get(current, []):
            raise HTTPException(400, f"Transition {current} → {upd.new_status} non autorisée")
        cur.execute("UPDATE incidents SET status=%s, updated_at=now() WHERE id=%s;",
                     (upd.new_status, incident_id))
        cur.execute("""INSERT INTO incident_audit_log
            (incident_id, action, field_changed, old_value, new_value, actor)
            VALUES (%s,'status_change','status',%s,%s,%s);""",
            (incident_id, current, upd.new_status, upd.actor))
    return {"id": incident_id, "old_status": current, "new_status": upd.new_status}

@app.patch("/incidents/{incident_id}/assign")
def assign_incident(incident_id: int, upd: AssignUpdate):
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT assigned_analyst_id FROM incidents WHERE id=%s;", (incident_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Incident introuvable")
        cur.execute("UPDATE incidents SET assigned_analyst_id=%s, updated_at=now() WHERE id=%s;",
                     (upd.analyst_id, incident_id))
        cur.execute("""INSERT INTO incident_audit_log
            (incident_id, action, field_changed, old_value, new_value, actor)
            VALUES (%s,'assignment_change','assigned_analyst_id',%s,%s,%s);""",
            (incident_id, str(row["assigned_analyst_id"]), str(upd.analyst_id), upd.actor))
    return {"id": incident_id, "assigned_analyst_id": upd.analyst_id}

@app.get("/incidents/{incident_id}/audit")
def get_audit(incident_id: int):
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM incident_audit_log WHERE incident_id=%s ORDER BY changed_at;", (incident_id,))
        return cur.fetchall()

@app.get("/analysts")
def list_analysts():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM analysts;")
        return cur.fetchall()