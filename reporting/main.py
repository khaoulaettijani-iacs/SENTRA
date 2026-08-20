from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from generate_report import generate

app = FastAPI()

@app.post("/report/{event_id}")
def create_report(event_id: str):
    try:
        incident_id = generate(event_id)
    except Exception as e:
        raise HTTPException(404, f"Événement introuvable ou erreur de génération : {e}")
    return {"incident_id": incident_id, "pdf": f"/report/{incident_id}/pdf", "txt": f"/report/{incident_id}/txt"}

@app.get("/report/{incident_id}/pdf")
def get_pdf(incident_id: str):
    return FileResponse(f"output/{incident_id}.pdf", media_type="application/pdf")

@app.get("/report/{incident_id}/txt")
def get_txt(incident_id: str):
    return FileResponse(f"output/{incident_id}.txt", media_type="text/plain")