"""
Utility functions for NexusFlow.ai

This package contains utility functions for the NexusFlow system:
- Logging: Customized logging setup
- Metrics: Performance tracking utilities
- Visualization: Flow visualization utilities
"""

# Import once implemented
# from nexusflow.utils.logging import setup_logging, get_logger
# from nexusflow.utils.metrics import track_execution_time, track_token_usage
# from nexusflow.utils.visualization import visualize_flow, export_flow_image

# Simple placeholder logging setup
import logging

def setup_logging(level=logging.INFO):
    """Set up logging with a standard format"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name):
    """Get a logger with the given name"""
    return logging.getLogger(name)

__all__ = [
    # Logging utilities
    'setup_logging',
    'get_logger',
    
    # These would be added once implemented
    # 'track_execution_time',
    # 'track_token_usage',
    # 'visualize_flow',
    # 'export_flow_image',
]
