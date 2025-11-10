import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import ContactMessage

app = FastAPI(title="Falcon (cnear) API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Falcon API is running", "product": "cnear", "status": "ok"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Falcon backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Contact form endpoint to capture leads from landing page
@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lightweight content endpoints for the landing page
@app.get("/api/features")
def features():
    return {
        "tagline": "India's Fastest Growing AI Based Platform for Placement Assistance.",
        "sections": [
            {
                "title": "For Students",
                "items": [
                    "Job Portal: Browse jobs, apply, and track application status.",
                    "Resume Builder: Create and update resumes with AI assistance.",
                    "Placement Policies: View eligibility criteria for job applications.",
                    "Study Resources: Access AI-curated study materials."
                ]
            },
            {
                "title": "For Placement Officers",
                "items": [
                    "Job Postings: Create, manage, and track job opportunities.",
                    "Student Shortlisting: Use AI-driven shortlisting to identify the best candidates.",
                    "Application Monitoring: Oversee student applications and their progress.",
                    "Placement Analytics: Access real-time reports and insights."
                ]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
