"""
Visualization utilities for NexusFlow.ai

This module provides utilities for visualizing flows and execution paths in the NexusFlow system.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import tempfile
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    VISUALIZATION_AVAILABLE = True
except ImportError:
    logger.warning("Visualization packages not installed. Install networkx and matplotlib for visualization features.")
    VISUALIZATION_AVAILABLE = False

class FlowVisualizer:
    """
    Visualizer for NexusFlow flows and execution paths
    
    This class provides methods for visualizing flows, execution paths, and node relationships.
    """
    
    def __init__(
        self,
        output_dir: str = "visualizations",
        default_format: str = "png",
        default_layout: str = "spring",
        default_figsize: Tuple[int, int] = (12, 8),
        theme: str = "light"
    ):
        """
        Initialize flow visualizer
        
        Args:
            output_dir: Directory for saving visualizations
            default_format: Default output format (png, svg, pdf)
            default_layout: Default layout algorithm
            default_figsize: Default figure size
            theme: Color theme ('light' or 'dark')
        """
        self.output_dir = output_dir
        self.default_format = default_format
        self.default_layout = default_layout
        self.default_figsize = default_figsize
        self.theme = theme
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up theme colors
        if theme == "dark":
            self.bg_color = "#2E3440"
            self.node_color = "#81A1C1"
            self.edge_color = "#D8DEE9"
            self.text_color = "#ECEFF4"
            self.highlight_color = "#A3BE8C"
            self.error_color = "#BF616A"
        else:
            self.bg_color = "#FFFFFF"
            self.node_color = "#4C6EF5"
            self.edge_color = "#212529"
            self.text_color = "#212529"
            self.highlight_color = "#40C057"
            self.error_color = "#FA5252"
        
        # Check if visualization packages are available
        self.visualization_available = VISUALIZATION_AVAILABLE
    
    def visualize_flow(
        self,
        flow_data: Dict[str, Any],
        output_file: Optional[str] = None,
        output_format: Optional[str] = None,
        layout: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None,
        show_details: bool = True,
        title: Optional[str] = None,
        return_base64: bool = False
    ) -> Optional[str]:
        """
        Visualize a flow
        
        Args:
            flow_data: Flow data to visualize
            output_file: Output file path (None for automatic naming)
            output_format: Output format (png, svg, pdf)
            layout: Layout algorithm
            figsize: Figure size
            show_details: Whether to show node and edge details
            title: Custom title for the visualization
            return_base64: Whether to return a base64-encoded image
            
        Returns:
            Path to the output file or base64-encoded image
        """
        if not self.visualization_available:
            logger.error("Visualization packages not installed. Install networkx and matplotlib.")
            return None
        
        # Extract nodes and edges from flow data
        nodes = flow_data.get("nodes", {})
        edges = flow_data.get("edges", [])
        
        # Create graph
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node_data in nodes.items():
            G.add_node(node_id, **node_data)
        
        # Add edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                G.add_edge(source, target, **{k: v for k, v in edge.items() if k not in ["source", "target"]})
        
        # Create figure
        figsize = figsize or self.default_figsize
        plt.figure(figsize=figsize)
        
        # Set background color
        plt.gca().set_facecolor(self.bg_color)
        plt.gcf().set_facecolor(self.bg_color)
        
        # Choose layout
        layout = layout or self.default_layout
        if layout == "spring":
            pos = nx.spring_layout(G, k=0.3, iterations=50)
        elif layout == "spectral":
            pos = nx.spectral_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "shell":
            pos = nx.shell_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        else:
            # Default to spring layout
            pos = nx.spring_layout(G, k=0.3, iterations=50)
        
        # Get node colors and sizes
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            node_data = G.nodes[node]
            
            # Color based on node type
            if node_data.get("node_type") == "agent":
                node_colors.append(self.node_color)
            elif node_data.get("node_type") == "tool":
                node_colors.append("#FF922B")  # Orange for tools
            elif node_data.get("node_type") == "router":
                node_colors.append("#20C997")  # Teal for routers
            elif node_data.get("node_type") == "start":
                node_colors.append(self.highlight_color)
            elif node_data.get("node_type") == "end":
                node_colors.append("#F06595")  # Pink for end node
            else:
                node_colors.append(self.node_color)
            
            # Size based on importance
            if node_data.get("node_type") in ["start", "end"]:
                node_sizes.append(300)  # Larger for special nodes
            elif node_data.get("node_type") == "agent":
                node_sizes.append(250)  # Regular size for agents
            else:
                node_sizes.append(200)  # Smaller for other nodes
        
        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            edgecolors=self.edge_color,
            linewidths=1
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color=self.edge_color,
            width=1.5,
            alpha=0.6,
            arrowsize=15,
            arrowstyle="->"
        )
        
        # Draw labels
        labels = {}
        for node in G.nodes():
            node_data = G.nodes[node]
            labels[node] = node_data.get("name", str(node))
        
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            font_size=10,
            font_color=self.text_color
        )
        
        # Draw edge labels if show_details is True
        if show_details:
            edge_labels = {}
            for u, v, data in G.edges(data=True):
                if "type" in data:
                    edge_labels[(u, v)] = data["type"]
            
            nx.draw_networkx_edge_labels(
                G, pos,
                edge_labels=edge_labels,
                font_size=8,
                font_color=self.text_color
            )
        
        # Add title
        if title:
            plt.title(title, color=self.text_color)
        elif "name" in flow_data:
            plt.title(f"Flow: {flow_data['name']}", color=self.text_color)
        else:
            plt.title("Flow Visualization", color=self.text_color)
        
        # Remove axes
        plt.axis("off")
        
        # Tight layout
        plt.tight_layout()
        
        # Determine output path
        output_format = output_format or self.default_format
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            flow_name = flow_data.get("name", "flow").replace(" ", "_").lower()
            output_file = os.path.join(self.output_dir, f"{flow_name}_{timestamp}.{output_format}")
        
        # Return base64 if requested
        if return_base64:
            buf = tempfile.BytesIO()
            plt.savefig(buf, format=output_format, facecolor=self.bg_color, dpi=100)
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/{output_format};base64,{img_str}"
        
        # Save figure
        plt.savefig(output_file, format=output_format, facecolor=self.bg_color, dpi=300)
        plt.close()
        
        logger.info(f"Flow visualization saved to {output_file}")
        return output_file
    
    def visualize_execution(
        self,
        execution_data: Dict[str, Any],
        flow_data: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None,
        output_format: Optional[str] = None,
        layout: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None,
        show_details: bool = True,
        title: Optional[str] = None,
        highlight_path: bool = True,
        return_base64: bool = False
    ) -> Optional[str]:
        """
        Visualize an execution path
        
        Args:
            execution_data: Execution data to visualize
            flow_data: Flow data for context (optional)
            output_file: Output file path (None for automatic naming)
            output_format: Output format (png, svg, pdf)
            layout: Layout algorithm
            figsize: Figure size
            show_details: Whether to show node and edge details
            title: Custom title for the visualization
            highlight_path: Whether to highlight the execution path
            return_base64:
