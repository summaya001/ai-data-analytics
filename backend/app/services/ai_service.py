import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        # Using mock mode since we don't have API key
        self.use_mock = True
        self.client = None
        print("⚠ Using mock AI responses (no API key required)")
    
    def analyze_data(self, data_summary: dict) -> str:
        """Generate insights from data summary"""
        return self._generate_mock_insights(data_summary)
    
    def _generate_mock_insights(self, data_summary: dict) -> str:
        """Generate realistic mock insights based on data summary"""
        rows = data_summary.get('rows', 0)
        columns = data_summary.get('columns', 0)
        column_names = data_summary.get('column_names', [])
        column_types = data_summary.get('column_types', {})
        statistics = data_summary.get('statistics', {})
        
        insights = []
        
        # Insight 1: Dataset Overview
        insights.append(
            f"**Dataset Overview**: This dataset contains {rows:,} rows and {columns} columns "
            f"({', '.join(column_names[:3])}{'...' if len(column_names) > 3 else ''}), "
            f"providing a {'comprehensive' if rows > 100 else 'focused'} view of the data."
        )
        
        # Insight 2: Numeric Analysis
        if statistics:
            numeric_cols = list(statistics.keys())
            if numeric_cols:
                col = numeric_cols[0]
                stats = statistics[col]
                mean_val = stats.get('mean', 0)
                min_val = stats.get('min', 0)
                max_val = stats.get('max', 0)
                range_val = max_val - min_val
                
                insights.append(
                    f"**{col} Distribution**: The {col.lower()} values range from {min_val:,.0f} to {max_val:,.0f} "
                    f"with an average of {mean_val:,.2f}, showing a spread of {range_val:,.0f}. "
                    f"This indicates {'moderate' if range_val / mean_val < 1 else 'significant'} variability."
                )
        
        # Insight 3: Data Types
        type_counts = {}
        for col_type in column_types.values():
            type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        if type_counts:
            type_summary = ", ".join([f"{count} {dtype}" for dtype, count in type_counts.items()])
            insights.append(
                f"**Data Structure**: The dataset includes {type_summary} columns, "
                f"suggesting a {'well-balanced' if len(type_counts) > 2 else 'focused'} mix of data types."
            )
        
        # Insight 4: Data Size Assessment
        if rows < 100:
            size_insight = "small but focused dataset, ideal for quick analysis and prototyping"
        elif rows < 1000:
            size_insight = "moderately-sized dataset that balances detail with manageability"
        else:
            size_insight = "substantial dataset providing robust statistical power for analysis"
        
        insights.append(
            f"**Data Volume**: With {rows:,} records, this is a {size_insight}."
        )
        
        # Insight 5: Additional numeric insight
        if len(statistics) > 1:
            cols = list(statistics.keys())[:2]
            insights.append(
                f"**Key Metrics**: The dataset includes quantitative measures for {' and '.join(cols)}, "
                f"enabling correlation analysis and trend identification."
            )
        else:
            insights.append(
                f"**Analysis Potential**: The combination of {columns} different attributes "
                f"allows for multi-dimensional analysis and pattern discovery."
            )
        
        # Add disclaimer
        disclaimer = "\n\n_Note: These are rule-based insights. For AI-powered analysis, add ANTHROPIC_API_KEY to .env file._"
        
        return "\n\n".join(insights) + disclaimer
