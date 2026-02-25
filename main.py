from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
from pathlib import Path
import shutil

from database import init_database, add_patient, add_report, get_patient_reports, get_patient
from ai_processor import process_image

app = FastAPI(title="Vitamin Deficiency Detection System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
async def startup_event():
    init_database()

@app.post("/api/analyze")
async def analyze_image(
    patient_id: str = Form(...),
    name: str = Form(...),
    address: str = Form(""),
    phone: str = Form(""),
    image: UploadFile = File(...)
):
    add_patient(patient_id, name, address, phone)
    
    image_id = str(uuid.uuid4())
    image_path = UPLOAD_DIR / f"{image_id}_{image.filename}"
    with image_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    try:
        result = process_image(str(image_path))
        
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        
        report_id = str(uuid.uuid4())
        add_report(
            report_id,
            patient_id,
            str(image_path),
            result["detected_disease"],
            result["confidence_score"],
            result["vitamin_deficiencies"]
        )
        
        return {
            "success": True,
            "report_id": report_id,
            "result": result
        }
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/patient/{patient_id}/reports")
async def get_reports(patient_id: str):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    reports = get_patient_reports(patient_id)
    return {
        "patient": patient,
        "reports": reports
    }

@app.get("/")
async def root():
    return {"message": "Vitamin Deficiency Detection System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
