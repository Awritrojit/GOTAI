// Main application logic for GOT-AI frontend

class GOTAIApp {
    constructor() {
        this.isRunning = false;
        this.updateInterval = null;
        this.baseURL = window.location.origin;
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        document.getElementById('start-btn').addEventListener('click', () => this.startAnalysis());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopAnalysis());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearData());
        document.getElementById('get-analysis').addEventListener('click', () => this.getAnalysis());
        document.getElementById('refresh-archives').addEventListener('click', () => this.loadArchives());
        
        // Add reset zoom handler
        document.getElementById('reset-zoom').addEventListener('click', () => {
            if (window.graphVisualizer && window.graphVisualizer.resetZoom) {
                window.graphVisualizer.resetZoom();
            }
        });
        
        // Enable enter key in inputs
        document.getElementById('hypothesis-input').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.startAnalysis();
            }
        });
        
        document.getElementById('run-name-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('hypothesis-input').focus();
            }
        });
        
        // Initial status check and load archives
        this.updateStatus();
        this.loadArchives();
        
        console.log('GOT-AI Frontend initialized');
    }
    
    async startAnalysis() {
        const hypothesis = document.getElementById('hypothesis-input').value.trim();
        
        if (!hypothesis) {
            alert('Please enter a hypothesis to analyze');
            return;
        }
        
        // Get advanced settings with defaults
        const maxDepth = parseInt(document.getElementById('max-depth-input').value) || 3;
        const maxNodes = parseInt(document.getElementById('max-nodes-input').value) || 50;
        
        try {
            this.setUIState('starting');
            
            const response = await fetch(`${this.baseURL}/api/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    hypothesis,
                    max_depth: maxDepth,
                    max_nodes: maxNodes
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Analysis started:', data);
            
            this.isRunning = true;
            this.setUIState('running');
            this.startPeriodicUpdates();
            
        } catch (error) {
            console.error('Error starting analysis:', error);
            this.showError('Failed to start analysis: ' + error.message);
            this.setUIState('ready');
        }
    }
    
    async stopAnalysis() {
        const runName = document.getElementById('run-name-input').value.trim();
        
        if (!runName) {
            const proceed = confirm('No run name provided. This will stop the analysis without archiving. Continue?');
            if (!proceed) return;
        }
        
        try {
            this.setUIState('stopping');
            
            const response = await fetch(`${this.baseURL}/api/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ run_name: runName || '' })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Analysis stopped:', data);
            
            // Show success message
            if (runName && data.archive_name) {
                this.showSuccess(`Analysis archived as "${runName}". ${data.nodes_archived} nodes saved.`);
            } else {
                this.showSuccess('Analysis stopped. Data cleared for fresh start.');
            }
            
            this.isRunning = false;
            this.setUIState('ready');
            this.stopPeriodicUpdates();
            
            // Clear inputs for fresh start
            this.clearInputs();
            
            // Refresh graph and archives
            this.updateGraph();
            this.loadArchives();
            
        } catch (error) {
            console.error('Error stopping analysis:', error);
            this.showError('Failed to stop analysis: ' + error.message);
            this.setUIState('ready');
        }
    }
    
    async clearData() {
        const confirm_clear = confirm('This will permanently clear all current analysis data. Are you sure?');
        if (!confirm_clear) return;
        
        try {
            const response = await fetch(`${this.baseURL}/api/clear`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Data cleared:', data);
            
            this.showSuccess('All data cleared successfully. Ready for new analysis.');
            
            // Clear inputs
            this.clearInputs();
            
            // Update UI
            this.updateStatus();
            this.updateGraph();
            
        } catch (error) {
            console.error('Error clearing data:', error);
            this.showError('Failed to clear data: ' + error.message);
        }
    }
    
    clearInputs() {
        document.getElementById('run-name-input').value = '';
        document.getElementById('hypothesis-input').value = '';
    }
    
    async loadArchives() {
        try {
            const response = await fetch(`${this.baseURL}/api/archives`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayArchives(data.archives);
            
        } catch (error) {
            console.error('Error loading archives:', error);
            this.showError('Failed to load archives: ' + error.message);
        }
    }
    
    displayArchives(archives) {
        const container = document.getElementById('archive-list');
        
        if (!archives || archives.length === 0) {
            container.innerHTML = '<p class="placeholder">No archived runs yet</p>';
            return;
        }
        
        const html = archives.map((archive, index) => {
            // Use archived_at for proper date formatting, fallback to timestamp
            const dateStr = archive.archived_at || archive.timestamp;
            let formattedDate = 'Invalid Date';
            
            try {
                if (dateStr) {
                    const date = new Date(dateStr);
                    if (!isNaN(date.getTime())) {
                        formattedDate = date.toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'short', 
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                }
            } catch (e) {
                console.warn('Date parsing error for archive:', archive.archive_name, e);
            }
            
            return `
                <div class="archive-item clickable-archive" data-archive-name="${archive.archive_name}" data-index="${index}">
                    <div class="archive-content">
                        <div class="archive-title">${archive.run_name}</div>
                        <div class="archive-date">${formattedDate}</div>
                    </div>
                    <button class="archive-delete-btn" data-archive-name="${archive.archive_name}" title="Delete archive">
                        🗑️
                    </button>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
        
        // Add event listeners after setting innerHTML
        this.attachArchiveEventListeners();
    }
    
    attachArchiveEventListeners() {
        const container = document.getElementById('archive-list');
        
        // Add click listeners for archive items (entire item is now clickable)
        container.querySelectorAll('.archive-item.clickable-archive').forEach((element, index) => {
            element.addEventListener('click', (event) => {
                // Don't trigger if clicking on delete button
                if (event.target.classList.contains('archive-delete-btn')) {
                    return;
                }
                
                event.preventDefault();
                event.stopPropagation();
                const archiveName = element.dataset.archiveName;
                if (archiveName) {
                    this.openArchiveInNewTab(archiveName);
                }
            });
        });
        
        // Add click listeners for delete buttons
        container.querySelectorAll('.archive-delete-btn').forEach((button, index) => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                const archiveName = button.dataset.archiveName;
                if (archiveName) {
                    this.deleteArchive(archiveName);
                }
            });
        });
    }
    
    openArchiveInNewTab(archiveName) {
        const archiveUrl = `${this.baseURL}/archive?archive=${encodeURIComponent(archiveName)}`;
        window.open(archiveUrl, '_blank');
    }

    async updateStatus() {
        try {
            const response = await fetch(`${this.baseURL}/api/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const status = await response.json();
            
            // Update UI elements
            document.getElementById('node-count').textContent = status.total_nodes;
            
            if (status.is_running !== this.isRunning) {
                this.isRunning = status.is_running;
                this.setUIState(status.is_running ? 'running' : 'ready');
                
                if (status.is_running && !this.updateInterval) {
                    this.startPeriodicUpdates();
                } else if (!status.is_running && this.updateInterval) {
                    this.stopPeriodicUpdates();
                }
            }
            
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }
    
    async updateGraph() {
        try {
            console.log('updateGraph called');
            const response = await fetch(`${this.baseURL}/api/graph_data`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const graphData = await response.json();
            console.log('Graph data received:', graphData);
            
            // Store for re-rendering when options change
            window.lastGraphData = graphData;
            
            // Update graph visualization
            if (window.graphVisualizer) {
                console.log('Updating graph visualizer...');
                window.graphVisualizer.update(graphData);
                console.log('Graph visualizer updated');
            } else {
                console.warn('GraphVisualizer not available, trying to initialize...');
                // Try to initialize it now
                const container = document.getElementById('graph-container');
                let svgElement = document.getElementById('graph-svg');
                
                if (container && !svgElement) {
                    container.innerHTML = '<svg id="graph-svg" width="800" height="600"></svg>';
                    svgElement = document.getElementById('graph-svg');
                }
                
                if (svgElement) {
                    try {
                        window.graphVisualizer = new GraphVisualizer('graph-svg');
                        console.log('GraphVisualizer created during update');
                        window.graphVisualizer.update(graphData);
                    } catch (error) {
                        console.error('Error creating GraphVisualizer during update:', error);
                    }
                } else {
                    console.error('Could not create SVG element during update');
                }
            }
            
            // Update best score
            if (graphData.nodes && graphData.nodes.length > 0) {
                const bestScore = Math.max(...graphData.nodes.map(n => n.cumulative_score));
                document.getElementById('best-score').textContent = bestScore.toFixed(2);
            }
            
        } catch (error) {
            console.error('Error updating graph:', error);
        }
    }
    
    async getAnalysis() {
        try {
            const response = await fetch(`${this.baseURL}/api/analysis`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const analysis = await response.json();
            this.displayAnalysis(analysis);
            
            // Store trajectory for highlighting
            if (analysis.best_trajectory && analysis.best_trajectory.path) {
                window.currentTrajectory = analysis.best_trajectory.path;
                this.highlightTrajectory(analysis.best_trajectory.path);
            }
            
        } catch (error) {
            console.error('Error getting analysis:', error);
            this.showError('Failed to get analysis: ' + error.message);
        }
    }
    
    highlightTrajectory(trajectory) {
        if (window.graphVisualizer && trajectory) {
            console.log('Highlighting trajectory with', trajectory.length, 'nodes');
            window.graphVisualizer.highlightTrajectory(trajectory.map(n => n.id));
        }
    }
    
    displayAnalysis(analysis) {
        const container = document.getElementById('analysis-results');
        
        if (analysis.message) {
            container.innerHTML = `<p class="placeholder">${analysis.message}</p>`;
            return;
        }
        
        const html = `
            <div class="analysis-summary">
                <h4>Analysis Summary</h4>
                <div class="analysis-stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Nodes:</span>
                        <span class="stat-value">${analysis.total_nodes}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Average Score:</span>
                        <span class="stat-value">${analysis.average_score.toFixed(3)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Pruned Nodes:</span>
                        <span class="stat-value">${analysis.pruned_nodes}</span>
                    </div>
                </div>
            </div>
            
            <div class="best-trajectory">
                <h4>Best Reasoning Path</h4>
                <div class="trajectory-stats">
                    <p><strong>Cumulative Score:</strong> ${analysis.best_trajectory.cumulative_score.toFixed(3)}</p>
                    <p><strong>Path Length:</strong> ${analysis.best_trajectory.path_length} steps</p>
                </div>
                <div class="final-insight">
                    <h5>Final Insight:</h5>
                    <p>${analysis.best_trajectory.final_insight}</p>
                </div>
                <div class="reasoning-path">
                    <h5>Reasoning Path:</h5>
                    ${analysis.best_trajectory.path.map((step, index) => `
                        <div class="path-step" data-node-id="${step.id}" data-step-index="${index}">
                            <span class="step-number">${index + 1}.</span>
                            <span class="step-text">${step.text}</span>
                            <span class="step-score">(${step.score.toFixed(2)})</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Add hover interactions for trajectory steps
        this.addTrajectoryHoverEvents();
    }
    
    addTrajectoryHoverEvents() {
        const pathSteps = document.querySelectorAll('.path-step');
        
        pathSteps.forEach(step => {
            const nodeId = step.dataset.nodeId;
            
            step.addEventListener('mouseenter', () => {
                // Highlight the corresponding node in the graph
                if (window.graphVisualizer && nodeId) {
                    window.graphVisualizer.highlightNode(nodeId);
                }
                step.classList.add('highlighted');
            });
            
            step.addEventListener('mouseleave', () => {
                // Remove node highlight
                if (window.graphVisualizer && nodeId) {
                    window.graphVisualizer.unhighlightNode(nodeId);
                }
                step.classList.remove('highlighted');
            });
            
            step.addEventListener('click', () => {
                // Focus on the node in the graph
                if (window.graphVisualizer && nodeId) {
                    window.graphVisualizer.focusOnNode(nodeId);
                }
            });
        });
    }
    
    setUIState(state) {
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const statusElement = document.getElementById('status');
        
        switch (state) {
            case 'ready':
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusElement.textContent = 'Ready';
                statusElement.className = 'value status-ready';
                break;
                
            case 'starting':
                startBtn.disabled = true;
                stopBtn.disabled = true;
                statusElement.textContent = 'Starting...';
                statusElement.className = 'value loading';
                break;
                
            case 'running':
                startBtn.disabled = true;
                stopBtn.disabled = false;
                statusElement.textContent = 'Running';
                statusElement.className = 'value status-running';
                break;
                
            case 'stopping':
                startBtn.disabled = true;
                stopBtn.disabled = true;
                statusElement.textContent = 'Stopping & Archiving...';
                statusElement.className = 'value loading';
                break;
                
            case 'stopped':
                startBtn.disabled = false;
                stopBtn.disabled = true;
                statusElement.textContent = 'Stopped';
                statusElement.className = 'value status-stopped';
                break;
        }
    }
    
    startPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Update immediately
        this.updateGraph();
        
        // Then update every 3 seconds
        this.updateInterval = setInterval(() => {
            this.updateStatus();
            this.updateGraph();
        }, 3000);
    }
    
    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    showError(message) {
        // Simple alert for now - in production, use a better notification system
        alert('Error: ' + message);
    }
    
    showSuccess(message) {
        // Simple alert for now - in production, use a better notification system
        alert('Success: ' + message);
    }
    
    async deleteArchive(archiveName) {
        if (!confirm(`Are you sure you want to delete the archive "${archiveName}"? This action cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.baseURL}/api/archive/${encodeURIComponent(archiveName)}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showSuccess(`Archive "${archiveName}" deleted successfully`);
                this.loadArchives(); // Refresh the list
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete archive');
            }
        } catch (error) {
            console.error('Error deleting archive:', error);
            this.showError('Failed to delete archive: ' + error.message);
        }
    }
    
    showNodeDetails(node) {
        const nodeDetailsContainer = document.getElementById('node-details');
        if (!nodeDetailsContainer) return;
        
        const truncateText = (text, maxLength = 200) => {
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        };
        
        const html = `
            <div class="node-detail-item">
                <span class="node-detail-label">ID:</span>
                <span class="node-detail-value">${node.id.substring(0, 8)}...</span>
            </div>
            <div class="node-detail-item">
                <span class="node-detail-label">Score:</span>
                <span class="node-detail-value">${node.score.toFixed(3)}</span>
            </div>
            <div class="node-detail-item">
                <span class="node-detail-label">Cumulative Score:</span>
                <span class="node-detail-value">${node.cumulative_score.toFixed(3)}</span>
            </div>
            <div class="node-detail-item">
                <span class="node-detail-label">Depth:</span>
                <span class="node-detail-value">${node.depth}</span>
            </div>
            <div class="node-detail-item">
                <span class="node-detail-label">Status:</span>
                <span class="node-detail-value">${node.is_pruned ? 'Pruned' : 'Active'}</span>
            </div>
            <div class="node-detail-item">
                <span class="node-detail-label">Content:</span>
                <div class="node-detail-value" style="white-space: pre-wrap; font-family: monospace; max-height: 200px; overflow-y: auto;">${truncateText(node.text)}</div>
            </div>
        `;
        
        nodeDetailsContainer.innerHTML = html;
    }
}

// Add some CSS for the analysis display
const analysisCSS = `
.analysis-summary {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e0e0e0;
}

.analysis-stats, .trajectory-stats {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 10px;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
}

.stat-label {
    font-weight: 600;
    color: #666;
}

.stat-value {
    font-weight: bold;
    color: #333;
}

.final-insight {
    margin: 15px 0;
    padding: 12px;
    background: #f0f8ff;
    border-radius: 6px;
    border-left: 4px solid #667eea;
}

.reasoning-path {
    margin-top: 15px;
}

.path-step {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 8px;
    padding: 8px;
    background: #f9f9f9;
    border-radius: 4px;
    font-size: 0.9rem;
}

.step-number {
    font-weight: bold;
    color: #667eea;
    min-width: 20px;
}

.step-text {
    flex: 1;
}

.step-score {
    font-weight: bold;
    color: #4CAF50;
    min-width: 50px;
    text-align: right;
}
`;

// Add the CSS to the page
const style = document.createElement('style');
style.textContent = analysisCSS;
document.head.appendChild(style);

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    window.app = new GOTAIApp();
    
    // Function to try initializing the graph visualizer
    function initGraphVisualizer() {
        const container = document.getElementById('graph-container');
        let svgElement = document.getElementById('graph-svg');
        
        console.log('Graph container:', container);
        console.log('SVG element:', svgElement);
        
        if (container && !svgElement) {
            console.log('Container found but no SVG, creating one...');
            container.innerHTML = '<svg id="graph-svg" width="800" height="600"></svg>';
            svgElement = document.getElementById('graph-svg');
        }
        
        if (svgElement) {
            try {
                window.graphVisualizer = new GraphVisualizer('graph-svg');
                console.log('GraphVisualizer created successfully:', window.graphVisualizer);
                return true;
            } catch (error) {
                console.error('Error creating GraphVisualizer:', error);
                return false;
            }
        } else {
            console.error('Could not find or create SVG element');
            return false;
        }
    }
    
    // Try multiple times with increasing delays
    setTimeout(() => {
        if (!initGraphVisualizer()) {
            setTimeout(() => {
                if (!initGraphVisualizer()) {
                    setTimeout(() => {
                        initGraphVisualizer();
                    }, 1000);
                }
            }, 500);
        }
    }, 100);
    
    // Set up global functions for node interaction
    window.showNodeDetails = function(node) {
        if (window.app) {
            window.app.showNodeDetails(node);
        }
    };
    
    console.log('App initialization complete');
});
