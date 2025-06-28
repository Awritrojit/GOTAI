# This is the most complex part. It runs the main loop in a background thread.
import time
import threading
import logging
from .agent import agent
from ..db.vector_store import vector_store_client
from ..db.data_models import Node

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.is_running = False
        self.current_thread = None
        self.max_depth = 3  # Limit exploration depth
        self.max_nodes = 50  # Limit total nodes

    def start_analysis(self, hypothesis: str, max_depth: int = 3, max_nodes: int = 50):
        """Start the GOT-AI analysis process"""
        if self.is_running:
            logger.warning("Analysis already running")
            return
            
        # Update limits for this run
        self.max_depth = max_depth
        self.max_nodes = max_nodes
        
        logger.info(f"Starting analysis for hypothesis: {hypothesis}")
        logger.info(f"Max depth: {max_depth}, Max nodes: {max_nodes}")
        
        # Clear previous data from ChromaDB
        vector_store_client.clear_collection()
        
        # Create the root node
        root_node = Node(
            text=hypothesis, 
            trajectory_id="root", 
            cumulative_score=0.5,
            score=0.5,
            depth=0
        )
        vector_store_client.add_node(root_node)
        
        # Start the analysis in a background thread
        self.is_running = True
        self.current_thread = threading.Thread(target=self._run_analysis_loop)
        self.current_thread.daemon = True
        self.current_thread.start()
        
        logger.info("Analysis started in background thread")

    def stop_analysis(self):
        """Stop the analysis process"""
        self.is_running = False
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=5)
        logger.info("Analysis stopped")

    def _run_analysis_loop(self):
        """Main analysis loop - runs in background thread"""
        cycle_count = 0
        
        while self.is_running:
            try:
                cycle_count += 1
                logger.info(f"Starting analysis cycle {cycle_count}")
                
                if not self._run_cycle():
                    logger.info("No more nodes to explore - analysis complete")
                    break
                    
                # Check limits
                all_nodes = vector_store_client.get_all_nodes_for_graph()
                if len(all_nodes) >= self.max_nodes:
                    logger.info(f"Reached maximum node limit ({self.max_nodes}) - stopping analysis")
                    break
                
                # Pause between cycles
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error in analysis cycle: {e}")
                break
        
        self.is_running = False
        logger.info(f"Analysis completed after {cycle_count} cycles")

    def _run_cycle(self) -> bool:
        """Run a single analysis cycle. Returns False if no more work to do."""
        try:
            # Get all nodes from DB to find the best one to expand
            all_nodes = vector_store_client.get_all_nodes_for_graph()
            
            # Filter for open nodes (not fully explored, not pruned, within depth limit)
            open_nodes = [
                n for n in all_nodes 
                if not n.is_fully_explored 
                and not n.is_pruned 
                and n.depth < self.max_depth
            ]

            if not open_nodes:
                return False

            # Select node with the highest score to explore next (greedy search)
            node_to_explore = max(open_nodes, key=lambda n: n.cumulative_score)
            logger.info(f"Exploring node: {node_to_explore.id} (score: {node_to_explore.score:.2f})")

            # Use an agent to generate new child nodes
            new_nodes = agent.investigate(node_to_explore)

            # Save new nodes to the database
            for node in new_nodes:
                vector_store_client.add_node(node)

            # Mark the parent node as explored
            node_to_explore.is_fully_explored = True
            vector_store_client.add_node(node_to_explore)  # Update in DB

            # Simple pruning: prune trajectories with very low scores
            self._prune_low_scoring_nodes(all_nodes + new_nodes)

            logger.info(f"Cycle complete: generated {len(new_nodes)} new nodes")
            return True
            
        except Exception as e:
            logger.error(f"Error in analysis cycle: {e}")
            return False

    def _prune_low_scoring_nodes(self, all_nodes):
        """Prune nodes with consistently low scores"""
        try:
            # Calculate average score
            scores = [n.score for n in all_nodes if n.score > 0]
            if not scores:
                return
                
            avg_score = sum(scores) / len(scores)
            threshold = avg_score * 0.5  # Prune nodes scoring less than 50% of average
            
            pruned_count = 0
            for node in all_nodes:
                if not node.is_pruned and node.score < threshold and node.depth > 0:
                    node.is_pruned = True
                    vector_store_client.add_node(node)  # Update in DB
                    pruned_count += 1
            
            if pruned_count > 0:
                logger.info(f"Pruned {pruned_count} low-scoring nodes (threshold: {threshold:.2f})")
                
        except Exception as e:
            logger.error(f"Error pruning nodes: {e}")

# Global instance
orchestrator = Orchestrator()
