from ..llm.llm_interface import llm_client
from .. import config
from .scoring import scorer
from ..db.data_models import Node
from typing import List
import logging

logger = logging.getLogger(__name__)

class Agent:
    def investigate(self, source_node: Node) -> List[Node]:
        """Generate new nodes by investigating the source node with the interrogative battery"""
        new_nodes = []
        
        logger.info(f"Agent investigating node: {source_node.id}")
        
        for question in config.INTERROGATIVE_BATTERY:
            try:
                prompt = config.AGENT_PROMPT_TEMPLATE.format(
                    question=question, 
                    statement_text=source_node.text
                )
                new_text = llm_client.generate(prompt)

                if "Error:" not in new_text and len(new_text.strip()) > 0:
                    # Create new node
                    new_node = Node(
                        parent_id=source_node.id,
                        trajectory_id=source_node.trajectory_id,
                        text=new_text.strip(),
                        depth=source_node.depth + 1
                    )
                    
                    # Score the new node
                    new_node.score = scorer.calculate_final_score(new_text)
                    new_node.cumulative_score = source_node.cumulative_score + new_node.score
                    
                    new_nodes.append(new_node)
                    logger.info(f"Generated new node with score: {new_node.score:.2f}")
                
            except Exception as e:
                logger.error(f"Error generating response for question '{question}': {e}")
                continue
        
        logger.info(f"Generated {len(new_nodes)} new nodes from source node")
        return new_nodes

# Global instance
agent = Agent()
