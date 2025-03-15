"""
Metrics utilities for NexusFlow.ai

This module provides utilities for tracking execution time, token usage,
and other performance metrics for the NexusFlow system.
"""

import time
import functools
import logging
import asyncio
from typing import Dict, Any, Optional, Union, Callable, TypeVar, cast
from datetime import datetime
import threading
import json
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Type variables for function decorators
F = TypeVar('F', bound=Callable[..., Any])
AsyncF = TypeVar('AsyncF', bound=Callable[..., Any])

class MetricsLogger:
    """
    Logger for system metrics
    
    This class provides methods for logging and aggregating metrics about
    system performance, including execution times, token usage, and other
    custom metrics.
    """
    
    def __init__(
        self,
        metrics_file: Optional[str] = None,
        log_to_console: bool = False,
        aggregate_interval: Optional[int] = None,
        metrics_dir: str = "metrics"
    ):
        """
        Initialize metrics logger
        
        Args:
            metrics_file: Path to metrics file (None for no file logging)
            log_to_console: Whether to log metrics to console
            aggregate_interval: Interval in seconds for aggregating metrics (None for no aggregation)
            metrics_dir: Directory for metrics files
        """
        self.metrics_file = metrics_file
        self.log_to_console = log_to_console
        self.aggregate_interval = aggregate_interval
        self.metrics_dir = metrics_dir
        
        # Create metrics directory if it doesn't exist
        if metrics_file and metrics_dir not in metrics_file:
            os.makedirs(metrics_dir, exist_ok=True)
        
        # Initialize storage for metrics
        self.metrics: Dict[str, Any] = {}
        self.metric_counts: Dict[str, int] = {}
        
        # Start aggregation thread if interval is specified
        if aggregate_interval:
            self._start_aggregation_thread()
    
    def _start_aggregation_thread(self) -> None:
        """Start a thread for periodic metrics aggregation"""
        def aggregate_periodically():
            while True:
                time.sleep(self.aggregate_interval)
                self.aggregate_and_save()
        
        thread = threading.Thread(target=aggregate_periodically, daemon=True)
        thread.start()
    
    def log_metric(self, metric_name: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a metric
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            metadata: Additional metadata about the metric
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Create metric entry
        metric_entry = {
            "timestamp": timestamp,
            "value": value,
            "metadata": metadata or {}
        }
        
        # Add to metrics storage
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(metric_entry)
        self.metric_counts[metric_name] = self.metric_counts.get(metric_name, 0) + 1
        
        # Log to console if requested
        if self.log_to_console:
            metadata_str = f", {metadata}" if metadata else ""
            logger.info(f"Metric {metric_name}: {value}{metadata_str}")
        
        # Save to file if available and not using aggregation
        if self.metrics_file and not self.aggregate_interval:
            self._append_to_file(metric_name, metric_entry)
    
    def _append_to_file(self, metric_name: str, metric_entry: Dict[str, Any]) -> None:
        """
        Append a metric entry to the metrics file
        
        Args:
            metric_name: Name of the metric
            metric_entry: Metric entry to append
        """
        try:
            with open(self.metrics_file, 'a') as f:
                entry = {
                    "metric": metric_name,
                    **metric_entry
                }
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to metrics file: {str(e)}")
    
    def aggregate_and_save(self) -> Dict[str, Any]:
        """
        Aggregate metrics and save to file
        
        Returns:
            Aggregated metrics
        """
        # Create aggregation timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Aggregate metrics
        aggregated_metrics = {
            "timestamp": timestamp,
            "metrics": {}
        }
        
        for metric_name, entries in self.metrics.items():
            # Skip metrics with no entries
            if not entries:
                continue
            
            # Extract values
            values = [entry["value"] for entry in entries if entry["value"] is not None]
            
            # Skip metrics with no valid values
            if not values:
                continue
            
            # Compute aggregates for numeric values
            try:
                numeric_values = [float(v) for v in values if isinstance(v, (int, float)) or isinstance(v, str) and v.replace('.', '', 1).isdigit()]
                
                if numeric_values:
                    aggregated_metrics["metrics"][metric_name] = {
                        "count": len(values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "mean": sum(numeric_values) / len(numeric_values),
                        "latest": values[-1]
                    }
                else:
                    # For non-numeric values, just log the count and latest value
                    aggregated_metrics["metrics"][metric_name] = {
                        "count": len(values),
                        "latest": values[-1]
                    }
            except Exception as e:
                logger.error(f"Error aggregating metric {metric_name}: {str(e)}")
                aggregated_metrics["metrics"][metric_name] = {
                    "count": len(values),
                    "error": str(e)
                }
        
        # Save to file if available
        if self.metrics_file:
            agg_file = self.metrics_file.replace('.json', '_aggregated.json')
            try:
                with open(agg_file, 'w') as f:
                    json.dump(aggregated_metrics, f, indent=2)
            except Exception as e:
                logger.error(f"Error writing aggregated metrics to file: {str(e)}")
        
        # Log aggregation to console
        if self.log_to_console:
            metric_summary = ", ".join([f"{name}: {data.get('count', 0)} entries" for name, data in aggregated_metrics["metrics"].items()])
            logger.info(f"Metrics aggregated: {metric_summary}")
        
        # Clear metrics after aggregation
        self.metrics = {}
        
        return aggregated_metrics
    
    def get_metrics(self, metric_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current metrics
        
        Args:
            metric_name: Name of specific metric to get (None for all)
            
        Returns:
            Current metrics
        """
        if metric_name:
            return {metric_name: self.metrics.get(metric_name, [])}
        else:
            return self.metrics

# Create global metrics logger
metrics_logger = MetricsLogger()

def track_execution_time(func_or_name: Union[Callable, str] = None, *, additional_info: Optional[Dict[str, Any]] = None) -> Callable:
    """
    Decorator to track the execution time of a function
    
    Can be used as a simple decorator or with a custom name:
    
    @track_execution_time
    def my_function():
        pass
        
    @track_execution_time("custom_name")
    def my_function():
        pass
    
    Args:
        func_or_name: Function to decorate or custom name for the metric
        additional_info: Additional information to include with the metric
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        # For normal functions
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get metric name (function name or custom name)
            metric_name = func.__name__ if isinstance(func_or_name, Callable) else func_or_name
            metric_name = f"execution_time.{metric_name}"
            
            # Collect additional info
            metadata = {
                "function": func.__name__,
                "module": func.__module__
            }
            if additional_info:
                metadata.update(additional_info)
            
            # Measure execution time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                metrics_logger.log_metric(metric_name, execution_time, metadata)
        
        # For async functions
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get metric name (function name or custom name)
            metric_name = func.__name__ if isinstance(func_or_name, Callable) else func_or_name
            metric_name = f"execution_time.{metric_name}"
            
            # Collect additional info
            metadata = {
                "function": func.__name__,
                "module": func.__module__,
                "async": True
            }
            if additional_info:
                metadata.update(additional_info)
            
            # Measure execution time
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                metrics_logger.log_metric(metric_name, execution_time, metadata)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)
    
    # Handle both @track_execution_time and @track_execution_time("name") forms
    if isinstance(func_or_name, Callable):
        return decorator(func_or_name)
    else:
        return decorator

def track_token_usage(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track token usage for a model call
    
    Args:
        model_name: Name of the model
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        metadata: Additional metadata about the model call
    """
    # Create base metric data
    base_metadata = {
        "model": model_name,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add additional metadata if provided
    if metadata:
        base_metadata.update(metadata)
    
    # Log prompt tokens
    metrics_logger.log_metric(
        f"token_usage.{model_name}.prompt",
        prompt_tokens,
        base_metadata
    )
    
    # Log completion tokens
    metrics_logger.log_metric(
        f"token_usage.{model_name}.completion",
        completion_tokens,
        base_metadata
    )
    
    # Log total tokens
    metrics_logger.log_metric(
        f"token_usage.{model_name}.total",
        prompt_tokens + completion_tokens,
        base_metadata
    )

@contextmanager
def timer(name: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Context manager for timing code blocks
    
    Usage:
    with timer("my_operation"):
        # code to time
    
    Args:
        name: Name for the timing metric
        metadata: Additional metadata about the operation
    """
    start_time = time.time()
    yield
    execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    metrics_logger.log_metric(f"timer.{name}", execution_time, metadata)

async def async_timer(name: str, coro, metadata: Optional[Dict[str, Any]] = None):
    """
    Async context manager for timing async code blocks
    
    Usage:
    result = await async_timer("my_operation", some_async_function())
    
    Args:
        name: Name for the timing metric
        coro: Coroutine to time
        metadata: Additional metadata about the operation
        
    Returns:
        Result of the coroutine
    """
    start_time = time.time()
    try:
        result = await coro
        return result
    finally:
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        metrics_logger.log_metric(f"async_timer.{name}", execution_time, metadata)
