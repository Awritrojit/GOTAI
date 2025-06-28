# GOTAI: Graph of Thoughts Autonomous Reasoning Framework

**Build an autonomous AI reasoning system that explores branching trajectories of thought**

## Overview

**Explore** scientific hypotheses through intelligent graph-based reasoning. **Create** dynamic knowledge graphs that branch, score, and prune ideas autonomously. **Archive** complete reasoning sessions for analysis and review.

## Features

- **Start** reasoning analysis with custom hypotheses
- **Configure** exploration depth and node limits
- **Watch** real-time graph visualization as thoughts develop
- **Interact** with nodes to see detailed reasoning paths
- **Archive** complete runs with metadata and timestamps
- **View** archived sessions in dedicated browser tabs
- **Delete** unwanted archives directly from the interface
- **Access** comprehensive analysis summaries

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start the System
```bash
cd backend
python main.py
```

### Access the Interface
**Open** your browser and navigate to `http://localhost:8000`

## Usage

### Run Analysis
1. **Enter** a hypothesis in the text area
2. **Set** max depth and max nodes (optional)
3. **Click** "Start Analysis" to begin reasoning
4. **Watch** the graph build in real-time
5. **Click** nodes to examine reasoning details
6. **Stop** and archive when satisfied

### Manage Archives
- **View** all archived runs at the bottom of the main page
- **Click** any archive to open it in a new browser tab
- **Delete** archives using the trash button
- **Refresh** the archive list with the refresh button

## Architecture

**Understand** the system components:

- **Frontend**: Interactive web interface with D3.js visualization
- **Backend**: FastAPI server with real-time processing
- **Vector Store**: ChromaDB for semantic node storage
- **Archive System**: File-based persistent storage
- **LLM Integration**: Local Qwen3 0.6B model via Ollama

## Development

### Test the System
```bash
cd tests
python test_complete_archive_system.py
```

### Debug Issues
**Check** the `/tests` directory for debugging tools and test scripts.

## Configuration

**Modify** settings in `backend/app/config.py`:
- LLM model selection
- Vector database paths
- Archive locations
- Reasoning prompts

---

**Start exploring** autonomous reasoning with GOT-AI!
