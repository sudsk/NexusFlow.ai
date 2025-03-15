"""
Data Analysis Tool for NexusFlow.ai

This module provides a tool for analyzing data and generating insights.
"""

import logging
import asyncio
import io
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import base64
import tempfile
import os

from .registry import ToolDefinition, ToolResult, tool_registry

logger = logging.getLogger(__name__)

class DataAnalysisTool:
    """Tool for analyzing data and generating insights"""
    
    def __init__(
        self,
        max_data_size: int = 10 * 1024 * 1024,  # 10MB
        timeout: int = 30,
        supported_formats: Optional[List[str]] = None
    ):
        """
        Initialize a data analysis tool
        
        Args:
            max_data_size: Maximum data size in bytes
            timeout: Maximum execution time in seconds
            supported_formats: List of supported data formats
        """
        self.max_data_size = max_data_size
        self.timeout = timeout
        self.supported_formats = supported_formats or ["csv", "json", "tsv", "excel", "parquet"]
        
        # Try to import analysis libraries
        self.has_pandas = False
        self.has_numpy = False
        self.has_matplotlib = False
        self.has_seaborn = False
        
        try:
            import pandas
            self.has_pandas = True
        except ImportError:
            logger.warning("Pandas not installed. Some data analysis features will be limited.")
        
        try:
            import numpy
            self.has_numpy = True
        except ImportError:
            logger.warning("NumPy not installed. Some data analysis features will be limited.")
        
        try:
            import matplotlib
            self.has_matplotlib = True
        except ImportError:
            logger.warning("Matplotlib not installed. Visualization features will be limited.")
        
        try:
            import seaborn
            self.has_seaborn = True
        except ImportError:
            logger.warning("Seaborn not installed. Advanced visualization features will be limited.")
        
        # Register the tool
        self._register_tool()
    
    def _register_tool(self):
        """Register the data analysis tool with the registry"""
        tool_def = ToolDefinition(
            name="data_analysis",
            description="Analyze data and generate insights",
            parameters={
                "data": {
                    "type": "string",
                    "description": "Data to analyze (CSV, JSON, or base64-encoded data)"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of analysis to perform",
                    "required": False,
                    "default": "descriptive",
                    "enum": [
                        "descriptive", "statistical", "correlation", 
                        "time_series", "clustering", "regression"
                    ]
                },
                "format": {
                    "type": "string",
                    "description": "Format of the data",
                    "required": False,
                    "default": "auto",
                    "enum": ["auto", "csv", "json", "tsv", "excel", "parquet"]
                },
                "columns": {
                    "type": "array",
                    "description": "Columns to include in the analysis (defaults to all)",
                    "required": False
                },
                "include_charts": {
                    "type": "boolean",
                    "description": "Whether to include visualizations",
                    "required": False,
                    "default": True
                }
            },
            handler=self.analyze_data,
            is_async=True,
            category="analysis",
            tags=["data", "analysis", "statistics", "visualization"]
        )
        
        tool_registry.register_tool(tool_def)
    
    async def analyze_data(
        self,
        data: str,
        analysis_type: str = "descriptive",
        format: str = "auto",
        columns: Optional[List[str]] = None,
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze data and generate insights
        
        Args:
            data: Data to analyze (CSV, JSON, or base64-encoded data)
            analysis_type: Type of analysis to perform
            format: Format of the data
            columns: Columns to include in the analysis
            include_charts: Whether to include visualizations
            
        Returns:
            Analysis results
        """
        # Check prerequisites
        if not self.has_pandas:
            return {
                "error": "Pandas is required for data analysis but is not installed",
                "details": "Please install pandas: pip install pandas"
            }
        
        # Import analysis libraries
        import pandas as pd
        import numpy as np
        
        # Prepare result container
        result = {
            "analysis_type": analysis_type,
            "summary": {},
            "details": {},
            "charts": [],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "tool_version": "0.1.0",
                "format": format
            }
        }
        
        try:
            # Measure execution time
            start_time = time.time()
            
            # Parse data
            df = await self._parse_data(data, format)
            
            # Validate data
            if df is None or df.empty:
                return {
                    "error": "Invalid or empty data",
                    "details": "The provided data could not be parsed or is empty"
                }
            
            # Filter columns if specified
            if columns:
                # Find intersection of requested columns and available columns
                valid_columns = [col for col in columns if col in df.columns]
                if not valid_columns:
                    return {
                        "error": "No valid columns specified",
                        "details": f"Available columns: {', '.join(df.columns)}"
                    }
                df = df[valid_columns]
            
            # Perform analysis based on type
            analysis_task = asyncio.create_task(
                self._execute_analysis(df, analysis_type, include_charts)
            )
            
            # Wait for analysis with timeout
            try:
                analysis_result = await asyncio.wait_for(analysis_task, timeout=self.timeout)
                execution_time = time.time() - start_time
                
                # Update result with analysis
                result.update(analysis_result)
                result["metadata"]["execution_time"] = execution_time
                
                return result
                
            except asyncio.TimeoutError:
                # Cancel the task if it's still running
                analysis_task.cancel()
                try:
                    await analysis_task
                except asyncio.CancelledError:
                    pass
                
                return {
                    "error": f"Analysis timed out after {self.timeout} seconds",
                    "metadata": {
                        "execution_time": self.timeout,
                        "data_shape": f"{df.shape[0]} rows, {df.shape[1]} columns"
                    }
                }
                
        except Exception as e:
            logger.exception(f"Error analyzing data: {str(e)}")
            return {
                "error": f"Error analyzing data: {str(e)}",
                "details": str(e),
                "metadata": {
                    "execution_time": time.time() - start_time
                }
            }
    
    async def _parse_data(self, data: str, format: str) -> Optional['pandas.DataFrame']:
        """
        Parse data into a pandas DataFrame
        
        Args:
            data: Data to parse
            format: Format of the data
            
        Returns:
            Parsed DataFrame or None if parsing failed
        """
        import pandas as pd
        
        try:
            # Check if data is a base64-encoded string
            if data.startswith('data:'):
                # Extract format and data from data URI
                parts = data.split(',', 1)
                if len(parts) > 1:
                    header = parts[0]
                    data_str = parts[1]
                    
                    # Extract format from header if available
                    if format == "auto" and ";" in header:
                        mime_type = header.split(';')[0].split(':')[1]
                        if "csv" in mime_type:
                            format = "csv"
                        elif "json" in mime_type:
                            format = "json"
                        elif "excel" in mime_type:
                            format = "excel"
                    
                    # Decode base64 data
                    try:
                        decoded_data = base64.b64decode(data_str)
                        
                        # Save to temporary file for pandas to read
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            temp_path = temp_file.name
                            temp_file.write(decoded_data)
                        
                        try:
                            # Parse based on format
                            if format == "csv" or (format == "auto" and temp_path.endswith('.csv')):
                                return pd.read_csv(temp_path)
                            elif format == "json" or (format == "auto" and temp_path.endswith('.json')):
                                return pd.read_json(temp_path)
                            elif format == "excel" or (format == "auto" and 
                                    (temp_path.endswith('.xlsx') or temp_path.endswith('.xls'))):
                                return pd.read_excel(temp_path)
                            elif format == "parquet" or (format == "auto" and temp_path.endswith('.parquet')):
                                return pd.read_parquet(temp_path)
                            else:
                                # Default to CSV
                                return pd.read_csv(temp_path)
                        finally:
                            # Clean up temporary file
                            os.unlink(temp_path)
                    except:
                        # If decoding fails, treat as regular data
                        pass
            
            # Try to parse data based on format
            if format == "csv" or format == "auto":
                return pd.read_csv(io.StringIO(data))
            elif format == "json":
                return pd.read_json(io.StringIO(data))
            elif format == "tsv":
                return pd.read_csv(io.StringIO(data), sep='\t')
            elif format == "excel":
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                    temp_path = temp_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(data.encode())
                    df = pd.read_excel(temp_path)
                    os.unlink(temp_path)
                    return df
            elif format == "parquet":
                with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as temp_file:
                    temp_path = temp_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(data.encode())
                    df = pd.read_parquet(temp_path)
                    os.unlink(temp_path)
                    return df
            else:
                # Try common formats
                try:
                    return pd.read_csv(io.StringIO(data))
                except:
                    try:
                        return pd.read_json(io.StringIO(data))
                    except:
                        raise ValueError(f"Could not parse data in format: {format}")
            
        except Exception as e:
            logger.exception(f"Error parsing data: {str(e)}")
            return None

async def _execute_analysis(
        self, 
        df: 'pandas.DataFrame',
        analysis_type: str,
        include_charts: bool
    ) -> Dict[str, Any]:
        """
        Execute analysis on a DataFrame
        
        Args:
            df: DataFrame to analyze
            analysis_type: Type of analysis to perform
            include_charts: Whether to include visualizations
            
        Returns:
            Analysis results
        """
        # Import visualization libraries if needed
        if include_charts and self.has_matplotlib:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            if self.has_seaborn:
                import seaborn as sns
                sns.set(style="whitegrid")
        
        # Common metadata for all analysis types
        result = {
            "summary": {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": df.isna().sum().to_dict()
            },
            "details": {},
            "charts": []
        }
        
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # Add data types to result
        result["summary"]["numeric_columns"] = numeric_cols
        result["summary"]["categorical_columns"] = categorical_cols
        
        # Execute analysis based on type
        if analysis_type == "descriptive":
            # Basic descriptive statistics
            if numeric_cols:
                result["details"]["statistics"] = df[numeric_cols].describe().to_dict()
            
            # Value counts for categorical columns (limited to top values)
            if categorical_cols:
                result["details"]["categories"] = {}
                for col in categorical_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    result["details"]["categories"][col] = value_counts
            
            # Generate charts if requested
            if include_charts and numeric_cols and self.has_matplotlib:
                # Histograms for numeric columns
                for col in numeric_cols[:5]:  # Limit to first 5 columns
                    try:
                        plt.figure(figsize=(8, 4))
                        plt.hist(df[col].dropna(), bins=20, alpha=0.7)
                        plt.title(f"Distribution of {col}")
                        plt.xlabel(col)
                        plt.ylabel("Frequency")
                        plt.grid(True, alpha=0.3)
                        
                        # Save to buffer
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        plt.close()
                        
                        # Convert to base64
                        buf.seek(0)
                        img_str = base64.b64encode(buf.read()).decode('utf-8')
                        
                        # Add to charts
                        result["charts"].append({
                            "title": f"Distribution of {col}",
                            "type": "histogram",
                            "data": f"data:image/png;base64,{img_str}"
                        })
                    except Exception as e:
                        logger.warning(f"Error generating histogram for {col}: {str(e)}")
                
                # Generate boxplot for numeric columns
                try:
                    plt.figure(figsize=(10, 6))
                    df[numeric_cols[:5]].boxplot()
                    plt.title("Boxplot of Numeric Features")
                    plt.grid(False)
                    plt.tight_layout()
                    
                    # Save to buffer
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    plt.close()
                    
                    # Convert to base64
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    
                    # Add to charts
                    result["charts"].append({
                        "title": "Boxplot of Numeric Features",
                        "type": "boxplot",
                        "data": f"data:image/png;base64,{img_str}"
                    })
                except Exception as e:
                    logger.warning(f"Error generating boxplot: {str(e)}")
                    
        elif analysis_type == "correlation":
            # Correlation analysis
            if len(numeric_cols) > 1:
                # Compute correlation matrix
                corr_matrix = df[numeric_cols].corr().round(3).to_dict()
                result["details"]["correlation_matrix"] = corr_matrix
                
                # Top correlations
                corr_df = df[numeric_cols].corr().unstack().sort_values(kind="quicksort", ascending=False)
                corr_df = corr_df[corr_df != 1.0]  # Remove self-correlations
                top_correlations = []
                seen = set()
                
                for idx, val in corr_df.items():
                    # Get variable pair and ensure uniqueness
                    var1, var2 = idx
                    if var1 == var2 or frozenset([var1, var2]) in seen:
                        continue
                    seen.add(frozenset([var1, var2]))
                    
                    top_correlations.append({
                        "variables": [var1, var2],
                        "correlation": val
                    })
                    
                    if len(top_correlations) >= 10:  # Limit to top 10
                        break
                
                result["details"]["top_correlations"] = top_correlations
                
                # Generate charts if requested
                if include_charts and self.has_matplotlib and self.has_seaborn:
                    try:
                        import seaborn as sns
                        # Correlation heatmap
                        plt.figure(figsize=(10, 8))
                        corr = df[numeric_cols].corr()
                        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
                        plt.title("Correlation Matrix")
                        plt.tight_layout()
                        
                        # Save to buffer
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        plt.close()
                        
                        # Convert to base64
                        buf.seek(0)
                        img_str = base64.b64encode(buf.read()).decode('utf-8')
                        
                        # Add to charts
                        result["charts"].append({
                            "title": "Correlation Matrix",
                            "type": "heatmap",
                            "data": f"data:image/png;base64,{img_str}"
                        })
                    except Exception as e:
                        logger.warning(f"Error generating correlation heatmap: {str(e)}")
            else:
                result["error"] = "Correlation analysis requires at least 2 numeric columns"
                
        elif analysis_type == "clustering":
            # Clustering analysis
            if len(numeric_cols) < 2:
                result["error"] = "Clustering requires at least 2 numeric columns"
            else:
                try:
                    from sklearn.cluster import KMeans
                    from sklearn.preprocessing import StandardScaler
                    
                    # Prepare data
                    cluster_data = df[numeric_cols].copy()
                    cluster_data = cluster_data.fillna(cluster_data.mean())
                    
                    # Standardize the data
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(cluster_data)
                    
                    # Determine optimal k (simplified elbow method)
                    k_range = range(2, min(10, len(df) // 5 + 1))
                    inertias = []
                    
                    for k in k_range:
                        kmeans = KMeans(n_clusters=k, random_state=42)
                        kmeans.fit(scaled_data)
                        inertias.append(kmeans.inertia_)
                    
                    # Find the "elbow" point
                    optimal_k = 2  # Default
                    for i in range(1, len(inertias) - 1):
                        prev_diff = inertias[i-1] - inertias[i]
                        next_diff = inertias[i] - inertias[i+1]
                        if prev_diff > 2 * next_diff:
                            optimal_k = k_range[i]
                            break
                    
                    # Perform clustering with optimal k
                    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
                    clusters = kmeans.fit_predict(scaled_data)
                    
                    # Add clusters to result
                    result["details"]["clusters"] = {
                        "method": "kmeans",
                        "num_clusters": optimal_k,
                        "inertia": float(kmeans.inertia_),
                        "cluster_sizes": {str(i): int((clusters == i).sum()) for i in range(optimal_k)}
                    }
                    
                    # Generate charts if requested
                    if include_charts and self.has_matplotlib:
                        # Plot the elbow curve
                        plt.figure(figsize=(8, 5))
                        plt.plot(list(k_range), inertias, 'bo-')
                        plt.xlabel('Number of Clusters')
                        plt.ylabel('Inertia')
                        plt.title('Elbow Method for Optimal k')
                        plt.grid(True, alpha=0.3)
                        plt.plot(optimal_k, inertias[list(k_range).index(optimal_k)], 'ro')
                        
                        # Save to buffer
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        plt.close()
                        
                        # Convert to base64
                        buf.seek(0)
                        img_str = base64.b64encode(buf.read()).decode('utf-8')
                        
                        # Add to charts
                        result["charts"].append({
                            "title": "Elbow Method for Optimal k",
                            "type": "line",
                            "data": f"data:image/png;base64,{img_str}"
                        })
                        
                        # Scatter plot of clusters (first 2 features)
                        if len(numeric_cols) >= 2:
                            plt.figure(figsize=(8, 6))
                            for i in range(optimal_k):
                                plt.scatter(
                                    df.loc[clusters == i, numeric_cols[0]], 
                                    df.loc[clusters == i, numeric_cols[1]], 
                                    label=f'Cluster {i}',
                                    alpha=0.7
                                )
                            plt.scatter(
                                kmeans.cluster_centers_[:, 0],
                                kmeans.cluster_centers_[:, 1],
                                s=100, c='black', marker='x', label='Centroids'
                            )
                            plt.title(f'K-means Clustering (k={optimal_k})')
                            plt.xlabel(numeric_cols[0])
                            plt.ylabel(numeric_cols[1])
                            plt.legend()
                            plt.grid(True, alpha=0.3)
                            
                            # Save to buffer
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            plt.close()
                            
                            # Convert to base64
                            buf.seek(0)
                            img_str = base64.b64encode(buf.read()).decode('utf-8')
                            
                            # Add to charts
                            result["charts"].append({
                                "title": "K-means Clustering",
                                "type": "scatter",
                                "data": f"data:image/png;base64,{img_str}"
                            })
                except Exception as e:
                    logger.warning(f"Error in clustering analysis: {str(e)}")
                    result["error"] = f"Clustering analysis failed: {str(e)}"
                    
        elif analysis_type == "regression":
            # Simple regression analysis
            if len(numeric_cols) < 2:
                result["error"] = "Regression analysis requires at least 2 numeric columns"
            else:
                try:
                    from sklearn.linear_model import LinearRegression
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import r2_score, mean_squared_error
                    
                    # Use the first numeric column as target by default
                    target_col = numeric_cols[0]
                    feature_cols = numeric_cols[1:]
                    
                    if not feature_cols:
                        result["error"] = "Regression requires at least 2 numeric columns"
                    else:
                        # Prepare data
                        X = df[feature_cols].fillna(df[feature_cols].mean())
                        y = df[target_col].fillna(df[target_col].mean())
                        
                        # Split data
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=0.3, random_state=42
                        )
                        
                        # Train model
                        model = LinearRegression()
                        model.fit(X_train, y_train)
                        
                        # Make predictions
                        y_pred = model.predict(X_test)
                        
                        # Evaluate model
                        r2 = r2_score(y_test, y_pred)
                        mse = mean_squared_error(y_test, y_pred)
                        
                        # Add regression results
                        result["details"]["regression"] = {
                            "target": target_col,
                            "features": feature_cols,
                            "coefficients": {feature: float(coef) for feature, coef in zip(feature_cols, model.coef_)},
                            "intercept": float(model.intercept_),
                            "r2_score": float(r2),
                            "mean_squared_error": float(mse)
                        }
                        
                        # Generate charts if requested
                        if include_charts and self.has_matplotlib:
                            # Actual vs Predicted
                            plt.figure(figsize=(8, 6))
                            plt.scatter(y_test, y_pred, alpha=0.5)
                            plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
                            plt.xlabel(f'Actual {target_col}')
                            plt.ylabel(f'Predicted {target_col}')
                            plt.title(f'Actual vs Predicted {target_col}')
                            plt.grid(True, alpha=0.3)
                            
                            # Save to buffer
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            plt.close()
                            
                            # Convert to base64
                            buf.seek(0)
                            img_str = base64.b64encode(buf.read()).decode('utf-8')
                            
                            # Add to charts
                            result["charts"].append({
                                "title": f"Actual vs Predicted {target_col}",
                                "type": "scatter",
                                "data": f"data:image/png;base64,{img_str}"
                            })
                            
                            # Feature Importance
                            plt.figure(figsize=(10, 6))
                            coefficients = model.coef_
                            features = feature_cols
                            
                            # Sort by absolute value of coefficient
                            sorted_idx = abs(coefficients).argsort()
                            plt.barh(
                                [features[i] for i in sorted_idx], 
                                [coefficients[i] for i in sorted_idx]
                            )
                            plt.xlabel('Coefficient')
                            plt.title('Feature Importance')
                            plt.grid(True, alpha=0.3)
                            
                            # Save to buffer
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            plt.close()
                            
                            # Convert to base64
                            buf.seek(0)
                            img_str = base64.b64encode(buf.read()).decode('utf-8')
                            
                            # Add to charts
                            result["charts"].append({
                                "title": "Feature Importance",
                                "type": "bar",
                                "data": f"data:image/png;base64,{img_str}"
                            })
                except Exception as e:
                    logger.warning(f"Error in regression analysis: {str(e)}")
                    result["error"] = f"Regression analysis failed: {str(e)}"
        
        else:
            # Default case for unsupported analysis types
            result["warning"] = f"Unknown analysis type: {analysis_type}. Performing descriptive analysis instead."
            # Perform basic descriptive analysis
            if numeric_cols:
                result["details"]["statistics"] = df[numeric_cols].describe().to_dict()
        
        return result

# Create a global instance
data_analysis_tool = DataAnalysisTool()

# Export the tool
__all__ = ["DataAnalysisTool", "data_analysis_tool"]
