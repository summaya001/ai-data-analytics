import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any
import numpy as np

class VisualizationService:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def recommend_charts(self) -> List[Dict[str, Any]]:
        """
        Analyze data and recommend appropriate chart types for each column
        """
        recommendations = []
        
        # Find numeric columns for values
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        # For categorical columns paired with numeric values
        for cat_col in categorical_cols:
            unique_count = self.df[cat_col].nunique()
            
            if unique_count < 15:
                # Find the best numeric column to sum (usually Sales, Revenue, Amount, etc.)
                value_col = None
                for num_col in numeric_cols:
                    if any(keyword in num_col.lower() for keyword in ['sales', 'revenue', 'amount', 'price', 'total', 'value']):
                        value_col = num_col
                        break
                
                if not value_col and len(numeric_cols) > 0:
                    value_col = numeric_cols[0]  # Use first numeric column
                
                if value_col:
                    # Bar chart with summed values
                    recommendations.append({
                        "column": cat_col,
                        "value_column": value_col,
                        "chart_type": "bar",
                        "reason": f"Shows total {value_col} for each {cat_col}",
                        "priority": "high"
                    })
                    
                    # Pie chart with summed values
                    if unique_count <= 8:
                        recommendations.append({
                            "column": cat_col,
                            "value_column": value_col,
                            "chart_type": "pie",
                            "reason": f"Shows proportion of {value_col} by {cat_col}",
                            "priority": "high"
                        })
        
        # Box plots for numeric distributions
        for col in numeric_cols:
            recommendations.append({
                "column": col,
                "chart_type": "box",
                "reason": f"Shows statistical distribution of {col}",
                "priority": "medium"
            })
        
        return recommendations
    
    def create_bar_chart(self, column: str, value_column: str = None, top_n: int = 10) -> Dict:
        """Create a bar chart for a column"""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        # Check if we should sum values instead of count
        if value_column and value_column in self.df.columns:
            # Sum the values for each category
            grouped_data = self.df.groupby(column)[value_column].sum().sort_values(ascending=False).head(top_n)
            y_label = f"Total {value_column}"
            title = f"Total {value_column} by {column}"
            print(f"[DEBUG] Bar chart: Summing {value_column} by {column}")
            print(f"[DEBUG] Data: {grouped_data.to_dict()}")
        else:
            # Count occurrences (original behavior)
            grouped_data = self.df[column].value_counts().head(top_n)
            y_label = "Count"
            title = f"Count by {column}"
            print(f"[DEBUG] Bar chart: Counting {column}")
        
        fig = go.Figure(data=[
            go.Bar(
                x=grouped_data.index.tolist(),
                y=grouped_data.values.tolist(),
                marker_color='steelblue',
                text=grouped_data.values.tolist(),
                textposition='outside',
                texttemplate='%{text:,.0f}',
                hovertemplate='<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=column,
            yaxis_title=y_label,
            template="plotly_white",
            height=450
        )
        
        return {
            "type": "bar",
            "column": column,
            "value_column": value_column,
            "data": fig.to_json()
        }
    
    def create_pie_chart(self, column: str, value_column: str = None, top_n: int = 8) -> Dict:
        """Create a pie chart for a column"""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        # Check if we should sum values instead of count
        if value_column and value_column in self.df.columns:
            # Sum the values for each category
            grouped_data = self.df.groupby(column)[value_column].sum().sort_values(ascending=False).head(top_n)
            title = f"Total {value_column} by {column}"
            print(f"[DEBUG] Pie chart: Summing {value_column} by {column}")
            print(f"[DEBUG] Data: {grouped_data.to_dict()}")
        else:
            # Count occurrences (original behavior)
            grouped_data = self.df[column].value_counts().head(top_n)
            title = f"Distribution of {column}"
            print(f"[DEBUG] Pie chart: Counting {column}")
        
        fig = go.Figure(data=[
            go.Pie(
                labels=grouped_data.index.tolist(),
                values=grouped_data.values.tolist(),
                hole=0.3,
                textinfo='label+value+percent',
                texttemplate='<b>%{label}</b><br>%{value:,.0f}<br>(%{percent})',
                textfont=dict(size=12),
                hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=450,
            showlegend=False
        )
        
        return {
            "type": "pie",
            "column": column,
            "value_column": value_column,
            "data": fig.to_json()
        }
    
    def create_box_plot(self, column: str) -> Dict:
        """Create a box plot for numeric column (shows quartiles and outliers)"""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")
        
        # Check if column is numeric
        if self.df[column].dtype not in ['int64', 'float64']:
            raise ValueError(f"Column '{column}' must be numeric (int or float). Current type: {self.df[column].dtype}")
        
        # Remove any NaN values and convert to list
        data = self.df[column].dropna().tolist()
        
        if len(data) == 0:
            raise ValueError(f"Column '{column}' has no valid numeric data")
        
        print(f"[DEBUG] Box plot for {column}: {len(data)} values, range {min(data)}-{max(data)}")
        
        # Create box plot with explicit trace
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data,
            name=column,
            marker=dict(color='steelblue'),
            boxmean='sd',
            boxpoints='outliers',
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Box Plot of {column}",
                font=dict(size=16)
            ),
            yaxis=dict(
                title=column,
                zeroline=True,
                gridcolor='lightgray'
            ),
            xaxis=dict(
                showticklabels=False
            ),
            template="plotly_white",
            height=450,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        result = {
            "type": "box",
            "column": column,
            "data": fig.to_json()
        }
        
        print(f"[DEBUG] Box plot JSON length: {len(result['data'])}")
        
        return result
    
    def create_grouped_bar_chart(self, category_column: str, value_column: str, group_column: str) -> Dict:
        """Create a grouped bar chart (compare categories side-by-side)"""
        if category_column not in self.df.columns or value_column not in self.df.columns or group_column not in self.df.columns:
            raise ValueError(f"One or more columns not found")
        
        # Pivot data for grouped bar chart
        pivot_data = self.df.pivot_table(
            values=value_column,
            index=category_column,
            columns=group_column,
            aggfunc='sum',
            fill_value=0
        )
        
        fig = go.Figure()
        
        for group in pivot_data.columns:
            fig.add_trace(go.Bar(
                name=str(group),
                x=pivot_data.index.tolist(),
                y=pivot_data[group].tolist()
            ))
        
        fig.update_layout(
            title=f"{value_column} by {category_column} (grouped by {group_column})",
            xaxis_title=category_column,
            yaxis_title=value_column,
            template="plotly_white",
            height=400,
            barmode='group'
        )
        
        return {
            "type": "grouped_bar",
            "columns": [category_column, value_column, group_column],
            "data": fig.to_json()
        }
    
    def generate_all_recommended_charts(self) -> List[Dict]:
        """Generate all recommended charts automatically"""
        recommendations = self.recommend_charts()
        charts = []
        
        for rec in recommendations:
            try:
                chart_type = rec["chart_type"]
                
                if chart_type == "bar":
                    value_col = rec.get("value_column")
                    chart = self.create_bar_chart(rec["column"], value_column=value_col)
                    chart["recommendation"] = rec
                    charts.append(chart)
                
                elif chart_type == "pie":
                    value_col = rec.get("value_column")
                    chart = self.create_pie_chart(rec["column"], value_column=value_col)
                    chart["recommendation"] = rec
                    charts.append(chart)
                
                elif chart_type == "box":
                    chart = self.create_box_plot(rec["column"])
                    chart["recommendation"] = rec
                    charts.append(chart)
            
            except Exception as e:
                print(f"Error creating {chart_type} chart: {e}")
                continue
        
        return charts
    
    def create_area_chart(self, x_column: str, y_column: str) -> Dict:
        """Create an area chart (filled line chart)."""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError("One or both columns not found")

        # Sort by x column
        df_sorted = self.df.sort_values(by=x_column)

        fig = go.Figure(data=[
            go.Scatter(
                x=df_sorted[x_column],
                y=df_sorted[y_column],
                mode='lines',
                fill='tozeroy',
                line=dict(color='#667eea', width=2),
                fillcolor='rgba(102, 126, 234, 0.3)'
            )
        ])

        fig.update_layout(
            title=f"{y_column} over {x_column} (Area Chart)",
            xaxis_title=x_column,
            yaxis_title=y_column,
            template="plotly_white",
            height=400,
            showlegend=False
        )

        return {
            "type": "area",
            "columns": [x_column, y_column],
            "data": fig.to_json()
        }

    def create_stacked_bar_chart(self, x_column: str, y_column: str, stack_column: str) -> Dict:
        """Create a stacked bar chart."""
        if (
            x_column not in self.df.columns or
            y_column not in self.df.columns or
            stack_column not in self.df.columns
        ):
            raise ValueError("One or more columns not found")

        # Pivot data
        pivot_data = self.df.pivot_table(
            values=y_column,
            index=x_column,
            columns=stack_column,
            aggfunc='sum',
            fill_value=0
        )

        fig = go.Figure()

        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']

        for i, stack_val in enumerate(pivot_data.columns):
            fig.add_trace(go.Bar(
                name=str(stack_val),
                x=pivot_data.index.tolist(),
                y=pivot_data[stack_val].tolist(),
                marker_color=colors[i % len(colors)]
            ))

        fig.update_layout(
            title=f"{y_column} by {x_column} (Stacked by {stack_column})",
            xaxis_title=x_column,
            yaxis_title=y_column,
            template="plotly_white",
            height=450,
            barmode='stack',
            legend=dict(title=stack_column)
        )

        return {
            "type": "stacked_bar",
            "columns": [x_column, y_column, stack_column],
            "data": fig.to_json()
        }


    def create_violin_plot(self, column: str, group_by: str = None) -> Dict:
        """Create a violin plot (distribution shape)."""
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")

        # Check if column is numeric
        if self.df[column].dtype not in ['int64', 'float64']:
            raise ValueError(f"Column '{column}' must be numeric for violin plot")

        fig = go.Figure()

        if group_by and group_by in self.df.columns:
            # Grouped violin plot
            for group in self.df[group_by].unique():
                group_data = self.df[self.df[group_by] == group][column].dropna().tolist()
                fig.add_trace(go.Violin(
                    y=group_data,
                    name=str(group),
                    box_visible=True,
                    meanline_visible=True
                ))
            title = f"Distribution of {column} by {group_by}"
        else:
            # Single violin plot
            data = self.df[column].dropna().tolist()
            fig.add_trace(go.Violin(
                y=data,
                name=column,
                box_visible=True,
                meanline_visible=True,
                fillcolor='lightblue',
                line_color='steelblue'
             ))
            title = f"Distribution of {column} (Violin Plot)"

        fig.update_layout(
            title=title,
            yaxis_title=column,
            template="plotly_white",
            height=450,
            showlegend=bool(group_by)
        )

        return {
            "type": "violin",
            "column": column,
            "group_by": group_by,
            "data": fig.to_json()
        }

    def create_line_chart(self, x_column: str, y_column: str) -> Dict:
        """Create a line chart for trend analysis"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError("One or both columns not found")
        
        # Sort by x column for proper line drawing
        df_sorted = self.df.sort_values(by=x_column)
        
        fig = go.Figure(data=[
            go.Scatter(
                x=df_sorted[x_column],
                y=df_sorted[y_column],
                mode='lines+markers',
                line=dict(color='steelblue', width=2),
                marker=dict(size=6)
            )
        ])
        
        fig.update_layout(
            title=f'{y_column} over {x_column}',
            xaxis_title=x_column,
            yaxis_title=y_column,
            template="plotly_white",
            showlegend=False,
            height=400
        )
        
        return {
            "type": "line",
            "columns": [x_column, y_column],
            "data": fig.to_json()
        }