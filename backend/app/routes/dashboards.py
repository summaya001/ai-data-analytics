from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Dashboard, Dataset, SavedChart  # Added SavedChart here
from ..services.data_processor import DataProcessor
from ..services.visualization_service import VisualizationService

router = APIRouter(prefix="/api", tags=["dashboards"])

# --------------------------
# Pydantic models
# --------------------------

class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: int
    chart_configs: List[dict]
    layout: str = "grid"


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chart_configs: Optional[List[dict]] = None
    layout: Optional[str] = None


# --------------------------
# Create Dashboard
# --------------------------

@router.post("/dashboards")
def create_dashboard(dashboard: DashboardCreate, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dashboard.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        new_dashboard = Dashboard(
            name=dashboard.name,
            description=dashboard.description,
            dataset_id=dashboard.dataset_id,
            chart_ids=dashboard.chart_configs,
            layout=dashboard.layout
        )

        db.add(new_dashboard)
        db.commit()
        db.refresh(new_dashboard)

        return {
            "message": "Dashboard created successfully",
            "dashboard_id": new_dashboard.id,
            "name": new_dashboard.name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dashboard: {str(e)}")


# --------------------------
# Get all dashboards
# --------------------------

@router.get("/dashboards")
def get_all_dashboards(db: Session = Depends(get_db)):
    dashboards = db.query(Dashboard).all()

    return {
        "count": len(dashboards),
        "dashboards": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "dataset_id": d.dataset_id,
                "chart_count": len(d.chart_ids) if d.chart_ids else 0,
                "layout": d.layout,
                "created_at": d.created_at.isoformat(),
                "updated_at": d.updated_at.isoformat()
            }
            for d in dashboards
        ]
    }


# --------------------------
# Get a dashboard
# --------------------------

@router.get("/dashboards/{dashboard_id}")
def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    print(f"Dashboard chart_ids: {dashboard.chart_ids}")  # DEBUG
    print(f"Type: {type(dashboard.chart_ids)}")  # DEBUG

    # Get the dataset
    dataset = db.query(Dataset).filter(Dataset.id == dashboard.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Initialize services
    data_processor = DataProcessor(dataset.file_path)
    viz_service = VisualizationService(data_processor)

    # Generate charts from configs
    charts = []
    if dashboard.chart_ids:
        for i, chart_config in enumerate(dashboard.chart_ids):
            print(f"Processing chart {i}: {chart_config}")  # DEBUG
            try:
                chart_type = chart_config.get("type")
                print(f"Chart type: {chart_type}")  # DEBUG
                
                # Generate the chart based on type
                if chart_type == "bar":
                    chart_data = viz_service.create_bar_chart(chart_config.get("column"))
                elif chart_type == "pie":
                    chart_data = viz_service.create_pie_chart(chart_config.get("column"))
                elif chart_type == "line":
                    chart_data = viz_service.create_line_chart(
                        chart_config.get("x_column"),
                        chart_config.get("y_column")
                    )
                else:
                    print(f"Unknown chart type: {chart_type}")  # DEBUG
                    continue
                
                print(f"Chart data generated: {chart_data[:100] if chart_data else 'None'}")  # DEBUG
                
                charts.append({
                    "type": chart_type,
                    "config": chart_config,
                    "data": chart_data
                })
            except Exception as e:
                print(f"Error generating chart: {e}")  # DEBUG
                import traceback
                traceback.print_exc()
                continue

    print(f"Total charts generated: {len(charts)}")  # DEBUG

    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "description": dashboard.description,
        "dataset_id": dashboard.dataset_id,
        "layout": dashboard.layout,
        "charts": charts,
        "created_at": dashboard.created_at.isoformat(),
        "updated_at": dashboard.updated_at.isoformat()
    }
# --------------------------
# Render dashboard charts (donut removed)
# --------------------------

@router.get("/dashboards/{dashboard_id}/render")
def render_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    dataset = db.query(Dataset).filter(Dataset.id == dashboard.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        processor = DataProcessor(dataset.file_path)
        processor.load_data()
        viz_service = VisualizationService(processor.df)

        charts = []

        for config in dashboard.chart_ids:
            chart_type = config.get("type")

            try:
                if chart_type == "bar":
                    chart = viz_service.create_bar_chart(config["column"])
                elif chart_type == "horizontal_bar":
                    chart = viz_service.create_horizontal_bar_chart(config["column"])
                elif chart_type == "pie":
                    chart = viz_service.create_pie_chart(config["column"])
                elif chart_type == "line":
                    chart = viz_service.create_line_chart(config["x_column"], config["y_column"])
                elif chart_type == "area":
                    chart = viz_service.create_area_chart(config["x_column"], config["y_column"])
                elif chart_type == "box":
                    chart = viz_service.create_box_plot(config["column"])
                elif chart_type == "violin":
                    chart = viz_service.create_violin_plot(config["column"], config.get("group_by"))
                elif chart_type == "grouped_bar":
                    chart = viz_service.create_grouped_bar_chart(
                        config["category_column"],
                        config["value_column"],
                        config["group_column"]
                    )
                elif chart_type == "stacked_bar":
                    chart = viz_service.create_stacked_bar_chart(
                        config["x_column"],
                        config["y_column"],
                        config["stack_column"]
                    )
                else:
                    print(f"Ignoring unknown chart type: {chart_type}")
                    continue

                charts.append(chart)

            except Exception as e:
                print(f"Error generating chart ({chart_type}): {e}")
                continue

        return {
            "dashboard_id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "layout": dashboard.layout,
            "charts": charts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render dashboard: {str(e)}")


# --------------------------
# Update dashboard
# --------------------------

@router.put("/dashboards/{dashboard_id}")
def update_dashboard(dashboard_id: int, dashboard: DashboardUpdate, db: Session = Depends(get_db)):
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    if dashboard.name is not None:
        db_dashboard.name = dashboard.name
    if dashboard.description is not None:
        db_dashboard.description = dashboard.description
    if dashboard.chart_configs is not None:
        db_dashboard.chart_ids = dashboard.chart_configs
    if dashboard.layout is not None:
        db_dashboard.layout = dashboard.layout

    db.commit()
    db.refresh(db_dashboard)

    return {"message": "Dashboard updated successfully", "dashboard_id": db_dashboard.id}


# --------------------------
# Delete dashboard
# --------------------------

@router.delete("/dashboards/{dashboard_id}")
def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    db.delete(dashboard)
    db.commit()

    return {"message": "Dashboard deleted successfully"}
