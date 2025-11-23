from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from ..database import get_db
from ..models import Dataset
from ..services.data_processor import DataProcessor
from ..services.ai_service import AIService  

router = APIRouter(prefix="/api", tags=["upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

# ---------------------------
# Upload endpoint
# ---------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV or Excel file for analysis
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        processor = DataProcessor(file_path)
        processor.load_data()
        summary = processor.get_summary()
        
        dataset = Dataset(
            filename=file.filename,
            file_path=file_path,
            columns_info=summary["column_types"],
            row_count=summary["rows"]
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return {
            "message": "File uploaded successfully",
            "dataset_id": dataset.id,
            "filename": file.filename,
            "summary": summary
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

# ---------------------------
# Get all datasets
# ---------------------------
@router.get("/datasets")
def get_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    return {
        "count": len(datasets),
        "datasets": [
            {
                "id": d.id,
                "filename": d.filename,
                "row_count": d.row_count,
                "columns": len(d.columns_info) if d.columns_info else 0,
                "uploaded_at": d.uploaded_at.isoformat()
            }
            for d in datasets
        ]
    }

# ---------------------------
# Get dataset details
# ---------------------------
@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "id": dataset.id,
        "filename": dataset.filename,
        "row_count": dataset.row_count,
        "columns_info": dataset.columns_info,
        "uploaded_at": dataset.uploaded_at.isoformat()
    }

# ---------------------------
# Get dataset preview
# ---------------------------
@router.get("/datasets/{dataset_id}/preview")
def get_dataset_preview(dataset_id: int, rows: int = 10, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        preview = processor.get_preview(num_rows=rows)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview data: {str(e)}")

# ---------------------------
# Get dataset statistics
# ---------------------------
@router.get("/datasets/{dataset_id}/statistics")
def get_dataset_statistics(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        stats = processor.get_statistics()
        return {"dataset_id": dataset_id, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# ---------------------------
# Clean dataset
# ---------------------------
@router.post("/datasets/{dataset_id}/clean")
def clean_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        report = processor.clean_data()
        dataset.row_count = report["final_rows"]
        db.commit()
        return {"dataset_id": dataset_id, "cleaning_report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean data: {str(e)}")

# ---------------------------
# Get column info
# ---------------------------
@router.get("/datasets/{dataset_id}/columns/{column_name}")
def get_column_info(dataset_id: int, column_name: str, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        info = processor.get_column_info(column_name)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get column info: {str(e)}")

# ---------------------------
# Analyze dataset (AI-powered insights)
# ---------------------------
@router.post("/datasets/{dataset_id}/analyze")
def analyze_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """
    Generate AI-powered insights for a dataset
    """
    # Get dataset from database
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        # Load and process data
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        summary = processor.get_summary()
        statistics = processor.get_statistics()
        
        # Prepare data for AI analysis
        data_for_ai = {
            "rows": summary["rows"],
            "columns": summary["columns"],
            "column_names": summary["column_names"],
            "column_types": summary["column_types"],
            "statistics": statistics
        }
        
        # Get AI insights
        ai_service = AIService()
        insights = ai_service.analyze_data(data_for_ai)
        
        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "insights": insights,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze dataset: {str(e)}")