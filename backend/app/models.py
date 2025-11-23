from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    columns_info = Column(JSON)
    row_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, nullable=False)
    insight_text = Column(Text)
    chart_type = Column(String)
    chart_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    dataset_id = Column(Integer, nullable=False)
    chart_ids = Column(JSON)  # List of chart configurations
    layout = Column(String, default="grid")  # grid, 2x2, 3x1, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavedChart(Base):
    __tablename__ = "saved_charts"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)  # User-given name
    chart_type = Column(String, nullable=False)  # bar, pie, scatter, etc.
    chart_config = Column(JSON)  # Column names, parameters
    chart_data = Column(Text)  # The actual Plotly JSON
    created_at = Column(DateTime, default=datetime.utcnow)    
