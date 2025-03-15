"""
Utility functions for NexusFlow.ai

This package contains utility functions for the NexusFlow system:
- Logging: Customized logging setup
- Metrics: Performance tracking utilities
- Visualization: Flow visualization utilities
"""

# Import logging utilities
from nexusflow.utils.logging import setup_logging, get_logger, JsonFormatter, StructuredLogAdapter, get_structured_logger

# Import metrics utilities
from nexusflow.utils.metrics import (
    track_execution_time, 
    track_token_usage, 
    MetricsLogger, 
    metrics_logger,
    timer,
    async_timer
)

# Import visualization utilities
try:
    from nexusflow.utils.visualization import (
        FlowVisualizer,
        visualize_flow,
        visualize_execution,
        visualize_agent_graph,
        export_flow_image
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    # Create stub functions if visualization packages are not available
    VISUALIZATION_AVAILABLE = False
    
    def _visualization_not_available(*args, **kwargs):
        import logging
        logging.warning("Visualization packages not installed. Install networkx and matplotlib.")
        return None
    
    # Create stub class
    class FlowVisualizer:
        def __init__(self, *args, **kwargs):
            import logging
            logging.warning("Visualization packages not installed. Install networkx and matplotlib.")
        
        def __getattr__(self, name):
            return _visualization_not_available
    
    # Create stub functions
    visualize_flow = _visualization_not_available
    visualize_execution = _visualization_not_available
    visualize_agent_graph = _visualization_not_available
    export_flow_image = _visualization_not_available

# Create default flow visualizer
if VISUALIZATION_AVAILABLE:
    flow_visualizer = FlowVisualizer()
    
    # Create convenience functions that use the default visualizer
    def visualize_flow(flow_data, **kwargs):
        return flow_visualizer.visualize_flow(flow_data, **kwargs)
    
    def visualize_execution(execution_data, flow_data=None, **kwargs):
        return flow_visualizer.visualize_execution(execution_data, flow_data, **kwargs)
    
    def visualize_agent_graph(agents, **kwargs):
        return flow_visualizer.visualize_agent_graph(agents, **kwargs)
    
    def export_flow_image(flow_data, **kwargs):
        return flow_visualizer.export_flow_image(flow_data, **kwargs)
    
    def visualize_execution_metrics(execution_data, **kwargs):
        return flow_visualizer.visualize_execution_metrics(execution_data, **kwargs)

__all__ = [
    # Logging utilities
    'setup_logging',
    'get_logger',
    'JsonFormatter',
    'StructuredLogAdapter',
    'get_structured_logger',
    
    # Metrics utilities
    'track_execution_time',
    'track_token_usage',
    'MetricsLogger',
    'metrics_logger',
    'timer',
    'async_timer',
    
    # Visualization utilities
    'FlowVisualizer',
    'flow_visualizer',
    'visualize_flow',
    'visualize_execution',
    'visualize_agent_graph',
    'export_flow_image',
    'visualize_execution_metrics',
    'VISUALIZATION_AVAILABLE',
]
