from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Dataset
from ..services.data_processor import DataProcessor
from ..services.visualization_service import VisualizationService

router = APIRouter(prefix="/api", tags=["visualizations"])

@router.get("/datasets/{dataset_id}/chart-recommendations")
def get_chart_recommendations(dataset_id: int, db: Session = Depends(get_db)):
    """
    Get recommended chart types for the dataset
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        # Load data
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Get recommendations
        viz_service = VisualizationService(processor.df)
        recommendations = viz_service.recommend_charts()
        
        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/datasets/{dataset_id}/charts/auto")
def generate_all_charts(dataset_id: int, db: Session = Depends(get_db)):
    """
    Automatically generate all recommended charts for the dataset
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        # Load data
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Generate all charts
        viz_service = VisualizationService(processor.df)
        charts = viz_service.generate_all_recommended_charts()
        
        return {
            "dataset_id": dataset_id,
            "filename": dataset.filename,
            "total_charts": len(charts),
            "charts": charts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate charts: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/bar")
def create_bar_chart(
    dataset_id: int,
    column: str,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Create a bar chart for a specific column
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_bar_chart(column, top_n)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/pie")
def create_pie_chart(
    dataset_id: int,
    column: str,
    top_n: int = 8,
    db: Session = Depends(get_db)
):
    """
    Create a pie chart for a specific column
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_pie_chart(column, top_n)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/box")
def create_box_plot(
    dataset_id: int,
    column: str,
    db: Session = Depends(get_db)
):
    """
    Create a box plot for a numeric column (shows quartiles and outliers)
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Check if column exists and is numeric
        if column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found in dataset")
        
        if processor.df[column].dtype not in ['int64', 'float64']:
            raise HTTPException(
                status_code=400, 
                detail=f"Column '{column}' must be numeric. Current type: {processor.df[column].dtype}"
            )
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_box_plot(column)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/violin")
def create_violin(
    dataset_id: int,
    column: str,
    group_by: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a violin plot (shows distribution shape)
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Check if column exists and is numeric
        if column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found in dataset")
        
        if processor.df[column].dtype not in ['int64', 'float64']:
            raise HTTPException(
                status_code=400, 
                detail=f"Column '{column}' must be numeric for violin plot"
            )
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_violin_plot(column, group_by)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")

@router.post("/datasets/{dataset_id}/charts/area")
def create_area_chart(
    dataset_id: int,
    x_column: str,
    y_column: str,
    db: Session = Depends(get_db)
):
    """
    Create an area chart (filled line chart)
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Validate columns exist
        if x_column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{x_column}' not found")
        if y_column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{y_column}' not found")
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_area_chart(x_column, y_column)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/stacked_bar")
def create_stacked_bar(
    dataset_id: int,
    x_column: str,
    y_column: str,
    stack_column: str,
    db: Session = Depends(get_db)
):
    """
    Create a stacked bar chart
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Validate columns exist
        missing_cols = []
        for col in [x_column, y_column, stack_column]:
            if col not in processor.df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Columns not found: {', '.join(missing_cols)}"
            )
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_stacked_bar_chart(x_column, y_column, stack_column)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/grouped_bar")
def create_grouped_bar(
    dataset_id: int,
    category_column: str,
    value_column: str,
    group_column: str,
    db: Session = Depends(get_db)
):
    """
    Create a grouped bar chart (compare categories side-by-side)
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Validate columns exist
        missing_cols = []
        for col in [category_column, value_column, group_column]:
            if col not in processor.df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Columns not found: {', '.join(missing_cols)}"
            )
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_grouped_bar_chart(category_column, value_column, group_column)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@router.post("/datasets/{dataset_id}/charts/line")
def create_line_chart(
    dataset_id: int,
    x_column: str,
    y_column: str,
    db: Session = Depends(get_db)
):
    """
    Create a line chart for two columns
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        
        # Validate columns exist
        if x_column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{x_column}' not found")
        if y_column not in processor.df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{y_column}' not found")
        
        viz_service = VisualizationService(processor.df)
        chart = viz_service.create_line_chart(x_column, y_column)
        
        return {
            "dataset_id": dataset_id,
            "chart": chart
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


# ==================== SAVED CHARTS ROUTES ====================

@router.post("/datasets/{dataset_id}/charts/save")
def save_chart(
    dataset_id: int,
    name: str,
    chart_type: str,
    chart_config: dict,
    chart_data: str,
    db: Session = Depends(get_db)
):
    """
    Save a generated chart to the database
    """
    from ..models import SavedChart
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        saved_chart = SavedChart(
            dataset_id=dataset_id,
            name=name,
            chart_type=chart_type,
            chart_config=chart_config,
            chart_data=chart_data
        )
        db.add(saved_chart)
        db.commit()
        db.refresh(saved_chart)
        
        return {
            "message": "Chart saved successfully",
            "chart_id": saved_chart.id,
            "name": saved_chart.name
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save chart: {str(e)}")


@router.get("/charts/saved")
def get_saved_charts(db: Session = Depends(get_db)):
    """
    Get all saved charts
    """
    from ..models import SavedChart
    
    try:
        charts = db.query(SavedChart).all()
        return {
            "count": len(charts),
            "charts": [
                {
                    "id": c.id,
                    "dataset_id": c.dataset_id,
                    "name": c.name,
                    "chart_type": c.chart_type,
                    "created_at": c.created_at.isoformat()
                }
                for c in charts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch saved charts: {str(e)}")


@router.get("/charts/saved/{chart_id}")
def get_saved_chart(chart_id: int, db: Session = Depends(get_db)):
    """
    Get a specific saved chart with full data
    """
    from ..models import SavedChart
    
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    return {
        "id": chart.id,
        "dataset_id": chart.dataset_id,
        "name": chart.name,
        "chart_type": chart.chart_type,
        "chart_config": chart.chart_config,
        "chart_data": chart.chart_data,
        "created_at": chart.created_at.isoformat()
    }


@router.delete("/charts/saved/{chart_id}")
def delete_saved_chart(chart_id: int, db: Session = Depends(get_db)):
    """
    Delete a saved chart
    """
    from ..models import SavedChart
    
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        db.delete(chart)
        db.commit()
        return {"message": "Chart deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete chart: {str(e)}")