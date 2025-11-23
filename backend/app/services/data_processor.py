import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
    
    def load_data(self) -> pd.DataFrame:
        """Load CSV or Excel file and safely convert numeric columns"""
        try:
            # --- Load file as before ---
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format")

            # ✅ Convert numeric-looking columns only (non-blocking and safe)
            for col in self.df.columns:
                # Try to convert, ignore if not possible
                self.df[col] = pd.to_numeric(self.df[col], errors='ignore')

            # Optional: Debug print (use logging instead of print in production)
            print("[DataProcessor] Loaded file:", self.file_path)
            print("[DataProcessor] Column types:")
            print(self.df.dtypes)

            return self.df

        except Exception as e:
            # Print to console so we actually SEE the error
            import traceback
            traceback.print_exc()
            raise Exception(f"Error loading file: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get basic data summary"""
        if self.df is None:
            self.load_data()
        
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
            "column_types": self._get_column_types(),
            "missing_values": self.df.isnull().sum().to_dict()
        }
    
    def get_preview(self, num_rows: int = 10) -> Dict[str, Any]:
        """Get preview of first N rows"""
        if self.df is None:
            self.load_data()
        
        preview_df = self.df.head(num_rows)
        
        return {
            "columns": self.df.columns.tolist(),
            "data": preview_df.values.tolist(),
            "total_rows": len(self.df)
        }
    
    def _get_column_types(self) -> Dict[str, str]:
        """Detect and return column types"""
        column_types = {}
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            
            # Categorize types
            if dtype.startswith('int') or dtype.startswith('uint'):
                column_types[col] = "integer"
            elif dtype.startswith('float'):
                column_types[col] = "float"
            elif dtype == 'bool':
                column_types[col] = "boolean"
            elif dtype == 'object':
                # Try to detect if it's actually a date or category
                if self._is_date_column(col):
                    column_types[col] = "date"
                elif self._is_categorical(col):
                    column_types[col] = "category"
                else:
                    column_types[col] = "text"
            else:
                column_types[col] = dtype
        
        return column_types
    
    def _is_date_column(self, column: str) -> bool:
        """Check if column contains dates"""
        try:
            pd.to_datetime(self.df[column], errors='coerce')
            # If more than 50% of values are valid dates, consider it a date column
            valid_dates = pd.to_datetime(self.df[column], errors='coerce').notna().sum()
            return valid_dates / len(self.df) > 0.5
        except:
            return False
    
    def _is_categorical(self, column: str) -> bool:
        """Check if column is categorical (limited unique values)"""
        unique_ratio = self.df[column].nunique() / len(self.df)
        # If less than 5% unique values, consider it categorical
        return unique_ratio < 0.05
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary for numeric columns"""
        if self.df is None:
            self.load_data()
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        statistics = {}
        for col in numeric_cols:
            statistics[col] = {
                "mean": float(self.df[col].mean()),
                "median": float(self.df[col].median()),
                "min": float(self.df[col].min()),
                "max": float(self.df[col].max()),
                "std": float(self.df[col].std()),
                "missing": int(self.df[col].isnull().sum())
            }
        
        return statistics
    
    def clean_data(self) -> Dict[str, Any]:
        """Perform basic data cleaning"""
        if self.df is None:
            self.load_data()
        
        cleaning_report = {
            "original_rows": len(self.df),
            "actions": []
        }
        
        # Remove duplicate rows
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            self.df = self.df.drop_duplicates()
            cleaning_report["actions"].append(f"Removed {duplicates} duplicate rows")
        
        # Handle missing values in numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                # Fill with median
                self.df[col].fillna(self.df[col].median(), inplace=True)
                cleaning_report["actions"].append(
                    f"Filled {missing_count} missing values in '{col}' with median"
                )
        
        # Handle missing values in text columns
        text_cols = self.df.select_dtypes(include=['object']).columns
        for col in text_cols:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                # Fill with mode (most common value) or 'Unknown'
                mode_val = self.df[col].mode()
                fill_value = mode_val[0] if len(mode_val) > 0 else 'Unknown'
                self.df[col].fillna(fill_value, inplace=True)
                cleaning_report["actions"].append(
                    f"Filled {missing_count} missing values in '{col}' with '{fill_value}'"
                )
        
        cleaning_report["final_rows"] = len(self.df)
        cleaning_report["rows_removed"] = cleaning_report["original_rows"] - cleaning_report["final_rows"]
        
        return cleaning_report
    
    def get_column_info(self, column_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific column"""
        if self.df is None:
            self.load_data()
        
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found")
        
        col = self.df[column_name]
        
        info = {
            "name": column_name,
            "type": str(col.dtype),
            "unique_values": int(col.nunique()),
            "missing_values": int(col.isnull().sum()),
            "missing_percentage": float(col.isnull().sum() / len(col) * 100)
        }
        
        # Add statistics for numeric columns
        if np.issubdtype(col.dtype, np.number):
            info["statistics"] = {
                "min": float(col.min()),
                "max": float(col.max()),
                "mean": float(col.mean()),
                "median": float(col.median()),
                "std": float(col.std())
            }
        else:
            # Add top values for categorical columns
            top_values = col.value_counts().head(10)
            info["top_values"] = {str(k): int(v) for k, v in top_values.items()}
        
        return info