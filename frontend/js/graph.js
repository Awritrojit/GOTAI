// D3.js Graph Visualization for GOT-AI

class GraphVisualizer {
    constructor(containerId) {
        console.log(`GraphVisualizer constructor called with containerId: ${containerId}`);
        
        this.container = d3.select(`#${containerId}`);
        this.svg = this.container; // This should be the SVG element itself
        this.width = 800;
        this.height = 600;
        
        // Check if the SVG was found
        if (this.container.empty()) {
            console.error(`SVG element with ID '${containerId}' not found!`);
            throw new Error(`SVG element with ID '${containerId}' not found!`);
        }
        
        console.log(`GraphVisualizer: SVG element found, proceeding with initialization`);
        
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.selectedNode = null;
        this.nodeClickHandler = null;
        
        try {
            this.init();
            console.log(`GraphVisualizer: Initialization completed successfully`);
        } catch (error) {
            console.error(`GraphVisualizer initialization failed:`, error);
            throw error;
        }
    }
    
    init() {
        // Clear any existing content
        this.svg.selectAll("*").remove();
        
        // Get container dimensions if available
        const containerNode = this.svg.node();
        if (containerNode) {
            const rect = containerNode.getBoundingClientRect();
            if (rect.width > 0) this.width = rect.width;
            if (rect.height > 0) this.height = rect.height;
        }
        
        // Set up SVG dimensions
        this.svg
            .attr("width", this.width)
            .attr("height", this.height)
            .attr("viewBox", `0 0 ${this.width} ${this.height}`);
            
        // Create groups for different elements
        this.linkGroup = this.svg.append("g").attr("class", "links");
        this.nodeGroup = this.svg.append("g").attr("class", "nodes");
        this.labelGroup = this.svg.append("g").attr("class", "labels");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                this.linkGroup.attr("transform", event.transform);
                this.nodeGroup.attr("transform", event.transform);
                this.labelGroup.attr("transform", event.transform);
            });
            
        this.svg.call(zoom);
        
        // Reset zoom to identity transform
        this.svg.call(zoom.transform, d3.zoomIdentity);
        
        // Store zoom for reset functionality
        this.zoom = zoom;
        
        // Set up simulation
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(25));
    }
    
    setNodeClickHandler(handler) {
        this.nodeClickHandler = handler;
    }
    
    drag(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }
    
    update(graphData) {
        this.lastGraphData = graphData; // Store for togglePrunedNodes
        this.nodes = graphData.nodes || [];
        this.links = graphData.links || [];
        
        // Filter out pruned nodes if option is unchecked
        const showPrunedElement = document.getElementById("show-pruned");
        const showPruned = showPrunedElement ? showPrunedElement.checked : true;
        const visibleNodes = showPruned ? this.nodes : this.nodes.filter(d => !d.is_pruned);
        const visibleLinks = this.links.filter(l => {
            const sourceVisible = visibleNodes.find(n => n.id === l.source || n.id === l.source.id);
            const targetVisible = visibleNodes.find(n => n.id === l.target || n.id === l.target.id);
            return sourceVisible && targetVisible;
        });
        
        this.updateLinks(visibleLinks);
        this.updateNodes(visibleNodes);
        this.updateLabels(visibleNodes);
        
        // Update simulation
        this.simulation.nodes(visibleNodes);
        this.simulation.force("link").links(visibleLinks);
        this.simulation.alpha(0.3).restart();
    }
    
    updateLinks(links) {
        const link = this.linkGroup
            .selectAll("line")
            .data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
            
        link.exit().remove();
        
        const linkEnter = link.enter()
            .append("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(d.value || 1) * 2);
            
        link.merge(linkEnter)
            .attr("stroke-opacity", d => (d.value || 0.5) * 0.6);
    }
    
    updateNodes(nodes) {
        const node = this.nodeGroup
            .selectAll("circle")
            .data(nodes, d => d.id);
            
        node.exit().remove();
        
        const nodeEnter = node.enter()
            .append("circle")
            .attr("class", "node")
            .attr("r", d => Math.max(8, Math.min(20, 10 + d.score * 10)));
            
        // Add drag behavior safely
        try {
            nodeEnter.call(this.drag(this.simulation));
        } catch (error) {
            console.error("Error applying drag behavior:", error);
        }
            
        const nodeUpdate = node.merge(nodeEnter)
            .attr("fill", d => this.getNodeColor(d))
            .classed("pruned", d => d.is_pruned)
            .classed("selected", d => this.selectedNode && d.id === this.selectedNode.id);
            
        // Add click handler
        nodeUpdate.on("click", (event, d) => {
            this.selectNode(d);
            // Call the node click handler if it exists (for archive viewer)
            if (this.nodeClickHandler) {
                this.nodeClickHandler(d);
            }
            // Call global showNodeDetails if it exists (for main app)
            else if (typeof window.showNodeDetails === 'function') {
                window.showNodeDetails(d);
            }
        });
        
        // Add hover effects
        nodeUpdate.on("mouseover", function(event, d) {
            d3.select(this).transition().duration(200).attr("r", 
                Math.max(10, Math.min(25, 12 + d.score * 12))
            );
        })
        .on("mouseout", function(event, d) {
            d3.select(this).transition().duration(200).attr("r", 
                Math.max(8, Math.min(20, 10 + d.score * 10))
            );
        });
        
        // Update simulation tick
        this.simulation.on("tick", () => {
            this.linkGroup.selectAll("line")
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
                
            this.nodeGroup.selectAll("circle")
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
                
            this.labelGroup.selectAll("text")
                .attr("x", d => d.x)
                .attr("y", d => d.y + 4);
        });
    }
    
    updateLabels(nodes) {
        const label = this.labelGroup
            .selectAll("text")
            .data(nodes, d => d.id);
            
        label.exit().remove();
        
        const labelEnter = label.enter()
            .append("text")
            .attr("class", "node-label")
            .attr("dy", "0.35em");
            
        label.merge(labelEnter)
            .text(d => d.score.toFixed(2))
            .attr("font-size", d => Math.max(8, Math.min(12, 8 + d.score * 4)));
    }
    
    getNodeColor(node) {
        if (node.is_pruned) {
            return "#888";
        }
        
        if (node.score >= 0.7) {
            return "#4CAF50"; // Green for high scores
        } else if (node.score >= 0.4) {
            return "#FFC107"; // Yellow for medium scores
        } else {
            return "#F44336"; // Red for low scores
        }
    }
    
    selectNode(node) {
        this.selectedNode = node;
        this.nodeGroup.selectAll("circle")
            .classed("selected", d => d.id === node.id);
    }
    
    resetZoom() {
        this.svg.transition().duration(750).call(
            this.zoom.transform,
            d3.zoomIdentity
        );
    }
    
    togglePrunedNodes() {
        if (this.lastGraphData) {
            this.update(this.lastGraphData);
        }
    }
    
    highlightTrajectory(nodeIds) {
        console.log('Highlighting trajectory:', nodeIds);
        
        // Clear previous highlights
        this.clearTrajectoryHighlight();
        
        // Store trajectory for reference
        this.trajectoryNodeIds = nodeIds;
        
        // Highlight trajectory nodes
        this.nodeGroup.selectAll("circle")
            .classed("trajectory-node", d => nodeIds.includes(d.id));
        
        // Highlight trajectory links
        this.linkGroup.selectAll("line")
            .classed("trajectory-link", d => {
                const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
                const targetId = typeof d.target === 'object' ? d.target.id : d.target;
                return nodeIds.includes(sourceId) && nodeIds.includes(targetId);
            });
        
        console.log('Trajectory highlighted');
    }
    
    clearTrajectoryHighlight() {
        this.nodeGroup.selectAll("circle")
            .classed("trajectory-node", false)
            .classed("trajectory-highlighted", false);
        
        this.linkGroup.selectAll("line")
            .classed("trajectory-link", false);
        
        this.trajectoryNodeIds = [];
    }
    
    highlightNode(nodeId) {
        // Add temporary highlight to specific node
        this.nodeGroup.selectAll("circle")
            .classed("node-highlighted", d => d.id === nodeId)
            .attr("r", d => {
                if (d.id === nodeId) {
                    // Scale up the highlighted node by increasing radius
                    return Math.max(10, Math.min(25, (10 + d.score * 10) * 1.3));
                }
                return Math.max(8, Math.min(20, 10 + d.score * 10));
            });
        
        // Also ensure the label follows the highlight
        this.labelGroup.selectAll("text")
            .classed("node-highlighted", d => d.id === nodeId);
    }
    
    unhighlightNode(nodeId) {
        // Remove temporary highlight from specific node and restore original size
        this.nodeGroup.selectAll("circle")
            .classed("node-highlighted", d => d.id === nodeId ? false : null)
            .attr("r", d => Math.max(8, Math.min(20, 10 + d.score * 10))); // Restore original radius
            
        // Also remove label highlight
        this.labelGroup.selectAll("text")
            .classed("node-highlighted", d => d.id === nodeId ? false : null);
    }
    
    focusOnNode(nodeId) {
        // Find the node and center the view on it
        const node = this.nodes.find(n => n.id === nodeId);
        if (node && node.x !== undefined && node.y !== undefined) {
            const transform = d3.zoomIdentity
                .translate(this.width / 2 - node.x, this.height / 2 - node.y)
                .scale(1.5);
            
            this.svg.transition().duration(750).call(
                this.zoom.transform,
                transform
            );
            
            // Temporarily highlight the focused node
            this.highlightNode(nodeId);
            setTimeout(() => this.unhighlightNode(nodeId), 2000);
        }
    }
    
    resetZoom() {
        if (this.zoom && this.svg) {
            this.svg.transition().duration(750).call(
                this.zoom.transform,
                d3.zoomIdentity
            );
        }
    }
    
    togglePrunedNodes(showPruned) {
        if (this.lastGraphData) {
            this.update(this.lastGraphData);
        }
    }
    
    selectNode(node) {
        this.selectedNode = node;
        // Update node styling to show selection
        this.nodeGroup.selectAll("circle")
            .classed("selected", d => d.id === node.id);
    }
}

// Initialize global graph visualizer (only if graph-container exists)
let graphVisualizer;

document.addEventListener('DOMContentLoaded', function() {
    const graphContainer = document.getElementById("graph-container");
    const graphSvg = document.getElementById("graph-svg");
    
    if (graphContainer && graphSvg) {
        console.log('Initializing GraphVisualizer for main page...');
        graphVisualizer = new GraphVisualizer("graph-svg");
        
        // Make it globally accessible
        window.graphVisualizer = graphVisualizer;
        
        // Add reset zoom functionality
        const resetZoomBtn = document.getElementById("reset-zoom");
        if (resetZoomBtn) {
            resetZoomBtn.addEventListener("click", () => {
                graphVisualizer.resetZoom();
            });
        }
        
        // Add show/hide pruned nodes functionality
        const showPrunedCheckbox = document.getElementById("show-pruned");
        if (showPrunedCheckbox) {
            showPrunedCheckbox.addEventListener("change", () => {
                // Re-render with current data
                if (window.lastGraphData) {
                    graphVisualizer.update(window.lastGraphData);
                }
            });
        }
        
        console.log('GraphVisualizer initialized successfully');
    } else {
        console.log('Graph container or SVG not found, skipping GraphVisualizer initialization');
    }
});
