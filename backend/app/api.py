from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .core.orchestrator import orchestrator
from .core.archive_manager import archive_manager
from .db.vector_store import vector_store_client
from .db.data_models import Node, GraphData, StartRequest, StopRequest, ArchiveResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GOT-AI Backend", description="Backend for the GOT-AI reasoning framework")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    else:
        return {"message": "GOT-AI Backend is running. Frontend not found."}

@app.get("/archive")
async def serve_archive_viewer():
    """Serve the archive viewer page"""
    archive_viewer_file = os.path.join(frontend_path, "archive_viewer.html")
    if os.path.exists(archive_viewer_file):
        return FileResponse(archive_viewer_file)
    else:
        raise HTTPException(status_code=404, detail="Archive viewer not found")

@app.get("/debug")
async def serve_debug_page():
    """Serve the debug page"""
    debug_file = os.path.join(frontend_path, "debug_archive.html")
    if os.path.exists(debug_file):
        return FileResponse(debug_file)
    else:
        raise HTTPException(status_code=404, detail="Debug page not found")

@app.post("/api/start")
async def start_process(request: StartRequest, background_tasks: BackgroundTasks):
    """Start the GOT-AI analysis process"""
    try:
        logger.info(f"Starting analysis for hypothesis: {request.hypothesis}")
        logger.info(f"Max depth: {request.max_depth}, Max nodes: {request.max_nodes}")
        background_tasks.add_task(orchestrator.start_analysis, request.hypothesis, request.max_depth, request.max_nodes)
        return {
            "message": "GOT-AI analysis started.", 
            "hypothesis": request.hypothesis,
            "max_depth": request.max_depth,
            "max_nodes": request.max_nodes
        }
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_process(request: StopRequest):
    """Stop the GOT-AI analysis process and archive the results"""
    try:
        # Stop the analysis
        orchestrator.stop_analysis()
        
        # Archive the current run if we have data
        nodes = vector_store_client.get_all_nodes_for_graph()
        if nodes and request.run_name.strip():
            # Get the current hypothesis from the root node
            root_nodes = [n for n in nodes if n.parent_id is None]
            hypothesis = root_nodes[0].text if root_nodes else "Unknown hypothesis"
            
            # Generate analysis for archiving
            analysis_data = None
            try:
                # Get the analysis data for the best trajectory
                best_node = max(nodes, key=lambda n: n.cumulative_score)
                path = []
                current = best_node
                while current:
                    path.insert(0, current)
                    if current.parent_id:
                        current = vector_store_client.get_node_by_id(current.parent_id)
                    else:
                        break
                
                total_nodes = len(nodes)
                avg_score = sum(n.score for n in nodes) / total_nodes if total_nodes > 0 else 0
                pruned_nodes = sum(1 for n in nodes if n.is_pruned)
                
                analysis_data = {
                    "total_nodes": total_nodes,
                    "average_score": avg_score,
                    "pruned_nodes": pruned_nodes,
                    "best_trajectory": {
                        "cumulative_score": best_node.cumulative_score,
                        "path_length": len(path),
                        "final_insight": best_node.text,
                        "path": [{"id": n.id, "text": n.text, "score": n.score} for n in path]
                    }
                }
            except Exception as e:
                logger.warning(f"Could not generate analysis data: {e}")
            
            # Archive the run with analysis data
            archive_result = archive_manager.archive_current_run(request.run_name, hypothesis, analysis_data)
            
            if archive_result["success"]:
                # Clear current data for fresh start
                archive_manager.clear_current_run()
                
                return {
                    "message": f"Analysis stopped and archived as '{request.run_name}'",
                    "archive_name": archive_result["archive_name"],
                    "nodes_archived": archive_result["nodes_count"],
                    "analysis_generated": analysis_data is not None
                }
            else:
                return {
                    "message": "Analysis stopped but archiving failed",
                    "error": archive_result.get("error", "Unknown error")
                }
        else:
            # Just stop without archiving if no data or no name
            archive_manager.clear_current_run()
            return {"message": "Analysis stopped. No data to archive or no run name provided."}
            
    except Exception as e:
        logger.error(f"Error stopping and archiving analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get the current status of the analysis"""
    return {
        "is_running": orchestrator.is_running,
        "total_nodes": len(vector_store_client.get_all_nodes_for_graph())
    }

@app.get("/api/graph_data", response_model=GraphData)
async def get_graph_data():
    """Get the current graph data for visualization"""
    try:
        nodes = vector_store_client.get_all_nodes_for_graph()
        
        # Create links between parent and child nodes
        links = []
        for node in nodes:
            if node.parent_id:
                links.append({
                    "source": node.parent_id,
                    "target": node.id,
                    "value": node.score  # Use score for link strength
                })
        
        return GraphData(nodes=nodes, links=links)
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/node/{node_id}", response_model=Node)
async def get_node_details(node_id: str):
    """Get detailed information about a specific node"""
    try:
        node = vector_store_client.get_node_by_id(node_id)
        if node:
            return node
        else:
            raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        logger.error(f"Error getting node details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis")
async def get_analysis():
    """Get analysis results - highest scoring paths, insights, etc."""
    try:
        nodes = vector_store_client.get_all_nodes_for_graph()
        
        if not nodes:
            return {"message": "No analysis data available"}
        
        # Find the highest scoring trajectory
        best_node = max(nodes, key=lambda n: n.cumulative_score)
        
        # Get path to best node
        path = []
        current = best_node
        while current:
            path.insert(0, current)
            if current.parent_id:
                current = vector_store_client.get_node_by_id(current.parent_id)
            else:
                break
        
        # Calculate statistics
        total_nodes = len(nodes)
        avg_score = sum(n.score for n in nodes) / total_nodes if total_nodes > 0 else 0
        pruned_nodes = sum(1 for n in nodes if n.is_pruned)
        
        return {
            "total_nodes": total_nodes,
            "average_score": avg_score,
            "pruned_nodes": pruned_nodes,
            "best_trajectory": {
                "cumulative_score": best_node.cumulative_score,
                "path_length": len(path),
                "final_insight": best_node.text,
                "path": [{"id": n.id, "text": n.text, "score": n.score} for n in path]
            }
        }
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/archive/{archive_name}/analysis")
async def get_archive_analysis(archive_name: str):
    """Get analysis data for a specific archived run"""
    try:
        analysis_data = archive_manager.load_archive_analysis(archive_name)
        if analysis_data:
            return analysis_data
        else:
            raise HTTPException(status_code=404, detail="Archive analysis not found")
    except Exception as e:
        logger.error(f"Error getting archive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_data():
    """Clear all current data for a fresh start"""
    try:
        success = archive_manager.clear_current_run()
        if success:
            return {"message": "All data cleared successfully. Ready for new analysis."}
        else:
            return {"message": "Failed to clear data completely."}
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/archives")
async def list_archives():
    """List all archived runs"""
    try:
        archives = archive_manager.list_archived_runs()
        return {"archives": archives}
    except Exception as e:
        logger.error(f"Error listing archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/archive/{archive_name}")
async def load_archive(archive_name: str):
    """Load a specific archived run for viewing"""
    try:
        archive_data = archive_manager.load_archived_run(archive_name)
        if archive_data["success"]:
            return archive_data
        else:
            raise HTTPException(status_code=404, detail=archive_data["error"])
    except Exception as e:
        logger.error(f"Error loading archive {archive_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/archive/{archive_name}")
async def delete_archive(archive_name: str):
    """Delete an archived run"""
    try:
        logger.info(f"Deleting archive: {archive_name}")
        result = archive_manager.delete_archive(archive_name)
        if result["success"]:
            return {"message": f"Archive '{archive_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Archive not found"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
