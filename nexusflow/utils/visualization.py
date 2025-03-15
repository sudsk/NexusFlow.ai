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
    import numpy as np
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
            return_base64: Whether to return a base64-encoded image
            
        Returns:
            Path to the output file or base64-encoded image
        """
        if not self.visualization_available:
            logger.error("Visualization packages not installed. Install networkx and matplotlib.")
            return None
        
        # Extract execution path from execution data
        execution_path = execution_data.get("execution_path", [])
        execution_trace = execution_data.get("execution_trace", [])
        
        # Use flow data if provided, or create from execution data
        if flow_data:
            # Extract nodes and edges from flow data
            nodes = flow_data.get("nodes", {})
            edges = flow_data.get("edges", [])
        else:
            # Create minimal flow representation from execution data
            nodes = {}
            edges = []
            agent_nodes = {}
            
            # Extract nodes from execution trace
            for step in execution_trace:
                if "agent_id" in step and "agent_name" in step:
                    agent_id = step["agent_id"]
                    if agent_id not in agent_nodes:
                        agent_nodes[agent_id] = {
                            "name": step["agent_name"],
                            "node_type": "agent"
                        }
            
            # Add nodes to flow data
            nodes = agent_nodes
            
            # Extract edges from execution trace
            prev_agent_id = None
            for step in execution_trace:
                if "agent_id" in step:
                    curr_agent_id = step["agent_id"]
                    # Add edge if we have a delegation
                    if prev_agent_id and prev_agent_id != curr_agent_id and step.get("type") == "delegation":
                        edges.append({
                            "source": prev_agent_id,
                            "target": curr_agent_id,
                            "type": "delegation"
                        })
                    prev_agent_id = curr_agent_id
        
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
        
        # Find nodes in the execution path for highlighting
        execution_path_nodes = set()
        if highlight_path:
            for step in execution_trace:
                if "agent_id" in step:
                    execution_path_nodes.add(step["agent_id"])
        
        for node in G.nodes():
            node_data = G.nodes[node]
            
            # Color based on node type and execution path
            if node in execution_path_nodes and highlight_path:
                node_colors.append(self.highlight_color)
            elif node_data.get("node_type") == "agent":
                node_colors.append(self.node_color)
            elif node_data.get("node_type") == "tool":
                node_colors.append("#FF922B")  # Orange for tools
            elif node_data.get("node_type") == "router":
                node_colors.append("#20C997")  # Teal for routers
            else:
                node_colors.append(self.node_color)
            
            # Size based on importance
            if node in execution_path_nodes and highlight_path:
                node_sizes.append(300)  # Larger for execution path nodes
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
        
        # Draw edges with different colors for execution path
        if highlight_path:
            # Regular edges
            regular_edges = [(u, v) for u, v in G.edges() if u not in execution_path_nodes or v not in execution_path_nodes]
            if regular_edges:
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=regular_edges,
                    edge_color=self.edge_color,
                    width=1.0,
                    alpha=0.4,
                    arrowstyle="->"
                )
            
            # Execution path edges
            execution_edges = [(u, v) for u, v in G.edges() if u in execution_path_nodes and v in execution_path_nodes]
            if execution_edges:
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=execution_edges,
                    edge_color=self.highlight_color,
                    width=2.0,
                    alpha=0.8,
                    arrowstyle="->",
                    arrowsize=15
                )
        else:
            # Draw all edges the same
            nx.draw_networkx_edges(
                G, pos,
                edge_color=self.edge_color,
                width=1.5,
                alpha=0.6,
                arrowstyle="->",
                arrowsize=15
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
        elif "flow_id" in execution_data:
            plt.title(f"Execution: {execution_data['flow_id']}", color=self.text_color)
        else:
            plt.title("Execution Visualization", color=self.text_color)
        
        # Remove axes
        plt.axis("off")
        
        # Tight layout
        plt.tight_layout()
        
        # Determine output path
        output_format = output_format or self.default_format
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exec_id = execution_data.get("id", "execution").replace(" ", "_").lower()
            output_file = os.path.join(self.output_dir, f"{exec_id}_{timestamp}.{output_format}")
        
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
        
        logger.info(f"Execution visualization saved to {output_file}")
        return output_file
    
    def visualize_agent_graph(
        self,
        agents: List[Dict[str, Any]],
        output_file: Optional[str] = None,
        output_format: Optional[str] = None,
        layout: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None,
        show_capabilities: bool = True,
        title: Optional[str] = None,
        return_base64: bool = False
    ) -> Optional[str]:
        """
        Visualize a graph of agents and their relationships
        
        Args:
            agents: List of agent dictionaries
            output_file: Output file path (None for automatic naming)
            output_format: Output format (png, svg, pdf)
            layout: Layout algorithm
            figsize: Figure size
            show_capabilities: Whether to show agent capabilities
            title: Custom title for the visualization
            return_base64: Whether to return a base64-encoded image
            
        Returns:
            Path to the output file or base64-encoded image
        """
        if not self.visualization_available:
            logger.error("Visualization packages not installed. Install networkx and matplotlib.")
            return None
            
        # Create graph
        G = nx.Graph()
        
        # Add nodes for each agent
        for agent in agents:
            agent_id = agent.get("agent_id", agent.get("id", f"agent_{len(G.nodes())}"))
            G.add_node(
                agent_id,
                name=agent.get("name", "Unnamed Agent"),
                capabilities=agent.get("capabilities", []),
                model=agent.get("model_provider", "") + "/" + agent.get("model_name", ""),
                tools=agent.get("tool_names", [])
            )
            
        # Add edges between agents that share capabilities
        for i, agent1 in enumerate(agents):
            agent1_id = agent1.get("agent_id", agent1.get("id", f"agent_{i}"))
            agent1_caps = set(agent1.get("capabilities", []))
            
            for j, agent2 in enumerate(agents[i+1:], i+1):
                agent2_id = agent2.get("agent_id", agent2.get("id", f"agent_{j}"))
                agent2_caps = set(agent2.get("capabilities", []))
                
                # If agents share capabilities, add an edge
                shared_caps = agent1_caps.intersection(agent2_caps)
                if shared_caps:
                    G.add_edge(agent1_id, agent2_id, shared_capabilities=list(shared_caps))
        
        # Create figure
        figsize = figsize or self.default_figsize
        plt.figure(figsize=figsize)
        
        # Set background color
        plt.gca().set_facecolor(self.bg_color)
        plt.gcf().set_facecolor(self.bg_color)
        
        # Choose layout
        layout = layout or "spring"
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
            pos = nx.spring_layout(G, k=0.3, iterations=50)
        
        # Draw nodes with colors based on number of capabilities
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            capabilities = G.nodes[node].get("capabilities", [])
            cap_count = len(capabilities)
            
            # Color based on capability count
            if cap_count > 3:
                node_colors.append("#3182CE")  # Blue for many capabilities
            elif cap_count > 1:
                node_colors.append("#38A169")  # Green for some capabilities
            else:
                node_colors.append("#E53E3E")  # Red for few capabilities
            
            # Size based on capability count
            node_sizes.append(200 + cap_count * 50)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8,
            edgecolors=self.edge_color,
            linewidths=1
        )
        
        # Draw edges with thickness based on shared capabilities
        edge_widths = []
        for u, v in G.edges():
            shared_caps = len(G.edges[u, v].get("shared_capabilities", []))
            edge_widths.append(1 + shared_caps * 0.5)
        
        nx.draw_networkx_edges(
            G, pos,
            width=edge_widths,
            alpha=0.6,
            edge_color=self.edge_color
        )
        
        # Draw labels
        labels = {}
        for node in G.nodes():
            labels[node] = G.nodes[node].get("name", str(node))
        
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            font_size=10,
            font_color=self.text_color
        )
        
        # Add capability labels if requested
        if show_capabilities:
            cap_labels = {}
            for node in G.nodes():
                caps = G.nodes[node].get("capabilities", [])
                if caps:
                    cap_labels[node] = "\n".join(caps)
            
            # Offset the position slightly for capability labels
            cap_pos = {node: (x, y - 0.1) for node, (x, y) in pos.items()}
            
            nx.draw_networkx_labels(
                G, cap_pos,
                labels=cap_labels,
                font_size=8,
                font_color="gray",
                horizontalalignment="center",
                verticalalignment="top"
            )
        
        # Add title
        if title:
            plt.title(title, color=self.text_color)
        else:
            plt.title("Agent Capability Graph", color=self.text_color)
        
        # Remove axes
        plt.axis("off")
        
        # Tight layout
        plt.tight_layout()
        
        # Determine output path
        output_format = output_format or self.default_format
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"agent_graph_{timestamp}.{output_format}")
        
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
        
        logger.info(f"Agent graph visualization saved to {output_file}")
        return output_file
    
    def export_flow_image(
        self,
        flow_data: Dict[str, Any],
        output_file: Optional[str] = None,
        output_format: Optional[str] = None,
        include_metadata: bool = True
    ) -> Optional[str]:
        """
        Export a flow as an image with metadata
        
        Args:
            flow_data: Flow data to visualize
            output_file: Output file path (None for automatic naming)
            output_format: Output format (png, svg, pdf)
            include_metadata: Whether to include metadata in the image
            
        Returns:
            Path to the output file
        """
        # Visualize flow
        flow_img_path = self.visualize_flow(
            flow_data=flow_data,
            output_file=None if include_metadata else output_file,
            output_format=output_format,
            show_details=True,
            title=flow_data.get("name", "Flow Visualization")
        )
        
        # If no metadata or visualization failed, return the flow image path
        if not include_metadata or not flow_img_path:
            return flow_img_path
        
        # Create a new figure with the flow visualization and metadata
        fig, (ax1, ax2) = plt.subplots(
            nrows=2, 
            ncols=1, 
            figsize=(12, 10),
            gridspec_kw={'height_ratios': [3, 1]}
        )
        
        # Set background color
        fig.set_facecolor(self.bg_color)
        ax1.set_facecolor(self.bg_color)
        ax2.set_facecolor(self.bg_color)
        
        # Load flow visualization
        img = plt.imread(flow_img_path)
        ax1.imshow(img)
        ax1.axis('off')
        
        # Add metadata text
        metadata_text = [
            f"Flow: {flow_data.get('name', 'Unnamed Flow')}",
            f"ID: {flow_data.get('flow_id', flow_data.get('id', 'Unknown'))}",
            f"Created: {flow_data.get('created_at', 'Unknown')}",
            f"Agents: {len(flow_data.get('agents', []))}",
            f"Description: {flow_data.get('description', 'No description')}"
        ]
        
        ax2.text(
            0.05, 0.5, 
            "\n".join(metadata_text), 
            fontsize=12,
            color=self.text_color,
            verticalalignment='center',
            transform=ax2.transAxes
        )
        ax2.axis('off')
        
        # Determine output path
        output_format = output_format or self.default_format
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            flow_name = flow_data.get("name", "flow").replace(" ", "_").lower()
            output_file = os.path.join(self.output_dir, f"{flow_name}_export_{timestamp}.{output_format}")
        
        # Save figure
        plt.savefig(output_file, format=output_format, facecolor=self.bg_color, dpi=300)
        plt.close(fig)
        
        # Clean up temporary file
        try:
            os.remove(flow_img_path)
        except:
            pass
        
        logger.info(f"Flow image with metadata exported to {output_file}")
        return output_file
    
    def visualize_execution_metrics(
        self,
        execution_data: Dict[str, Any],
        output_file: Optional[str] = None,
        output_format: Optional[str] = None,
        figsize: Optional[Tuple[int, int]] = None
    ) -> Optional[str]:
        """
        Visualize metrics from an execution
        
        Args:
            execution_data: Execution data to visualize
            output_file: Output file path (None for automatic naming)
            output_format: Output format (png, svg, pdf)
            figsize: Figure size
            
        Returns:
            Path to the output file
        """
        if not self.visualization_available:
            logger.error("Visualization packages not installed. Install networkx and matplotlib.")
            return None
        
        # Extract execution trace
        execution_trace = execution_data.get("execution_trace", [])
        if not execution_trace:
            logger.error("No execution trace found in execution data")
            return None
        
        # Create figure
        figsize = figsize or (10, 12)
        fig = plt.figure(figsize=figsize)
        fig.set_facecolor(self.bg_color)
        
        # Create subplots
        gs = plt.GridSpec(3, 2, figure=fig)
        
        # 1. Agent activity plot
        ax1 = fig.add_subplot(gs[0, :])
        ax1.set_facecolor(self.bg_color)
        
        # Extract agent activities
        agent_activities = {}
        agent_steps = []
        
        for step in execution_trace:
            if "agent_id" in step and "timestamp" in step:
                agent_id = step["agent_id"]
                agent_name = step.get("agent_name", agent_id)
                timestamp = datetime.fromisoformat(step["timestamp"].replace("Z", "+00:00"))
                step_num = step.get("step", 0)
                
                if agent_name not in agent_activities:
                    agent_activities[agent_name] = []
                
                agent_activities[agent_name].append((step_num, timestamp))
                agent_steps.append((step_num, agent_name, timestamp))
        
        # Sort by step number
        agent_steps.sort(key=lambda x: x[0])
        
        # Plot agent activity
        agents = list(agent_activities.keys())
        colors = plt.cm.tab10(np.linspace(0, 1, len(agents)))
        
        for i, (agent_name, activities) in enumerate(agent_activities.items()):
            steps, timestamps = zip(*activities)
            ax1.scatter(steps, [i] * len(steps), label=agent_name, color=colors[i], s=100, alpha=0.7)
            
            # Connect points
            if len(steps) > 1:
                ax1.plot(steps, [i] * len(steps), color=colors[i], alpha=0.4)
        
        ax1.set_yticks(range(len(agents)))
        ax1.set_yticklabels(agents)
        ax1.set_xlabel('Execution Step')
        ax1.set_title('Agent Activity During Execution', color=self.text_color)
        ax1.grid(True, linestyle='--', alpha=0.3)
        
        # 2. Tool usage pie chart
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.set_facecolor(self.bg_color)
        
        # Count tool usage
        tool_usage = {}
        for step in execution_trace:
            if step.get("type") == "tool_execution" and "decision" in step:
                tool_name = step["decision"].get("tool_name", "unknown")
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        if tool_usage:
            # Plot pie chart
            labels = list(tool_usage.keys())
            sizes = list(tool_usage.values())
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(np.linspace(0, 1, len(labels))))
            ax2.axis('equal')
            ax2.set_title('Tool Usage Distribution', color=self.text_color)
        else:
            ax2.text(0.5, 0.5, "No tool usage data", ha='center', va='center', color=self.text_color)
            ax2.axis('off')
        
        # 3. Step duration bar chart
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.set_facecolor(self.bg_color)
        
        # Calculate step durations
        step_durations = []
        prev_timestamp = None
        
        for step_num, agent_name, timestamp in agent_steps:
            if prev_timestamp:
                duration = (timestamp - prev_timestamp).total_seconds()
                step_durations.append((step_num - 1, duration))
            prev_timestamp = timestamp
        
        if step_durations:
            steps, durations = zip(*step_durations)
            ax3.bar(steps, durations, color='teal', alpha=0.7)
            ax3.set_xlabel('Step Number')
            ax3.set_ylabel('Duration (seconds)')
            ax3.set_title('Step Duration', color=self.text_color)
            ax3.grid(True, linestyle='--', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, "No step duration data", ha='center', va='center', color=self.text_color)
            ax3.axis('off')
        
        # 4. Agent decision types
        ax4 = fig.add_subplot(gs[2, :])
        ax4.set_facecolor(self.bg_color)
        
        # Count decision types by agent
        decision_types = {}
        for step in execution_trace:
            if "agent_name" in step and "output" in step and isinstance(step["output"], dict) and "metadata" in step["output"]:
                agent_name = step["agent_name"]
                if "decision" in step["output"]["metadata"] and "action" in step["output"]["metadata"]["decision"]:
                    action = step["output"]["metadata"]["decision"]["action"]
                    
                    if agent_name not in decision_types:
                        decision_types[agent_name] = {}
                    
                    decision_types[agent_name][action] = decision_types[agent_name].get(action, 0) + 1
        
        if decision_types:
            # Prepare data for stacked bar chart
            agents = list(decision_types.keys())
            all_actions = set()
            for agent_decisions in decision_types.values():
                all_actions.update(agent_decisions.keys())
            
            all_actions = sorted(list(all_actions))
            action_colors = plt.cm.tab10(np.linspace(0, 1, len(all_actions)))
            
            # Create data for each action
            data = {action: [] for action in all_actions}
            for agent in agents:
                for action in all_actions:
                    data[action].append(decision_types.get(agent, {}).get(action, 0))
            
            # Plot stacked bar chart
            bottom = np.zeros(len(agents))
            for i, action in enumerate(all_actions):
                ax4.bar(agents, data[action], bottom=bottom, label=action, color=action_colors[i], alpha=0.7)
                bottom += np.array(data[action])
            
            ax4.set_xlabel('Agent')
            ax4.set_ylabel('Number of Decisions')
            ax4.set_title('Agent Decision Types', color=self.text_color)
            ax4.legend(title="Decision Type")
            ax4.grid(True, linestyle='--', alpha=0.3)
        else:
            ax4.text(0.5, 0.5, "No decision data available", ha='center', va='center', color=self.text_color)
            ax4.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Determine output path
        output_format = output_format or self.default_format
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exec_id = execution_data.get("id", "execution").replace(" ", "_").lower()
            output_file = os.path.join(self.output_dir, f"{exec_id}_metrics_{timestamp}.{output_format}")
        
        # Save figure
        plt.savefig(output_file, format=output_format, facecolor=self.bg_color, dpi=300)
        plt.close()
        
        logger.info(f"Execution metrics visualization saved to {output_file}")
        return output_file
