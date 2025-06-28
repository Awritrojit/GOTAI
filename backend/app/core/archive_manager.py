import os
import json
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..db.vector_store import vector_store_client
from ..db.data_models import Node
from .. import config
import logging

logger = logging.getLogger(__name__)

class ArchiveManager:
    def __init__(self):
        self.archive_base_path = config.ARCHIVE_BASE_PATH
        self._ensure_archive_directory()
    
    def _ensure_archive_directory(self):
        """Ensure the archive directory exists"""
        if not os.path.exists(self.archive_base_path):
            os.makedirs(self.archive_base_path)
            logger.info(f"Created archive directory: {self.archive_base_path}")
    
    def _sanitize_run_name(self, run_name: str) -> str:
        """Sanitize run name for use as filename"""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = run_name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length and remove extra spaces
        sanitized = sanitized.strip()[:50]
        
        # Add timestamp if name is empty
        if not sanitized:
            sanitized = "unnamed_run"
            
        return sanitized
    
    def archive_current_run(self, run_name: str, hypothesis: str, analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Archive the current run data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_name = self._sanitize_run_name(run_name)
            archive_name = f"{timestamp}_{sanitized_name}"
            archive_path = os.path.join(self.archive_base_path, archive_name)
            
            # Create archive directory
            os.makedirs(archive_path)
            
            # Get all current nodes
            nodes = vector_store_client.get_all_nodes_for_graph()
            
            # Use provided analysis data or generate it
            if analysis_data is None:
                analysis_data = self._generate_analysis_data(nodes, hypothesis)
            
            # Save data files
            self._save_nodes_data(nodes, archive_path)
            self._save_analysis_data(analysis_data, archive_path)
            self._save_metadata(run_name, hypothesis, timestamp, archive_path)
            
            # Copy database files if they exist
            self._archive_database_files(archive_path)
            
            logger.info(f"Successfully archived run '{run_name}' to {archive_path}")
            
            return {
                "success": True,
                "archive_path": archive_path,
                "archive_name": archive_name,
                "nodes_count": len(nodes),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error archiving run: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_nodes_data(self, nodes: List[Node], archive_path: str):
        """Save nodes data as JSON"""
        nodes_data = []
        for node in nodes:
            node_dict = node.dict()
            # Convert any non-serializable data
            if 'embedding' in node_dict and node_dict['embedding']:
                node_dict['embedding_length'] = len(node_dict['embedding'])
                del node_dict['embedding']  # Remove large embedding data
            nodes_data.append(node_dict)
        
        nodes_file = os.path.join(archive_path, "nodes.json")
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(nodes_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(nodes_data)} nodes to {nodes_file}")
    
    def _save_analysis_data(self, analysis_data: Dict[str, Any], archive_path: str):
        """Save analysis results"""
        analysis_file = os.path.join(archive_path, "analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analysis data to {analysis_file}")
    
    def _save_metadata(self, run_name: str, hypothesis: str, timestamp: str, archive_path: str):
        """Save run metadata"""
        metadata = {
            "run_name": run_name,
            "hypothesis": hypothesis,
            "timestamp": timestamp,
            "archived_at": datetime.now().isoformat(),
            "archive_format_version": "1.0"
        }
        
        metadata_file = os.path.join(archive_path, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to {metadata_file}")
    
    def _archive_database_files(self, archive_path: str):
        """Copy database files to archive"""
        db_path = config.VECTOR_DB_PATH
        if os.path.exists(db_path):
            archive_db_path = os.path.join(archive_path, "database")
            try:
                shutil.copytree(db_path, archive_db_path)
                logger.info(f"Archived database files to {archive_db_path}")
            except Exception as e:
                logger.warning(f"Could not archive database files: {e}")
    
    def _generate_analysis_data(self, nodes: List[Node], hypothesis: str) -> Dict[str, Any]:
        """Generate comprehensive analysis data"""
        if not nodes:
            return {
                "message": "No analysis data available",
                "hypothesis": hypothesis,
                "total_nodes": 0
            }
        
        # Calculate statistics
        total_nodes = len(nodes)
        scores = [n.score for n in nodes if n.score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        pruned_nodes = sum(1 for n in nodes if n.is_pruned)
        explored_nodes = sum(1 for n in nodes if n.is_fully_explored)
        
        # Find best trajectory
        best_node = max(nodes, key=lambda n: n.cumulative_score)
        best_path = self._construct_path_to_node(best_node, nodes)
        
        # Find all trajectories and their endpoints
        trajectories = self._analyze_trajectories(nodes)
        
        # Calculate depth statistics
        depths = [n.depth for n in nodes]
        max_depth = max(depths) if depths else 0
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        return {
            "hypothesis": hypothesis,
            "total_nodes": total_nodes,
            "average_score": avg_score,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "pruned_nodes": pruned_nodes,
            "explored_nodes": explored_nodes,
            "max_depth": max_depth,
            "average_depth": avg_depth,
            "total_trajectories": len(trajectories),
            "best_trajectory": {
                "cumulative_score": best_node.cumulative_score,
                "path_length": len(best_path),
                "final_insight": best_node.text,
                "final_score": best_node.score,
                "path": [{"id": n.id, "text": n.text, "score": n.score, "depth": n.depth} for n in best_path]
            },
            "trajectory_analysis": trajectories,
            "score_distribution": self._calculate_score_distribution(scores)
        }
    
    def _construct_path_to_node(self, target_node: Node, all_nodes: List[Node]) -> List[Node]:
        """Construct the path from root to a specific node"""
        path = []
        current = target_node
        node_dict = {n.id: n for n in all_nodes}
        
        while current:
            path.insert(0, current)
            if current.parent_id and current.parent_id in node_dict:
                current = node_dict[current.parent_id]
            else:
                break
        
        return path
    
    def _analyze_trajectories(self, nodes: List[Node]) -> List[Dict[str, Any]]:
        """Analyze all trajectories in the graph"""
        # Find leaf nodes (nodes with no children)
        node_dict = {n.id: n for n in nodes}
        children_count = {}
        
        for node in nodes:
            if node.parent_id:
                children_count[node.parent_id] = children_count.get(node.parent_id, 0) + 1
        
        leaf_nodes = [n for n in nodes if n.id not in children_count]
        
        trajectories = []
        for leaf in leaf_nodes:
            path = self._construct_path_to_node(leaf, nodes)
            trajectories.append({
                "endpoint_id": leaf.id,
                "cumulative_score": leaf.cumulative_score,
                "final_score": leaf.score,
                "length": len(path),
                "is_pruned": leaf.is_pruned,
                "final_insight": leaf.text,
                "path_scores": [n.score for n in path]
            })
        
        # Sort by cumulative score
        trajectories.sort(key=lambda t: t["cumulative_score"], reverse=True)
        return trajectories
    
    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate score distribution statistics"""
        if not scores:
            return {"high": 0, "medium": 0, "low": 0}
        
        high_scores = sum(1 for s in scores if s >= 0.7)
        medium_scores = sum(1 for s in scores if 0.4 <= s < 0.7)
        low_scores = sum(1 for s in scores if s < 0.4)
        
        return {
            "high": high_scores,
            "medium": medium_scores,
            "low": low_scores,
            "high_percentage": (high_scores / len(scores)) * 100,
            "medium_percentage": (medium_scores / len(scores)) * 100,
            "low_percentage": (low_scores / len(scores)) * 100
        }
    
    def clear_current_run(self):
        """Clear all current run data for a fresh start"""
        try:
            # Clear the vector database using ChromaDB's proper method
            vector_store_client.clear_collection()
            logger.info("Successfully cleared vector database collection")
            
            logger.info("Successfully cleared current run data")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing current run data: {e}")
            return False
    
    def list_archived_runs(self) -> List[Dict[str, Any]]:
        """List all archived runs"""
        try:
            archived_runs = []
            if not os.path.exists(self.archive_base_path):
                return archived_runs
            
            for item in os.listdir(self.archive_base_path):
                item_path = os.path.join(self.archive_base_path, item)
                if os.path.isdir(item_path):
                    metadata_file = os.path.join(item_path, "metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            # Add file size info
                            total_size = sum(
                                os.path.getsize(os.path.join(dirpath, filename))
                                for dirpath, dirnames, filenames in os.walk(item_path)
                                for filename in filenames
                            )
                            
                            archived_runs.append({
                                "archive_name": item,
                                "run_name": metadata.get("run_name", "Unknown"),
                                "hypothesis": metadata.get("hypothesis", "No hypothesis"),
                                "timestamp": metadata.get("timestamp", "Unknown"),
                                "archived_at": metadata.get("archived_at", "Unknown"),
                                "size_bytes": total_size,
                                "path": item_path
                            })
                        except Exception as e:
                            logger.warning(f"Could not read metadata for {item}: {e}")
            
            # Sort by timestamp (newest first)
            archived_runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return archived_runs
            
        except Exception as e:
            logger.error(f"Error listing archived runs: {e}")
            return []
    
    def load_archived_run(self, archive_name: str) -> Dict[str, Any]:
        """Load an archived run for viewing"""
        try:
            archive_path = os.path.join(self.archive_base_path, archive_name)
            
            if not os.path.exists(archive_path) or not os.path.isdir(archive_path):
                return {"success": False, "error": "Archive not found"}
            
            # Load metadata
            metadata_file = os.path.join(archive_path, "metadata.json")
            if not os.path.exists(metadata_file):
                return {"success": False, "error": "Archive metadata not found"}
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load nodes data
            nodes_file = os.path.join(archive_path, "nodes.json")
            nodes = []
            if os.path.exists(nodes_file):
                with open(nodes_file, 'r', encoding='utf-8') as f:
                    nodes_data = json.load(f)
                    # Handle both list and dict formats
                    if isinstance(nodes_data, list):
                        nodes = nodes_data
                    elif isinstance(nodes_data, dict):
                        nodes = nodes_data.get('nodes', [])
                    else:
                        nodes = []
            
            # Load graph data
            graph_file = os.path.join(archive_path, "graph_data.json")
            graph_data = {"nodes": [], "links": []}
            if os.path.exists(graph_file):
                with open(graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
            
            # If graph data is empty but we have nodes, generate graph data
            if (not graph_data.get('nodes') or len(graph_data.get('nodes', [])) == 0) and nodes:
                graph_data = self._generate_graph_data_from_nodes(nodes)
            
            # Load analysis summary
            summary_file = os.path.join(archive_path, "analysis_summary.json")
            summary = {}
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
            
            return {
                "success": True,
                "metadata": metadata,
                "nodes": nodes,
                "graph_data": graph_data,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error loading archived run {archive_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def load_archive_analysis(self, archive_name: str) -> Optional[Dict[str, Any]]:
        """Load analysis data for a specific archived run"""
        try:
            archive_path = os.path.join(self.archive_base_path, archive_name)
            
            if not os.path.exists(archive_path) or not os.path.isdir(archive_path):
                return None
            
            # Load analysis summary
            analysis_file = os.path.join(archive_path, "analysis.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading archive analysis {archive_name}: {e}")
            return None
    
    def _generate_graph_data_from_nodes(self, nodes):
        """Generate graph visualization data from node list"""
        try:
            graph_nodes = []
            links = []
            
            for node in nodes:
                # Create graph node
                graph_node = {
                    "id": node.get('id'),
                    "text": node.get('text', '')[:100] + ('...' if len(node.get('text', '')) > 100 else ''),
                    "score": node.get('score', 0.0),
                    "is_pruned": node.get('is_pruned', False),
                    "x": None,  # Let D3 position
                    "y": None
                }
                graph_nodes.append(graph_node)
                
                # Create link if node has parent
                if node.get('parent_id'):
                    link = {
                        "source": node.get('parent_id'),
                        "target": node.get('id')
                    }
                    links.append(link)
            
            return {
                "nodes": graph_nodes,
                "links": links
            }
            
        except Exception as e:
            logger.error(f"Error generating graph data from nodes: {e}")
            return {"nodes": [], "links": []}
    
    def delete_archive(self, archive_name: str) -> Dict[str, Any]:
        """Delete an archived run"""
        try:
            archive_path = os.path.join(self.archive_base_path, archive_name)
            
            if not os.path.exists(archive_path):
                return {
                    "success": False,
                    "error": f"Archive '{archive_name}' not found"
                }
            
            # Remove the archive directory and all its contents
            shutil.rmtree(archive_path)
            
            logger.info(f"Archive '{archive_name}' deleted successfully")
            return {
                "success": True,
                "message": f"Archive '{archive_name}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting archive '{archive_name}': {e}")
            return {
                "success": False,
                "error": f"Failed to delete archive: {str(e)}"
            }

# Global instance
archive_manager = ArchiveManager()
