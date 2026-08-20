import os, uuid
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from elasticsearch import Elasticsearch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from recommendations import get_recommendations

ES = Elasticsearch(os.environ.get("ES_HOST", "http://elasticsearch:9200"))
env = Environment(loader=FileSystemLoader("templates"))

def fetch_event(event_id: str) -> dict:
    doc = ES.get(index="correlated-events", id=event_id)
    return doc["_source"]

def build_context(event: dict) -> dict:
    mitre = event.get("mitre", {})
    ml = event.get("ml", {})
    risk = event.get("risk", {})
    return {
        "incident_id": str(uuid.uuid4())[:8],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "timestamp": event.get("@timestamp"),
        "src_ip": event.get("src_ip"), "dest_ip": event.get("dest_ip"),
        "signature": event.get("signature"),
        "ids_severity": event.get("ids_severity", "-"),
        "mitre_tactic": mitre.get("tactic", "Unmapped"),
        "mitre_technique_id": mitre.get("technique_id", "-"),
        "mitre_technique_name": mitre.get("technique_name", "-"),
        "rf_proba": ml.get("rf_proba", 0),
        "iso_raw_score": ml.get("iso_raw_score", 0),
        "risk_score": risk.get("risk_score", 0),
        "risk_level": risk.get("risk_level", "Unknown"),
        "breakdown": risk.get("breakdown", {}),
        "recommendations": get_recommendations(mitre.get("tactic", "Unmapped"), risk.get("risk_level", "Low")),
    }

def render_text(ctx: dict, out_path: str):
    template = env.get_template("incident_report.j2")
    with open(out_path, "w") as f:
        f.write(template.render(**ctx))

def render_pdf(ctx: dict, out_path: str):
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Rapport d'incident de sécurité — SENTRA", styles["Title"]),
        Paragraph(f"Référence : {ctx['incident_id']} — Généré le {ctx['generated_at']}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Résumé exécutif", styles["Heading2"]),
        Paragraph(
            f"Le {ctx['timestamp']}, une activité classée {ctx['risk_level']} "
            f"(score {ctx['risk_score']}/100) a été détectée depuis {ctx['src_ip']} "
            f"vers {ctx['dest_ip']}, associée à la technique MITRE {ctx['mitre_technique_id']} "
            f"({ctx['mitre_technique_name']}).", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Détails techniques", styles["Heading2"]),
    ]

    data = [
        ["Signature IDS", ctx["signature"]],
        ["Sévérité IDS", str(ctx["ids_severity"])],
        ["Tactique MITRE", ctx["mitre_tactic"]],
        ["Technique MITRE", f"{ctx['mitre_technique_id']} — {ctx['mitre_technique_name']}"],
        ["Probabilité RF", f"{ctx['rf_proba']:.3f}"],
        ["Score Isolation Forest", f"{ctx['iso_raw_score']:.3f}"],
        ["Score de risque", f"{ctx['risk_score']}/100 ({ctx['risk_level']})"],
    ]
    table = Table(data, colWidths=[180, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements += [table, Spacer(1, 16), Paragraph("Recommandations", styles["Heading2"])]
    elements += [Paragraph(f"• {r}", styles["Normal"]) for r in ctx["recommendations"]]

    doc.build(elements)

def generate(event_id: str, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    event = fetch_event(event_id)
    ctx = build_context(event)
    render_text(ctx, f"{output_dir}/{ctx['incident_id']}.txt")
    render_pdf(ctx, f"{output_dir}/{ctx['incident_id']}.pdf")
    return ctx["incident_id"]

if __name__ == "__main__":
    import sys
    print(generate(sys.argv[1]))