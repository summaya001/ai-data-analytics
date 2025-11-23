from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db
from .routes import upload, visualizations, dashboards
import os

app = FastAPI(title="AI Data Analytics API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Include routers
app.include_router(upload.router)
app.include_router(visualizations.router)
app.include_router(dashboards.router)
# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized!")

@app.get("/")
def read_root():
    return {"message": "AI Data Analytics API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)